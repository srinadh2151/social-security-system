"""
Workflow Orchestrator for Document Processing and Assessment

This orchestrator manages the complete workflow from document upload
to final assessment for financial support applications.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import asyncio

try:
    from req_agents.document_processor import DocumentProcessingAgent, DocumentType
    from req_agents.assessment_agent import AssessmentAgent, EligibilityStatus
    from req_agents.llm_interface import LangChainLLMInterface
    from req_agents.base_agent import LangChainBaseAgent
except ImportError:
    from document_processor import DocumentProcessingAgent, DocumentType
    from assessment_agent import AssessmentAgent, EligibilityStatus
    from llm_interface import LangChainLLMInterface
    from base_agent import LangChainBaseAgent

logger = logging.getLogger(__name__)


class WorkflowStatus:
    """Workflow status tracking."""
    INITIATED = "initiated"
    PROCESSING_DOCUMENTS = "processing_documents"
    DOCUMENTS_PROCESSED = "documents_processed"
    RUNNING_ASSESSMENT = "running_assessment"
    ASSESSMENT_COMPLETE = "assessment_complete"
    COMPLETED = "completed"
    FAILED = "failed"


class ApplicationWorkflowOrchestrator(LangChainBaseAgent):
    """Orchestrator for the complete application assessment workflow."""
    
    def __init__(
        self,
        llm_interface: Optional[LangChainLLMInterface] = None,
        model: str = "gpt-4o",
        output_dir: str = "./workflow_outputs"
    ):
        """Initialize workflow orchestrator."""
        super().__init__(
            name="workflow_orchestrator",
            llm_interface=llm_interface,
            model=model,
            system_prompt=self._get_system_prompt()
        )
        
        # Initialize sub-agents
        self.document_processor = DocumentProcessingAgent(
            llm_interface=self.llm,
            model=model
        )
        
        self.assessment_agent = AssessmentAgent(
            llm_interface=self.llm,
            model=model
        )
        
        # Setup output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Workflow state
        self.current_workflow = None
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for workflow orchestration."""
        return """
You are a workflow orchestrator for financial support application processing.
Your role is to coordinate document processing and assessment activities.

Key responsibilities:
1. Validate uploaded documents and their purposes
2. Coordinate multimodal document processing
3. Ensure data quality and completeness
4. Orchestrate the assessment process
5. Generate comprehensive reports
6. Handle errors and edge cases gracefully

Always maintain audit trails and ensure data privacy throughout the process.
"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete workflow."""
        try:
            workflow_id = task.get("workflow_id", f"WF-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
            documents = task.get("documents", [])
            applicant_info = task.get("applicant_info", {})
            
            logger.info(f"Starting workflow {workflow_id} with {len(documents)} documents")
            
            # Initialize workflow
            workflow_result = await self.process_application_workflow(
                workflow_id=workflow_id,
                documents=documents,
                applicant_info=applicant_info
            )
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "status": WorkflowStatus.FAILED,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def process_application_workflow(
        self,
        workflow_id: str,
        documents: List[Dict[str, Any]],
        applicant_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process complete application workflow."""
        
        workflow_state = {
            "workflow_id": workflow_id,
            "status": WorkflowStatus.INITIATED,
            "start_time": datetime.now().isoformat(),
            "documents": documents,
            "applicant_info": applicant_info or {},
            "processed_documents": [],
            "assessment_result": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Step 1: Validate documents
            workflow_state["status"] = WorkflowStatus.PROCESSING_DOCUMENTS
            validation_result = await self._validate_documents(documents)
            
            if not validation_result["valid"]:
                workflow_state["errors"].extend(validation_result["errors"])
                workflow_state["status"] = WorkflowStatus.FAILED
                return workflow_state
            
            # Step 2: Process documents
            processed_documents = []
            for doc_info in documents:
                try:
                    result = await self.document_processor.execute({
                        "file_path": doc_info["file_path"],
                        "document_purpose": doc_info.get("purpose", "unknown")
                    })
                    
                    if result["status"] == "success":
                        processed_documents.append(result["extracted_data"])
                    else:
                        workflow_state["errors"].append(f"Failed to process {doc_info['file_path']}: {result.get('message', 'Unknown error')}")
                        
                except Exception as e:
                    workflow_state["errors"].append(f"Document processing error for {doc_info['file_path']}: {str(e)}")
            
            workflow_state["processed_documents"] = processed_documents
            workflow_state["status"] = WorkflowStatus.DOCUMENTS_PROCESSED
            
            # Step 3: Convert to assessment format
            if processed_documents:
                assessment_data = await self.document_processor.convert_to_assessment_format(processed_documents)
                
                # Merge with any provided applicant info
                if applicant_info:
                    assessment_data["applicant_info"].update(applicant_info)
                
                # Step 4: Run assessment
                workflow_state["status"] = WorkflowStatus.RUNNING_ASSESSMENT
                assessment_result = await self.assessment_agent.assess_application(assessment_data)
                
                workflow_state["assessment_result"] = assessment_result
                workflow_state["status"] = WorkflowStatus.ASSESSMENT_COMPLETE
                
                # Step 5: Generate comprehensive report
                comprehensive_report = await self._generate_comprehensive_report(
                    workflow_state, assessment_data, assessment_result
                )
                
                workflow_state["comprehensive_report"] = comprehensive_report
                workflow_state["status"] = WorkflowStatus.COMPLETED
                
                # Save workflow results
                await self._save_workflow_results(workflow_id, workflow_state)
                
            else:
                workflow_state["errors"].append("No documents were successfully processed")
                workflow_state["status"] = WorkflowStatus.FAILED
            
            workflow_state["end_time"] = datetime.now().isoformat()
            workflow_state["duration"] = self._calculate_duration(
                workflow_state["start_time"], 
                workflow_state["end_time"]
            )
            
            return workflow_state
            
        except Exception as e:
            logger.error(f"Workflow processing failed: {str(e)}")
            workflow_state["status"] = WorkflowStatus.FAILED
            workflow_state["errors"].append(str(e))
            workflow_state["end_time"] = datetime.now().isoformat()
            return workflow_state
    
    async def _validate_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate uploaded documents."""
        errors = []
        warnings = []
        
        # Check if we have required document types
        required_docs = {
            DocumentType.EMIRATES_ID.value: False,
            DocumentType.RESUME.value: False,
            DocumentType.ASSETS_LIABILITIES.value: False,
            DocumentType.CREDIT_REPORT.value: False
        }
        
        for doc in documents:
            file_path = doc.get("file_path", "")
            purpose = doc.get("purpose", "").lower()
            
            # Check if file exists
            if not file_path or not os.path.exists(file_path):
                errors.append(f"File not found: {file_path}")
                continue
            
            # Check file format
            file_ext = Path(file_path).suffix.lower()
            valid_extensions = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".png", ".jpg", ".jpeg", ".txt"}
            
            if file_ext not in valid_extensions:
                errors.append(f"Unsupported file format: {file_ext} for {file_path}")
                continue
            
            # Validate purpose-format combinations
            format_rules = {
                "emirates_id": [".pdf"],
                "resume": [".pdf", ".docx", ".doc"],
                "assets_liabilities": [".xlsx", ".xls"],
                "credit_report": [".pdf", ".txt"],
                "bank_statement": [".pdf", ".txt"]
            }
            
            if purpose in format_rules:
                if file_ext not in format_rules[purpose]:
                    errors.append(f"Invalid format {file_ext} for {purpose}. Expected: {format_rules[purpose]}")
                else:
                    required_docs[purpose] = True
            
            # Check file size (max 50MB)
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    errors.append(f"File too large: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
            except:
                errors.append(f"Cannot access file: {file_path}")
        
        # Check for missing critical documents
        missing_critical = []
        if not required_docs[DocumentType.EMIRATES_ID.value]:
            missing_critical.append("Emirates ID")
        if not required_docs[DocumentType.RESUME.value]:
            warnings.append("Resume/CV not provided - employment assessment may be limited")
        
        if missing_critical:
            errors.extend([f"Missing required document: {doc}" for doc in missing_critical])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "document_coverage": required_docs
        }
    
    async def _generate_comprehensive_report(
        self,
        workflow_state: Dict[str, Any],
        assessment_data: Dict[str, Any],
        assessment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive workflow report."""
        
        prompt = f"""
        Generate a comprehensive report for this financial support application workflow:
        
        Workflow Information:
        - Workflow ID: {workflow_state['workflow_id']}
        - Processing Duration: {workflow_state.get('duration', 'N/A')}
        - Documents Processed: {len(workflow_state['processed_documents'])}
        - Status: {workflow_state['status']}
        
        Assessment Result:
        {json.dumps(assessment_result, indent=2)}
        
        Document Processing Summary:
        {json.dumps([{
            'type': doc.get('document_type'),
            'confidence': doc.get('confidence_score', 0),
            'format': doc.get('file_format')
        } for doc in workflow_state['processed_documents']], indent=2)}
        
        Generate a comprehensive report including:
        {{
            "executive_summary": {{
                "applicant_name": "string",
                "application_id": "string",
                "final_decision": "approved/conditionally_approved/pending_review/rejected",
                "overall_score": "number",
                "priority_level": "high/medium/low",
                "key_findings": ["list of key findings"],
                "recommendation_summary": "string"
            }},
            "document_analysis": {{
                "documents_processed": "number",
                "data_quality_score": "number (0-1)",
                "missing_information": ["list of missing info"],
                "data_confidence": "high/medium/low",
                "processing_notes": ["any notable issues or observations"]
            }},
            "assessment_breakdown": {{
                "income_assessment": {{
                    "score": "number",
                    "key_factors": ["list"],
                    "concerns": ["list"]
                }},
                "employment_assessment": {{
                    "score": "number", 
                    "key_factors": ["list"],
                    "concerns": ["list"]
                }},
                "family_assessment": {{
                    "score": "number",
                    "key_factors": ["list"],
                    "concerns": ["list"]
                }},
                "wealth_assessment": {{
                    "score": "number",
                    "key_factors": ["list"],
                    "concerns": ["list"]
                }},
                "demographic_assessment": {{
                    "score": "number",
                    "key_factors": ["list"],
                    "concerns": ["list"]
                }}
            }},
            "recommendations": {{
                "support_types": ["list of recommended support types"],
                "support_amount": "estimated amount if applicable",
                "conditions": ["any conditions for approval"],
                "next_steps": ["required actions"],
                "review_timeline": "when to review again"
            }},
            "risk_assessment": {{
                "risk_level": "low/medium/high",
                "risk_factors": ["identified risk factors"],
                "mitigation_strategies": ["recommended mitigations"]
            }},
            "compliance_notes": {{
                "regulatory_compliance": "compliant/non-compliant/needs_review",
                "data_privacy": "compliant/needs_attention",
                "audit_trail": "complete/incomplete"
            }}
        }}
        
        Provide detailed, actionable insights for decision makers.
        """
        
        report = await self.generate_structured_response(
            prompt,
            schema={
                "type": "object",
                "properties": {
                    "executive_summary": {"type": "object"},
                    "document_analysis": {"type": "object"},
                    "assessment_breakdown": {"type": "object"},
                    "recommendations": {"type": "object"},
                    "risk_assessment": {"type": "object"},
                    "compliance_notes": {"type": "object"}
                }
            }
        )
        
        # Add metadata
        report["report_metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "workflow_id": workflow_state["workflow_id"],
            "processing_duration": workflow_state.get("duration", "N/A"),
            "ai_model": self.model,
            "report_version": "1.0"
        }
        
        return report
    
    async def _save_workflow_results(self, workflow_id: str, workflow_state: Dict[str, Any]):
        """Save workflow results to files."""
        try:
            # Create workflow-specific directory
            workflow_dir = self.output_dir / workflow_id
            workflow_dir.mkdir(exist_ok=True)
            
            # Save complete workflow state
            with open(workflow_dir / "workflow_state.json", "w") as f:
                json.dump(workflow_state, f, indent=2, default=str)
            
            # Save assessment result separately
            if workflow_state.get("assessment_result"):
                with open(workflow_dir / "assessment_result.json", "w") as f:
                    json.dump(workflow_state["assessment_result"], f, indent=2, default=str)
            
            # Save comprehensive report
            if workflow_state.get("comprehensive_report"):
                with open(workflow_dir / "comprehensive_report.json", "w") as f:
                    json.dump(workflow_state["comprehensive_report"], f, indent=2, default=str)
            
            # Generate summary report
            summary = {
                "workflow_id": workflow_id,
                "status": workflow_state["status"],
                "applicant_name": workflow_state.get("assessment_result", {}).get("applicant_name", "N/A"),
                "final_decision": workflow_state.get("assessment_result", {}).get("status", "N/A"),
                "overall_score": workflow_state.get("assessment_result", {}).get("overall_score", 0),
                "processing_time": workflow_state.get("duration", "N/A"),
                "documents_processed": len(workflow_state.get("processed_documents", [])),
                "errors": len(workflow_state.get("errors", [])),
                "warnings": len(workflow_state.get("warnings", []))
            }
            
            with open(workflow_dir / "summary.json", "w") as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Workflow results saved to {workflow_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save workflow results: {str(e)}")
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calculate duration between timestamps."""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            duration = end - start
            
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            return f"{minutes}m {seconds}s"
        except:
            return "N/A"
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a specific workflow."""
        workflow_dir = self.output_dir / workflow_id
        
        if not workflow_dir.exists():
            return {"error": "Workflow not found"}
        
        try:
            # Load summary
            summary_file = workflow_dir / "summary.json"
            if summary_file.exists():
                with open(summary_file, "r") as f:
                    return json.load(f)
            
            # Fallback to workflow state
            state_file = workflow_dir / "workflow_state.json"
            if state_file.exists():
                with open(state_file, "r") as f:
                    state = json.load(f)
                    return {
                        "workflow_id": workflow_id,
                        "status": state.get("status", "unknown"),
                        "start_time": state.get("start_time"),
                        "end_time": state.get("end_time")
                    }
            
            return {"error": "Workflow data not found"}
            
        except Exception as e:
            return {"error": f"Failed to load workflow status: {str(e)}"}
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows."""
        workflows = []
        
        try:
            for workflow_dir in self.output_dir.iterdir():
                if workflow_dir.is_dir():
                    summary_file = workflow_dir / "summary.json"
                    if summary_file.exists():
                        with open(summary_file, "r") as f:
                            workflows.append(json.load(f))
            
            # Sort by workflow ID (newest first)
            workflows.sort(key=lambda x: x.get("workflow_id", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {str(e)}")
        
        return workflows


# Test implementation
if __name__ == "__main__":
    import asyncio
    
    async def test_workflow_orchestrator():
        """Test the workflow orchestrator."""
        print("🧪 Testing Workflow Orchestrator...")
        
        # Create orchestrator
        orchestrator = ApplicationWorkflowOrchestrator(model="gpt-4o")
        
        # Sample workflow task
        test_task = {
            "workflow_id": "TEST-002",
            "documents": [
                {
                    "file_path": "/Users/srinadh.nidadana-c/Downloads/workflowautomation/sample_emirates_id.pdf",
                    "purpose": "emirates_id"
                },
                {
                    "file_path": "/Users/srinadh.nidadana-c/Downloads/workflowautomation/sample_resume.pdf",
                    "purpose": "resume"
                },
                {
                    "file_path": "/Users/srinadh.nidadana-c/Downloads/workflowautomation/sample_bank_statement.txt",
                    "purpose": "bank_statement"
                },
                {
                    "file_path": "/Users/srinadh.nidadana-c/Downloads/workflowautomation/sample_assets.xlsx",
                    "purpose": "assets_liabilities"
                },
                {
                    "file_path": "/Users/srinadh.nidadana-c/Downloads/workflowautomation/sample_credit_report.txt",
                    "purpose": "credit_report"
                }
            ],
            "applicant_info": {
                "name": "Srinadh Raja Nidadana",
                "email": "srinadh.673@gmail.com"
            }
        }
        
        try:
            print("🚀 Starting workflow...")
            result = await orchestrator.execute(test_task)
            
            print(f"✅ Workflow completed!")
            print(f"Status: {result.get('status')}")
            print(f"Duration: {result.get('duration', 'N/A')}")
            print(f"Documents Processed: {len(result.get('processed_documents', []))}")
            print(f"Errors: {len(result.get('errors', []))}")
            
            if result.get("assessment_result"):
                assessment = result["assessment_result"]
                print(f"\n📊 Assessment Results:")
                print(f"Final Decision: {assessment.get('status')}")
                print(f"Overall Score: {assessment.get('overall_score', 0):.2f}")
                print(f"Priority Level: {assessment.get('priority_level')}")
            
            if result.get("comprehensive_report"):
                report = result["comprehensive_report"]
                print(f"\n📋 Report Generated:")
                print(f"Executive Summary Available: {'executive_summary' in report}")
                print(f"Risk Assessment: {report.get('risk_assessment', {}).get('risk_level', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test workflow listing
        print(f"\n📂 Listing workflows...")
        workflows = await orchestrator.list_workflows()
        print(f"Found {len(workflows)} workflows")
        
        for wf in workflows[:3]:  # Show first 3
            print(f"  - {wf.get('workflow_id')}: {wf.get('status')} ({wf.get('processing_time', 'N/A')})")
    
    # Run test
    asyncio.run(test_workflow_orchestrator())