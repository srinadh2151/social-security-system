"""
Assessment Agent for Financial Support and Economic Enablement

This agent evaluates applications based on multiple criteria to determine
eligibility for financial support and economic enablement programs.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from enum import Enum
import asyncio

try:
    from req_agents.llm_interface import LangChainLLMInterface
except ImportError:
    from llm_interface import LangChainLLMInterface

logger = logging.getLogger(__name__)


class EligibilityStatus(Enum):
    """Eligibility status options."""
    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    INSUFFICIENT_DATA = "insufficient_data"


class SupportType(Enum):
    """Types of support available."""
    FINANCIAL_ASSISTANCE = "financial_assistance"
    ECONOMIC_ENABLEMENT = "economic_enablement"
    EMERGENCY_SUPPORT = "emergency_support"
    SKILL_DEVELOPMENT = "skill_development"
    BUSINESS_SUPPORT = "business_support"


class AssessmentAgent:
    """Agent for assessing financial support applications."""
    
    def __init__(
        self,
        llm_interface: Optional[LangChainLLMInterface] = None,
        model: str = "gpt-4o",
        assessment_criteria: Optional[Dict[str, Any]] = None
    ):
        """Initialize assessment agent."""
        self.llm = llm_interface or LangChainLLMInterface(default_model=model)
        self.model = model
        
        # Default assessment criteria
        self.criteria = assessment_criteria or self._get_default_criteria()
        
        # System prompt for the agent
        self.system_prompt = """
You are an expert financial assessment agent for social security and economic enablement programs.
Your role is to evaluate applications fairly and consistently based on established criteria.

Key principles:
1. Be objective and data-driven in your assessments
2. Consider the applicant's overall situation holistically
3. Prioritize those with the greatest need
4. Ensure compliance with program guidelines
5. Provide clear reasoning for all decisions
6. Be sensitive to diverse backgrounds and circumstances

