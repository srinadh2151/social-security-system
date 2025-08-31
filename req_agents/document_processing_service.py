"""
Document Processing Service

This service integrates document processing with the workflow orchestrator
to process uploaded documents and generate final assessments.
"""

import logging
import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid

try:
    from req_agents.document_processor import DocumentProcessingAgent
    from req_agents.workflow_orchestrator import ApplicationWorkflowOrchestrator
    from req_agents.llm_interface import LangChainLLMInterface
except ImportError:
    from document_processor import DocumentProcessingAgent
    from workflow_orchestrator import ApplicationWorkflowOrchestrator
    from llm_interface import LangChainLLMInterface

logger = logging.getLogger(__name__)


class DocumentProcessingService:
    """Service for processing uploaded documents and generating assessments."""
    
    def __init__(
        self,
        uploads_dir: str = "./backend/uploads",
        outputs_dir: str = "./workflow_outputs",
        model: str = "gpt-4o"
    ):
        """Initialize the document processing service."""
        self.uploads_dir = Path(uploads_dir)
        self.outputs_dir = Path(outputs_dir)
        self.model = model
        
        # Ensure directories exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize workflow orchestrator
        self.orchestrator = ApplicationWorkflowOrchestrator(
            model=model,
            output_dir=str(self.outputs_dir)
        )
        
        logger.info(f"Document Processing Service initialized")
        logger.info(f"Uploads directory: {self.uploads_dir}")
        logger.info(f"Outputs directory: {self.outputs_dir}")
    
    async def process_uploaded_documents(
        self,
        applicant_info: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process all documents in the uploads directory and generate assessment.
        
        Args:
            applicant_info: Optional applicant information
            workflow_id: Optional workflow ID, will generate one if not provided
            
        Returns:
            Complete workflow result with assessment and judgment
        """
        try:
            # Generate workflow ID if not provided
            if not workflow_id:
                workflow_id = f"WF-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
            
            logger.info(f"Starting document processing workflow: {workflow_id}")
            
            # Scan uploads directory for documents
            documents = await self._scan_uploaded_documents()
            
            if not documents:
                return {
                    "status": "error",
                    "message": "No documents found in uploads directory",
                    "workflow_id": workflow_id
                }
            
            logger.info(f"Found {len(documents)} documents to process")
            
            # Create workflow task
            workflow_task = {
                "workflow_id": workflow_id,
                "documents": documents,
                "applicant_info": applicant_info or {}
            }
            
            # Execute workflow
            result = await self.orchestrator.execute(workflow_task)
            
            # Generate final judgment summary
            if result.get("status") == "completed":
                judgment_summary = await self._generate_judgment_summary(result)
                result["judgment_summary"] = judgment_summary
                
                # Save judgment summary as separate file
                await self._save_judgment_summary(workflow_id, judgment_summary)
            
            logger.info(f"Workflow {workflow_id} completed with status: {result.get('status')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "workflow_id": workflow_id or "unknown"
            }
    
    async def _scan_uploaded_documents(self) -> List[Dict[str, Any]]:
        """Scan uploads directory and classify documents."""
        documents = []
        
        # Document type mapping based on filename patterns
        document_type_patterns = {
            "emirates_id": ["emirates", "id", "identity"],
            "resume": ["resume", "cv", "curriculum"],
            "assets_liabilities": ["assets", "liabilities", "balance", "financial"],
            "credit_report": ["credit", "report", "aecb", "bureau"],
            "bank_statement": ["bank", "statement", "account"]
        }
        
        try:
            for file_path in self.uploads_dir.iterdir():
                if file_path.is_file():
                    filename_lower = file_path.name.lower()
                    
                    # Determine document purpose based on filename
                    document_purpose = "unknown"
                    for doc_type, patterns in document_type_patterns.items():
                        if any(pattern in filename_lower for pattern in patterns):
                            document_purpose = doc_type
                            break
                    
                    # If still unknown, try to infer from file extension and content
                    if document_purpose == "unknown":
                        if file_path.suffix.lower() == ".xlsx":
                            document_purpose = "assets_liabilities"
                        elif "sample_emirates_id" in filename_lower:
                            document_purpose = "emirates_id"
                        elif "sample_resume" in filename_lower:
                            document_purpose = "resume"
                        elif "sample_credit" in filename_lower:
                            document_purpose = "credit_report"
                        elif "sample_bank" in filename_lower:
                            document_purpose = "bank_statement"
                    
                    documents.append({
                        "file_path": str(file_path),
                        "purpose": document_purpose,
                        "filename": file_path.name,
                        "file_size": file_path.stat().st_size,
                        "upload_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                    
                    logger.info(f"Found document: {file_path.name} -> {document_purpose}")
        
        except Exception as e:
            logger.error(f"Error scanning uploads directory: {str(e)}")
        
        return documents
    
    async def _generate_judgment_summary(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a concise judgment summary from workflow results."""
        
        assessment_result = workflow_result.get("assessment_result", {})
        comprehensive_report = workflow_result.get("comprehensive_report", {})
        
        # Extract key information
        applicant_name = assessment_result.get("applicant_name", "Unknown")
        final_decision = assessment_result.get("status", "unknown")
        overall_score = assessment_result.get("overall_score", 0)
        priority_level = assessment_result.get("priority_level", "medium")
        
        # Get executive summary if available
        executive_summary = comprehensive_report.get("executive_summary", {})
        recommendations = comprehensive_report.get("recommendations", {})
        risk_assessment = comprehensive_report.get("risk_assessment", {})
        
        judgment_summary = {
            "workflow_id": workflow_result.get("workflow_id"),
            "processing_timestamp": datetime.now().isoformat(),
            "applicant_information": {
                "name": applicant_name,
                "application_id": assessment_result.get("application_id", "N/A")
            },
            "final_judgment": {
                "decision": final_decision,
                "overall_score": overall_score,
                "priority_level": priority_level,
                "confidence_level": self._determine_confidence_level(workflow_result)
            },
            "key_findings": executive_summary.get("key_findings", []),
            "support_recommendation": {
                "recommended_support_types": recommendations.get("support_types", []),
                "estimated_support_amount": recommendations.get("support_amount", "To be determined"),
                "conditions": recommendations.get("conditions", []),
                "next_steps": recommendations.get("next_steps", [])
            },
            "risk_profile": {
                "risk_level": risk_assessment.get("risk_level", "medium"),
                "key_risk_factors": risk_assessment.get("risk_factors", []),
                "mitigation_required": len(risk_assessment.get("risk_factors", [])) > 0
            },
            "document_processing_summary": {
                "documents_processed": len(workflow_result.get("processed_documents", [])),
                "processing_duration": workflow_result.get("duration", "N/A"),
                "data_quality": self._assess_data_quality(workflow_result),
                "missing_documents": self._identify_missing_documents(workflow_result)
            },
            "approval_workflow": {
                "requires_manual_review": self._requires_manual_review(assessment_result, risk_assessment),
                "escalation_required": priority_level == "high" or risk_assessment.get("risk_level") == "high",
                "review_timeline": recommendations.get("review_timeline", "Standard processing time")
            }
        }
        
        return judgment_summary
    
    def _determine_confidence_level(self, workflow_result: Dict[str, Any]) -> str:
        """Determine confidence level based on document processing results."""
        processed_docs = workflow_result.get("processed_documents", [])
        
        if not processed_docs:
            return "low"
        
        # Calculate average confidence score
        confidence_scores = [doc.get("confidence_score", 0) for doc in processed_docs]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        if avg_confidence >= 0.8:
            return "high"
        elif avg_confidence >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _assess_data_quality(self, workflow_result: Dict[str, Any]) -> str:
        """Assess overall data quality from processing results."""
        errors = workflow_result.get("errors", [])
        warnings = workflow_result.get("warnings", [])
        processed_docs = workflow_result.get("processed_documents", [])
        
        if len(errors) > 0:
            return "poor"
        elif len(warnings) > 2:
            return "fair"
        elif len(processed_docs) >= 4:  # Most documents processed successfully
            return "excellent"
        elif len(processed_docs) >= 2:
            return "good"
        else:
            return "fair"
    
    def _identify_missing_documents(self, workflow_result: Dict[str, Any]) -> List[str]:
        """Identify missing critical documents."""
        processed_docs = workflow_result.get("processed_documents", [])
        doc_types = [doc.get("document_type") for doc in processed_docs]
        
        required_docs = ["emirates_id", "resume", "assets_liabilities", "credit_report", "bank_statement"]
        missing = [doc_type for doc_type in required_docs if doc_type not in doc_types]
        
        return missing
    
    def _requires_manual_review(self, assessment_result: Dict[str, Any], risk_assessment: Dict[str, Any]) -> bool:
        """Determine if manual review is required."""
        # Require manual review for high-risk cases or edge cases
        risk_level = risk_assessment.get("risk_level", "medium")
        overall_score = assessment_result.get("overall_score", 0)
        
        return (
            risk_level == "high" or
            overall_score < 0.3 or  # Very low scores
            overall_score > 0.9 or  # Very high scores (might be too good to be true)
            len(risk_assessment.get("risk_factors", [])) > 3
        )
    
    async def _save_judgment_summary(self, workflow_id: str, judgment_summary: Dict[str, Any]):
        """Save judgment summary to a separate file."""
        try:
            workflow_dir = self.outputs_dir / workflow_id
            workflow_dir.mkdir(exist_ok=True)
            
            # Save judgment summary
            judgment_file = workflow_dir / "final_judgment.json"
            with open(judgment_file, "w") as f:
                json.dump(judgment_summary, f, indent=2, default=str)
            
            # Create a human-readable summary
            readable_summary = self._create_readable_summary(judgment_summary)
            summary_file = workflow_dir / "judgment_summary.txt"
            with open(summary_file, "w") as f:
                f.write(readable_summary)
            
            logger.info(f"Judgment summary saved to {workflow_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save judgment summary: {str(e)}")
    
    def _create_readable_summary(self, judgment_summary: Dict[str, Any]) -> str:
        """Create a human-readable summary of the judgment."""
        
        applicant = judgment_summary.get("applicant_information", {})
        decision = judgment_summary.get("final_judgment", {})
        support = judgment_summary.get("support_recommendation", {})
        risk = judgment_summary.get("risk_profile", {})
        processing = judgment_summary.get("document_processing_summary", {})
        
        summary = f"""
FINANCIAL SUPPORT APPLICATION - FINAL JUDGMENT
==============================================

Workflow ID: {judgment_summary.get('workflow_id', 'N/A')}
Processing Date: {judgment_summary.get('processing_timestamp', 'N/A')}

APPLICANT INFORMATION
--------------------
Name: {applicant.get('name', 'N/A')}
Application ID: {applicant.get('application_id', 'N/A')}

FINAL DECISION
--------------
Decision: {decision.get('decision', 'N/A').upper()}
Overall Score: {decision.get('overall_score', 0):.2f}/1.0
Priority Level: {decision.get('priority_level', 'N/A').upper()}
Confidence Level: {decision.get('confidence_level', 'N/A').upper()}

KEY FINDINGS
------------
"""
        
        key_findings = judgment_summary.get("key_findings", [])
        for i, finding in enumerate(key_findings, 1):
            summary += f"{i}. {finding}\n"
        
        summary += f"""
SUPPORT RECOMMENDATION
---------------------
Recommended Support Types: {', '.join(support.get('recommended_support_types', ['None']))}
Estimated Support Amount: {support.get('estimated_support_amount', 'To be determined')}

Conditions:
"""
        
        conditions = support.get('conditions', [])
        for condition in conditions:
            summary += f"- {condition}\n"
        
        summary += f"""
Next Steps:
"""
        
        next_steps = support.get('next_steps', [])
        for step in next_steps:
            summary += f"- {step}\n"
        
        summary += f"""
RISK ASSESSMENT
---------------
Risk Level: {risk.get('risk_level', 'N/A').upper()}
Mitigation Required: {'YES' if risk.get('mitigation_required', False) else 'NO'}

Key Risk Factors:
"""
        
        risk_factors = risk.get('key_risk_factors', [])
        for factor in risk_factors:
            summary += f"- {factor}\n"
        
        summary += f"""
DOCUMENT PROCESSING SUMMARY
---------------------------
Documents Processed: {processing.get('documents_processed', 0)}
Processing Duration: {processing.get('processing_duration', 'N/A')}
Data Quality: {processing.get('data_quality', 'N/A').upper()}

Missing Documents: {', '.join(processing.get('missing_documents', ['None']))}

APPROVAL WORKFLOW
-----------------
Manual Review Required: {'YES' if judgment_summary.get('approval_workflow', {}).get('requires_manual_review', False) else 'NO'}
Escalation Required: {'YES' if judgment_summary.get('approval_workflow', {}).get('escalation_required', False) else 'NO'}
Review Timeline: {judgment_summary.get('approval_workflow', {}).get('review_timeline', 'Standard processing time')}

==============================================
End of Judgment Summary
"""
        
        return summary
    
    async def process_specific_documents(
        self,
        document_paths: List[str],
        applicant_info: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process specific documents by their paths.
        
        Args:
            document_paths: List of document file paths to process
            applicant_info: Optional applicant information
            workflow_id: Optional workflow ID
            
        Returns:
            Complete workflow result with assessment and judgment
        """
        try:
            # Generate workflow ID if not provided
            if not workflow_id:
                workflow_id = f"WF-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
            
            logger.info(f"Processing specific documents for workflow: {workflow_id}")
            
            # Prepare document list
            documents = []
            for doc_path in document_paths:
                if os.path.exists(doc_path):
                    # Determine document purpose from filename
                    filename = os.path.basename(doc_path).lower()
                    purpose = "unknown"
                    
                    if "emirates" in filename or "id" in filename:
                        purpose = "emirates_id"
                    elif "resume" in filename or "cv" in filename:
                        purpose = "resume"
                    elif "assets" in filename or "liabilities" in filename:
                        purpose = "assets_liabilities"
                    elif "credit" in filename or "report" in filename:
                        purpose = "credit_report"
                    elif "bank" in filename or "statement" in filename:
                        purpose = "bank_statement"
                    
                    documents.append({
                        "file_path": doc_path,
                        "purpose": purpose,
                        "filename": os.path.basename(doc_path)
                    })
                else:
                    logger.warning(f"Document not found: {doc_path}")
            
            if not documents:
                return {
                    "status": "error",
                    "message": "No valid documents found",
                    "workflow_id": workflow_id
                }
            
            # Create and execute workflow
            workflow_task = {
                "workflow_id": workflow_id,
                "documents": documents,
                "applicant_info": applicant_info or {}
            }
            
            result = await self.orchestrator.execute(workflow_task)
            
            # Generate final judgment summary
            if result.get("status") == "completed":
                judgment_summary = await self._generate_judgment_summary(result)
                result["judgment_summary"] = judgment_summary
                await self._save_judgment_summary(workflow_id, judgment_summary)
            
            return result
            
        except Exception as e:
            logger.error(f"Specific document processing failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "workflow_id": workflow_id or "unknown"
            }
    
    async def get_processing_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the processing status and results for a workflow."""
        return await self.orchestrator.get_workflow_status(workflow_id)
    
    async def list_all_workflows(self) -> List[Dict[str, Any]]:
        """List all processed workflows."""
        return await self.orchestrator.list_workflows()


# Test implementation
if __name__ == "__main__":
    import asyncio
    
    async def test_document_processing_service():
        """Test the document processing service."""
        print("🧪 Testing Document Processing Service...")
        
        # Create service
        service = DocumentProcessingService()
        
        # Test processing uploaded documents
        print("📄 Processing uploaded documents...")
        
        applicant_info = {
            "name": "Test Applicant",
            "email": "test@example.com",
            "phone": "+971-50-123-4567"
        }
        
        try:
            result = await service.process_uploaded_documents(
                applicant_info=applicant_info
            )
            
            print(f"✅ Processing completed!")
            print(f"Status: {result.get('status')}")
            print(f"Workflow ID: {result.get('workflow_id')}")
            
            if result.get("judgment_summary"):
                judgment = result["judgment_summary"]
                print(f"\n📋 Final Judgment:")
                print(f"Decision: {judgment.get('final_judgment', {}).get('decision')}")
                print(f"Score: {judgment.get('final_judgment', {}).get('overall_score', 0):.2f}")
                print(f"Risk Level: {judgment.get('risk_profile', {}).get('risk_level')}")
            
            # List all workflows
            print(f"\n📂 All Workflows:")
            workflows = await service.list_all_workflows()
            for wf in workflows[:3]:
                print(f"  - {wf.get('workflow_id')}: {wf.get('status')}")
            
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run test
    asyncio.run(test_document_processing_service())