Always provide detailed explanations for your assessments and recommendations.
"""
    
    def _get_default_criteria(self) -> Dict[str, Any]:
        """Get default assessment criteria."""
        return {
            "income_thresholds": {
                "very_low": 30000,      # Below 30k - high priority
                "low": 50000,           # 30k-50k - medium priority  
                "moderate": 75000,      # 50k-75k - low priority
                "high": 100000          # Above 75k - generally ineligible
            },
            "family_size_multipliers": {
                1: 1.0,
                2: 1.3,
                3: 1.6,
                4: 1.9,
                5: 2.2,
                "6+": 2.5
            },
            "employment_stability_weights": {
                "unemployed": 1.0,
                "part_time": 0.7,
                "temporary": 0.6,
                "full_time": 0.3,
                "self_employed": 0.5
            },
            "demographic_priorities": {
                "single_parent": 0.8,
                "elderly": 0.7,
                "disabled": 0.9,
                "veteran": 0.6,
                "student": 0.5,
                "immigrant": 0.6
            },
            "wealth_assessment_factors": {
                "savings_threshold": 10000,
                "property_value_threshold": 200000,
                "debt_to_income_ratio": 0.4
            }
        }
    
    async def assess_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess a complete application for financial support eligibility.
        
        Args:
            application_data: JSON data containing applicant information
            
        Returns:
            Assessment result with eligibility status and recommendations
        """
        try:
            logger.info(f"Starting assessment for application ID: {application_data.get('application_id', 'N/A')}")
            
            # Debug: Log the structure of application_data
            logger.info(f"Application data structure: {json.dumps({k: type(v).__name__ for k, v in application_data.items()}, indent=2)}")
            if "applicant_info" in application_data:
                logger.info(f"Applicant info: {json.dumps(application_data['applicant_info'], indent=2)}")
            
            # Validate input data
            validation_result = self._validate_application_data(application_data)
            if not validation_result["valid"]:
                return {
                    "status": EligibilityStatus.INSUFFICIENT_DATA.value,
                    "reason": validation_result["errors"],
                    "assessment_date": datetime.now().isoformat(),
                    "recommendations": ["Please provide missing required information"]
                }
            
            # Perform individual assessments
            income_assessment = await self._assess_income_eligibility(application_data)
            employment_assessment = await self._assess_employment_history(application_data)
            family_assessment = await self._assess_family_situation(application_data)
            wealth_assessment = await self._assess_wealth_status(application_data)
            demographic_assessment = await self._assess_demographic_profile(application_data)
            
            # Combine all assessments
            comprehensive_assessment = await self._generate_comprehensive_assessment(
                application_data,
                {
                    "income": income_assessment,
                    "employment": employment_assessment,
                    "family": family_assessment,
                    "wealth": wealth_assessment,
                    "demographic": demographic_assessment
                }
            )
            
            # Generate final recommendation
            final_result = await self._generate_final_recommendation(
                application_data,
                comprehensive_assessment
            )
            
            logger.info(f"Assessment completed with status: {final_result['status']}")
            return final_result
            
        except Exception as e:
            logger.error(f"Assessment failed: {str(e)}")
            return {
                "status": EligibilityStatus.PENDING_REVIEW.value,
                "reason": f"Assessment error: {str(e)}",
                "assessment_date": datetime.now().isoformat(),
                "recommendations": ["Manual review required due to system error"]
            }
    
    def _validate_application_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that required application data is present."""
        required_fields = [
            "applicant_info",
            "income_info", 
            "employment_info",
            "family_info"
        ]
        
        errors = []
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check nested required fields
        if "applicant_info" in data:
            applicant_required = ["name", "age", "address"]
            for field in applicant_required:
                if field not in data["applicant_info"]:
                    errors.append(f"Missing applicant info: {field}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _assess_income_eligibility(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess income-based eligibility."""
        income_info = data.get("income_info", {})
        family_info = data.get("family_info", {})
        
        annual_income = income_info.get("annual_income", 0)
        family_size = family_info.get("family_size", 1)
        
        # Adjust income threshold based on family size
        base_threshold = self.criteria["income_thresholds"]["moderate"]
        family_multiplier = self.criteria["family_size_multipliers"].get(
            family_size if family_size <= 5 else "6+", 1.0
        )
        adjusted_threshold = base_threshold * family_multiplier
        
        # Calculate income-to-threshold ratio
        income_ratio = annual_income / adjusted_threshold if adjusted_threshold > 0 else 0
        
        # Determine eligibility level
        if income_ratio <= 0.4:  # Very low income
            eligibility_score = 1.0
            priority = "high"
        elif income_ratio <= 0.7:  # Low income
            eligibility_score = 0.8
            priority = "medium"
        elif income_ratio <= 1.0:  # Moderate income
            eligibility_score = 0.5
            priority = "low"
        else:  # High income
            eligibility_score = 0.2
            priority = "very_low"
        
        prompt = f"""
        Analyze the income eligibility for this applicant:
        
        Annual Income: ${annual_income:,}
        Family Size: {family_size}
        Adjusted Threshold: ${adjusted_threshold:,}
        Income Ratio: {income_ratio:.2f}
        
        Additional income details: {json.dumps(income_info, indent=2)}
        
        Provide a detailed assessment of income-based eligibility including:
        1. Income adequacy analysis
        2. Comparison to poverty guidelines
        3. Sustainability concerns
        4. Specific recommendations
        """
        
        analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        return {
            "score": eligibility_score,
            "priority": priority,
            "annual_income": annual_income,
            "adjusted_threshold": adjusted_threshold,
            "income_ratio": income_ratio,
            "analysis": analysis,
            "meets_criteria": eligibility_score >= 0.5
        }
    
    async def _assess_employment_history(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess employment history and stability."""
        employment_info = data.get("employment_info", {})
        
        current_status = employment_info.get("current_status", "unemployed")
        employment_history = employment_info.get("history", [])
        months_unemployed = employment_info.get("months_unemployed", 0)
        
        # Calculate employment stability score
        stability_weight = self.criteria["employment_stability_weights"].get(current_status, 0.5)
        
        # Factor in unemployment duration
        unemployment_penalty = min(months_unemployed * 0.1, 0.5) if months_unemployed > 0 else 0
        
        employment_score = max(0, stability_weight + unemployment_penalty)
        
        prompt = f"""
        Assess the employment situation for this applicant:
        
        Current Status: {current_status}
        Months Unemployed: {months_unemployed}
        Employment History: {json.dumps(employment_history, indent=2)}
        
        Full employment details: {json.dumps(employment_info, indent=2)}
        
        Evaluate:
        1. Employment stability and consistency
        2. Skills and qualifications
        3. Barriers to employment
        4. Potential for economic improvement
        5. Recommendations for support
        """
        
        analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        return {
            "score": employment_score,
            "current_status": current_status,
            "months_unemployed": months_unemployed,
            "stability_assessment": "stable" if employment_score < 0.5 else "unstable",
            "analysis": analysis,
            "support_needed": employment_score > 0.6
        }
    
    async def _assess_family_situation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess family situation and dependencies."""
        family_info = data.get("family_info", {})
        
        family_size = family_info.get("family_size", 1)
        dependents = family_info.get("dependents", 0)
        marital_status = family_info.get("marital_status", "single")
        special_circumstances = family_info.get("special_circumstances", [])
        
        # Calculate family support score
        dependency_ratio = dependents / family_size if family_size > 0 else 0
        
        # Higher score means more need for support
        family_score = dependency_ratio * 0.6
        
        # Add points for special circumstances
        if "single_parent" in special_circumstances:
            family_score += 0.3
        if "elderly_care" in special_circumstances:
            family_score += 0.2
        if "disabled_member" in special_circumstances:
            family_score += 0.4
        
        family_score = min(family_score, 1.0)
        
        prompt = f"""
        Analyze the family situation for this applicant:
        
        Family Size: {family_size}
        Dependents: {dependents}
        Marital Status: {marital_status}
        Special Circumstances: {special_circumstances}
        Dependency Ratio: {dependency_ratio:.2f}
        
        Full family details: {json.dumps(family_info, indent=2)}
        
        Assess:
        1. Family support needs and responsibilities
        2. Impact of dependents on financial situation
        3. Special circumstances requiring additional support
        4. Family stability and resilience factors
        5. Recommended support types
        """
        
        analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        return {
            "score": family_score,
            "family_size": family_size,
            "dependents": dependents,
            "dependency_ratio": dependency_ratio,
            "special_circumstances": special_circumstances,
            "analysis": analysis,
            "high_need": family_score > 0.6
        }
    
    async def _assess_wealth_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess wealth and assets."""
        wealth_info = data.get("wealth_info", {})
        income_info = data.get("income_info", {})
        
        savings = wealth_info.get("savings", 0)
        property_value = wealth_info.get("property_value", 0)
        debts = wealth_info.get("total_debts", 0)
        annual_income = income_info.get("annual_income", 0)
        
        # Calculate wealth indicators
        net_worth = savings + property_value - debts
        debt_to_income = debts / annual_income if annual_income > 0 else 0
        
        # Wealth assessment score (higher score = more need)
        wealth_score = 0
        
        if savings < self.criteria["wealth_assessment_factors"]["savings_threshold"]:
            wealth_score += 0.3
        
        if property_value < self.criteria["wealth_assessment_factors"]["property_value_threshold"]:
            wealth_score += 0.2
        
        if debt_to_income > self.criteria["wealth_assessment_factors"]["debt_to_income_ratio"]:
            wealth_score += 0.4
        
        if net_worth < 0:
            wealth_score += 0.3
        
        wealth_score = min(wealth_score, 1.0)
        
        prompt = f"""
        Evaluate the wealth and financial assets of this applicant:
        
        Savings: ${savings:,}
        Property Value: ${property_value:,}
        Total Debts: ${debts:,}
        Net Worth: ${net_worth:,}
        Debt-to-Income Ratio: {debt_to_income:.2f}
        
        Full wealth details: {json.dumps(wealth_info, indent=2)}
        
        Analyze:
        1. Overall financial stability and liquidity
        2. Asset adequacy for emergency situations
        3. Debt burden and repayment capacity
        4. Long-term financial sustainability
        5. Wealth-building potential and barriers
        """
        
        analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        return {
            "score": wealth_score,
            "net_worth": net_worth,
            "debt_to_income_ratio": debt_to_income,
            "savings": savings,
            "financial_stress": wealth_score > 0.6,
            "analysis": analysis,
            "needs_financial_counseling": debt_to_income > 0.5
        }
    
    async def _assess_demographic_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess demographic factors that may affect eligibility."""
        applicant_info = data.get("applicant_info", {})
        demographic_info = data.get("demographic_info", {})
        
        age = applicant_info.get("age", 0)
        gender = demographic_info.get("gender", "")
        ethnicity = demographic_info.get("ethnicity", "")
        disability_status = demographic_info.get("disability_status", False)
        veteran_status = demographic_info.get("veteran_status", False)
        education_level = demographic_info.get("education_level", "")
        
        # Calculate demographic priority score
        demo_score = 0
        priority_factors = []
        
        if age >= 65:
            demo_score += 0.3
            priority_factors.append("elderly")
        
        if age <= 25:
            demo_score += 0.2
            priority_factors.append("young_adult")
        
        if disability_status:
            demo_score += 0.4
            priority_factors.append("disabled")
        
        if veteran_status:
            demo_score += 0.3
            priority_factors.append("veteran")
        
        if education_level in ["high_school", "less_than_high_school"]:
            demo_score += 0.2
            priority_factors.append("limited_education")
        
        demo_score = min(demo_score, 1.0)
        
        prompt = f"""
        Analyze the demographic profile and potential barriers for this applicant:
        
        Age: {age}
        Gender: {gender}
        Ethnicity: {ethnicity}
        Disability Status: {disability_status}
        Veteran Status: {veteran_status}
        Education Level: {education_level}
        Priority Factors: {priority_factors}
        
        Full demographic details: {json.dumps(demographic_info, indent=2)}
        
        Consider:
        1. Potential barriers to economic opportunity
        2. Historical disadvantages or discrimination
        3. Special program eligibilities
        4. Cultural or language considerations
        5. Recommended targeted support services
        """
        
        analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        return {
            "score": demo_score,
            "priority_factors": priority_factors,
            "age": age,
            "disability_status": disability_status,
            "veteran_status": veteran_status,
            "analysis": analysis,
            "needs_specialized_support": demo_score > 0.5
        }
    
    async def _generate_comprehensive_assessment(
        self,
        application_data: Dict[str, Any],
        individual_assessments: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive assessment combining all factors."""
        
        # Calculate weighted overall score
        weights = {
            "income": 0.35,
            "employment": 0.3,
            "family": 0.15,
            "wealth": 0.15,
            "demographic": 0.05
        }
        
        overall_score = sum(
            individual_assessments[category]["score"] * weight
            for category, weight in weights.items()
        )
        
        # Determine preliminary eligibility
        if overall_score >= 0.8:
            preliminary_status = EligibilityStatus.APPROVED
        elif overall_score >= 0.49:
            preliminary_status = EligibilityStatus.CONDITIONALLY_APPROVED
        elif overall_score >= 0.4:
            preliminary_status = EligibilityStatus.PENDING_REVIEW
        else:
            preliminary_status = EligibilityStatus.REJECTED
        
        prompt = f"""
        Provide a comprehensive assessment summary for this application:
        
        Overall Score: {overall_score:.2f}
        Preliminary Status: {preliminary_status.value}
        
        Individual Assessment Scores:
        - Income: {individual_assessments['income']['score']:.2f}
        - Employment: {individual_assessments['employment']['score']:.2f}
        - Family: {individual_assessments['family']['score']:.2f}
        - Wealth: {individual_assessments['wealth']['score']:.2f}
        - Demographic: {individual_assessments['demographic']['score']:.2f}
        
        Key Findings:
        {json.dumps({k: v.get('analysis', 'No analysis') for k, v in individual_assessments.items()}, indent=2)}
        
        Provide:
        1. Executive summary of the applicant's situation
        2. Primary factors supporting or hindering eligibility
        3. Risk factors and mitigation strategies
        4. Holistic assessment of need and potential impact
        5. Preliminary recommendations for support types
        """
        
        comprehensive_analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        return {
            "overall_score": overall_score,
            "preliminary_status": preliminary_status.value,
            "individual_scores": {k: v["score"] for k, v in individual_assessments.items()},
            "comprehensive_analysis": comprehensive_analysis,
            "assessment_timestamp": datetime.now().isoformat()
        }
    
    async def _generate_final_recommendation(
        self,
        application_data: Dict[str, Any],
        comprehensive_assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final recommendation and support plan."""
        
        overall_score = comprehensive_assessment["overall_score"]
        preliminary_status = comprehensive_assessment["preliminary_status"]
        
        # Determine support types
        recommended_support = []
        if overall_score >= 0.7:
            recommended_support.extend([
                SupportType.FINANCIAL_ASSISTANCE.value,
                SupportType.ECONOMIC_ENABLEMENT.value
            ])
        elif overall_score >= 0.5:
            recommended_support.append(SupportType.ECONOMIC_ENABLEMENT.value)
        
        # Add specialized support based on individual assessments
        if application_data.get("employment_info", {}).get("current_status") == "unemployed":
            recommended_support.append(SupportType.SKILL_DEVELOPMENT.value)
        
        if application_data.get("wealth_info", {}).get("total_debts", 0) > 50000:
            recommended_support.append("debt_counseling")
        
        # Extract applicant name for the prompt
        applicant_name_for_prompt = "the applicant"
        if application_data.get("applicant_info", {}).get("name"):
            applicant_name_for_prompt = application_data["applicant_info"]["name"]
        elif application_data.get("applicant_info", {}).get("full_name"):
            applicant_name_for_prompt = application_data["applicant_info"]["full_name"]
        
        prompt = f"""
        Generate the final recommendation for this application:
        
        APPLICANT NAME: {applicant_name_for_prompt}
        Overall Assessment Score: {overall_score:.2f}
        Preliminary Status: {preliminary_status}
        Recommended Support Types: {recommended_support}
        
        Application Summary: {json.dumps(application_data.get('applicant_info', {}), indent=2)}
        Comprehensive Analysis: {comprehensive_assessment['comprehensive_analysis']}
        
        IMPORTANT: When referring to the applicant in your response, use the name "{applicant_name_for_prompt}" (not any placeholder names).
        
        Provide:
        1. Final eligibility determination with clear reasoning
        2. Specific support amount/level recommendations
        3. Conditions or requirements for approval
        4. Timeline for support implementation
        5. Success metrics and review schedule
        6. Alternative resources if not approved
        """
        
        final_analysis = await self.llm.generate_response(prompt, system_prompt=self.system_prompt)
        
        # Determine final status
        final_status = preliminary_status
        if overall_score < 0.3:
            final_status = EligibilityStatus.REJECTED.value
        elif overall_score >= 0.8:
            final_status = EligibilityStatus.APPROVED.value
        
        # Extract applicant name from multiple possible locations
        applicant_name = "N/A"
        
        # Try different paths to find the name
        if application_data.get("applicant_info", {}).get("name"):
            applicant_name = application_data["applicant_info"]["name"]
        elif application_data.get("applicant_info", {}).get("full_name"):
            applicant_name = application_data["applicant_info"]["full_name"]
        elif application_data.get("personal_info", {}).get("name"):
            applicant_name = application_data["personal_info"]["name"]
        elif application_data.get("personal_info", {}).get("full_name"):
            applicant_name = application_data["personal_info"]["full_name"]
        
        # Log the application data structure for debugging
        logger.info(f"Application data keys: {list(application_data.keys())}")
        if "applicant_info" in application_data:
            logger.info(f"Applicant info keys: {list(application_data['applicant_info'].keys())}")
        
        return {
            "application_id": application_data.get("application_id", "N/A"),
            "applicant_name": applicant_name,
            "status": final_status,
            "overall_score": overall_score,
            "individual_assessments": comprehensive_assessment["individual_scores"],
            "recommended_support_types": recommended_support,
            "final_analysis": final_analysis,
            "assessment_date": datetime.now().isoformat(),
            "assessor": "AI Assessment Agent v1.0",
            "requires_human_review": overall_score >= 0.4 and overall_score <= 0.6,
            "priority_level": "high" if overall_score >= 0.8 else "medium" if overall_score >= 0.5 else "low"
        }


# Test implementation
if __name__ == "__main__":
    import asyncio
    
    async def test_assessment_agent():
        """Test the assessment agent with sample data."""
        print("🧪 Testing Assessment Agent...")
        
        # Sample application data
        sample_application = {
            "application_id": "APP-2024-001",
            "applicant_info": {
                "name": "Jane Smith",
                "age": 34,
                "address": "123 Main St, Anytown, ST 12345"
            },
            "income_info": {
                "annual_income": 28000,
                "income_sources": ["part_time_employment", "child_support"],
                "monthly_income": 2333
            },
            "employment_info": {
                "current_status": "part_time",
                "months_unemployed": 0,
                "history": [
                    {"employer": "Local Store", "duration": "2 years", "status": "part_time"},
                    {"employer": "Previous Job", "duration": "1 year", "status": "full_time"}
                ]
            },
            "family_info": {
                "family_size": 3,
                "dependents": 2,
                "marital_status": "single",
                "special_circumstances": ["single_parent"]
            },
            "wealth_info": {
                "savings": 1500,
                "property_value": 0,
                "total_debts": 15000
            },
            "demographic_info": {
                "gender": "female",
                "ethnicity": "hispanic",
                "disability_status": False,
                "veteran_status": False,
                "education_level": "high_school"
            }
        }
        
        # Create assessment agent
        agent = AssessmentAgent(model="gpt-4o")
        
        try:
            # Perform assessment
            print("📋 Processing application...")
            result = await agent.assess_application(sample_application)
            
            # Display results
            print(f"\n✅ Assessment Complete!")
            print(f"Status: {result['status']}")
            print(f"Overall Score: {result.get('overall_score', 'N/A')}")
            print(f"Priority Level: {result.get('priority_level', 'N/A')}")
            print(f"Recommended Support: {result.get('recommended_support_types', [])}")
            print(f"Requires Human Review: {result.get('requires_human_review', False)}")
            
            print(f"\n📊 Individual Assessment Scores:")
            for category, score in result.get('individual_assessments', {}).items():
                print(f"  {category.title()}: {score:.2f}")
            
            print(f"\n📝 Final Analysis:")
            print(result.get('final_analysis', 'No analysis available'))
            
        except Exception as e:
            print(f"❌ Assessment failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Run test
    asyncio.run(test_assessment_agent())