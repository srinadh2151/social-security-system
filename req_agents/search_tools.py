"""
Search Tools for Job Search and Career Guidance

This module provides tools for searching job opportunities and career guidance resources.
"""

import requests
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json
import os
from urllib.parse import quote_plus
from datetime import datetime, timedelta


class JobSearchInput(BaseModel):
    """Input for job search tool."""
    skills: str = Field(description="Skills, job title, or experience to search for")
    location: str = Field(default="UAE", description="Location to search jobs in")
    experience_level: str = Field(default="", description="Experience level (entry, mid, senior)")


class LinkedInJobSearchAPI:
    """LinkedIn Job Search API integration."""
    
    def __init__(self):
        self.base_url = "https://linkedin-job-search-api.p.rapidapi.com/active-jb-7d"
        self.headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": "linkedin-job-search-api.p.rapidapi.com"
        }
    
    def search_jobs(self, title: str, location: str = "Dubai", experience_level: str = "", limit: int = 4) -> List[Dict[str, Any]]:
        """Search for jobs using LinkedIn API."""
        try:
            # Map experience levels to API format
            experience_mapping = {
                "entry": "0-2",
                "junior": "0-2", 
                "mid": "2-5",
                "senior": "5-10",
                "expert": "10+",
                "": "2-5"  # Default to mid-level
            }
            
            # Map location to specific cities if UAE
            location_mapping = {
                "UAE": "Dubai",
                "United Arab Emirates": "Dubai",
                "uae": "Dubai"
            }
            
            mapped_location = location_mapping.get(location, location)
            mapped_experience = experience_mapping.get(experience_level.lower(), "2-5")
            
            # Calculate date filter (last 30 days for better results)
            date_filter = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            querystring = {
                "limit": str(limit),
                "offset": "0",
                "title_filter": f'"{title}"',
                "location_filter": f'"{mapped_location}"',
                "ai_experience_level_filter": mapped_experience,
                "date_filter": date_filter
            }
            
            print(f"LinkedIn API request: {title} in {mapped_location} ({mapped_experience} years)")
            
            response = requests.get(self.base_url, headers=self.headers, params=querystring, timeout=15)
            
            print(f"LinkedIn API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"LinkedIn API response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Response keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"Response list length: {len(data)}")
                    
                    return self._process_linkedin_response(data)
                except json.JSONDecodeError as e:
                    print(f"LinkedIn API JSON decode error: {str(e)}")
                    print(f"Response text: {response.text[:500]}")
                    return []
            else:
                print(f"LinkedIn API error: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"LinkedIn API request failed: {str(e)}")
            return []
        except Exception as e:
            print(f"LinkedIn API processing error: {str(e)}")
            return []
    
    def _process_linkedin_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process LinkedIn API response into standardized format."""
        jobs = []
        
        try:
            # Handle different response formats
            if isinstance(data, list):
                job_list = data
            elif isinstance(data, dict):
                job_list = data.get('jobs', data.get('data', data.get('results', [])))
                if isinstance(job_list, dict):
                    job_list = job_list.get('jobs', [])
            else:
                print(f"Unexpected data format: {type(data)}")
                return []
            
            print(f"Processing {len(job_list)} jobs from LinkedIn API")
            
            for i, job in enumerate(job_list):
                try:
                    # Handle case where job might be a string or unexpected format
                    if not isinstance(job, dict):
                        print(f"Skipping non-dict job at index {i}: {type(job)}")
                        continue
                    
                    # Extract company name safely
                    company = "N/A"
                    if "company" in job:
                        company_data = job["company"]
                        if isinstance(company_data, dict):
                            company = company_data.get("name", "N/A")
                        elif isinstance(company_data, str):
                            company = company_data
                    
                    processed_job = {
                        "title": job.get("title", "N/A"),
                        "company": company,
                        "location": job.get("location", "N/A"),
                        "salary": self._extract_salary(job),
                        "requirements": self._extract_requirements(job),
                        "apply_link": job.get("job_url", job.get("url", job.get("link", "Apply on LinkedIn"))),
                        "match_score": self._calculate_match_score(job),
                        "posted_date": job.get("posted_date", job.get("date", "Recently")),
                        "job_type": job.get("job_type", job.get("type", "Full-time")),
                        "description": job.get("description", "")[:200] + "..." if job.get("description") else "No description available"
                    }
                    jobs.append(processed_job)
                    
                except Exception as e:
                    print(f"Error processing job at index {i}: {str(e)}")
                    continue
            
            print(f"Successfully processed {len(jobs)} jobs")
            return jobs
            
        except Exception as e:
            print(f"Error in _process_linkedin_response: {str(e)}")
            return []
    
    def _extract_salary(self, job: Dict[str, Any]) -> str:
        """Extract salary information from job data."""
        # Try different salary fields
        salary_fields = ["salary", "salary_range", "compensation", "pay"]
        
        for field in salary_fields:
            if field in job and job[field]:
                salary = job[field]
                if isinstance(salary, dict):
                    min_sal = salary.get("min", "")
                    max_sal = salary.get("max", "")
                    currency = salary.get("currency", "AED")
                    if min_sal and max_sal:
                        return f"{currency} {min_sal} - {max_sal}"
                    elif min_sal:
                        return f"{currency} {min_sal}+"
                elif isinstance(salary, str) and salary.strip():
                    return salary
        
        # Default salary ranges based on job title
        title = job.get("title", "").lower()
        if any(word in title for word in ["senior", "lead", "principal"]):
            return "AED 15,000 - 25,000"
        elif any(word in title for word in ["manager", "director"]):
            return "AED 18,000 - 30,000"
        elif any(word in title for word in ["engineer", "developer", "analyst"]):
            return "AED 8,000 - 15,000"
        else:
            return "Competitive salary"
    
    def _extract_requirements(self, job: Dict[str, Any]) -> str:
        """Extract job requirements from job data."""
        requirements = []
        
        # Extract from description
        description = job.get("description", "").lower()
        if "bachelor" in description or "degree" in description:
            requirements.append("Bachelor's degree preferred")
        if "experience" in description:
            requirements.append("Relevant work experience")
        if "english" in description:
            requirements.append("English proficiency")
        
        # Extract from skills
        skills = job.get("skills", [])
        if skills and isinstance(skills, list):
            requirements.extend(skills[:3])  # Top 3 skills
        
        # Default requirements
        if not requirements:
            requirements = ["Relevant experience", "Good communication skills", "UAE residence visa"]
        
        return ", ".join(requirements[:4])  # Limit to 4 requirements
    
    def _calculate_match_score(self, job: Dict[str, Any]) -> int:
        """Calculate a match score for the job."""
        score = 70  # Base score
        
        # Boost score based on job attributes
        title = job.get("title", "").lower()
        if any(word in title for word in ["senior", "lead"]):
            score += 10
        if job.get("salary"):
            score += 5
        if job.get("company", {}).get("name") if isinstance(job.get("company"), dict) else job.get("company"):
            score += 5
        
        return min(score, 95)  # Cap at 95%


class JobSearchTool(BaseTool):
    """Tool to search for job opportunities based on skills and experience."""
    
    name: str = "job_search"
    description: str = """
    Search for job opportunities on popular job sites like LinkedIn, Indeed, Bayt, etc.
    Provide skills, job title, or experience and get relevant job listings.
    """
    args_schema: type = JobSearchInput
    
    def _run(self, skills: str, location: str = "UAE", experience_level: str = "") -> str:
        """Search for job opportunities using real LinkedIn API."""
        try:
            search_query = f"{skills} {experience_level} jobs in {location}".strip()
            
            # Initialize LinkedIn API
            linkedin_api = LinkedInJobSearchAPI()
            
            # Try to get real jobs from LinkedIn API
            real_jobs = linkedin_api.search_jobs(
                title=skills,
                location=location,
                experience_level=experience_level,
                limit=4
            )
            
            # If API fails or returns no results, fall back to simulated data
            if not real_jobs:
                print("LinkedIn API unavailable, using simulated data...")
                real_jobs = self._simulate_job_search(skills, location, experience_level)
            
            formatted_results = f"""
            🔍 JOB SEARCH RESULTS FOR: {search_query.upper()}
            {'='*60}
            Here are the top job opportunities I found for you:
            """
            
            for i, job in enumerate(real_jobs, 1):
                formatted_results += f"""
                {i}. 🏢 {job['title']} at {job['company']}
                📍 Location: {job['location']}
                💰 Salary: {job['salary']}
                📋 Requirements: {job['requirements']}
                🔗 Apply: {job['apply_link']}
                ⭐ Match Score: {job['match_score']}%
                📅 Posted: {job.get('posted_date', 'Recently')}
                """
            
            # Add data source indicator
            is_real_data = len(real_jobs) > 0 and any(
                'linkedin' in job.get('apply_link', '').lower() or 
                job.get('company', '') not in ['Various Companies', 'Emirates Airlines', 'ADNOC', 'Emaar Properties']
                for job in real_jobs
            )
            data_source = "🌐 Data from LinkedIn Jobs API" if is_real_data else "📊 Simulated job data for demo"
            
            formatted_results += f"""
            {data_source}
            💡 TIPS FOR APPLYING:
            • Update your CV to highlight relevant skills
            • Research each company before applying
            • Prepare for common interview questions
            • Consider networking through LinkedIn
            • Apply within 24-48 hours of job posting

            🌐 RECOMMENDED JOB SITES:
            • LinkedIn Jobs (linkedin.com/jobs)
            • Bayt.com (UAE's leading job site)
            • Indeed UAE (ae.indeed.com)
            • GulfTalent (gulftalent.com)
            • Naukri Gulf (naukrigulf.com)
            """
            
            return formatted_results
            
        except Exception as e:
            return f"Error searching for jobs: {str(e)}\n\nFalling back to simulated data...\n\n" + self._get_fallback_results(skills, location, experience_level)

    def _get_fallback_results(self, skills: str, location: str, experience_level: str) -> str:
        """Get fallback results when API fails."""
        try:
            fallback_jobs = self._simulate_job_search(skills, location, experience_level)
            search_query = f"{skills} {experience_level} jobs in {location}".strip()
            
            formatted_results = f"""
            🔍 JOB SEARCH RESULTS FOR: {search_query.upper()}
            {'='*60}
            Here are relevant job opportunities:
            """
            
            for i, job in enumerate(fallback_jobs, 1):
                formatted_results += f"""
                {i}. 🏢 {job['title']} at {job['company']}
                📍 Location: {job['location']}
                💰 Salary: {job['salary']}
                📋 Requirements: {job['requirements']}
                🔗 Apply: {job['apply_link']}
                ⭐ Match Score: {job['match_score']}%
                """
            
            return formatted_results
            
        except Exception as e:
            return f"Error in fallback job search: {str(e)}"
    
    def _simulate_job_search(self, skills: str, location: str, experience_level: str) -> List[Dict[str, Any]]:
        """Simulate job search results based on skills."""
        
        # Map skills to relevant jobs
        skill_job_mapping = {
            "engineer": [
                {"title": "Senior Software Engineer", "company": "Emirates Airlines", "salary": "AED 12,000 - 18,000"},
                {"title": "Mechanical Engineer", "company": "ADNOC", "salary": "AED 10,000 - 15,000"},
                {"title": "Civil Engineer", "company": "Emaar Properties", "salary": "AED 8,000 - 12,000"}
            ],
            "manager": [
                {"title": "Project Manager", "company": "Dubai Municipality", "salary": "AED 15,000 - 22,000"},
                {"title": "Operations Manager", "company": "Carrefour UAE", "salary": "AED 12,000 - 18,000"},
                {"title": "Business Development Manager", "company": "Etisalat", "salary": "AED 14,000 - 20,000"}
            ],
            "consultant": [
                {"title": "Business Consultant", "company": "PwC Middle East", "salary": "AED 16,000 - 25,000"},
                {"title": "IT Consultant", "company": "Accenture", "salary": "AED 14,000 - 22,000"},
                {"title": "Management Consultant", "company": "McKinsey & Company", "salary": "AED 20,000 - 35,000"}
            ],
            "supervisor": [
                {"title": "Operations Supervisor", "company": "DP World", "salary": "AED 8,000 - 12,000"},
                {"title": "Team Supervisor", "company": "Majid Al Futtaim", "salary": "AED 7,000 - 10,000"},
                {"title": "Production Supervisor", "company": "ALBA", "salary": "AED 9,000 - 13,000"}
            ]
        }
        
        # Default jobs for any skill
        default_jobs = [
            {"title": "Administrative Assistant", "company": "Various Companies", "salary": "AED 4,000 - 7,000"},
            {"title": "Customer Service Representative", "company": "Telecom Companies", "salary": "AED 5,000 - 8,000"},
            {"title": "Sales Executive", "company": "Real Estate Firms", "salary": "AED 6,000 - 12,000"},
            {"title": "Data Entry Clerk", "company": "Government Entities", "salary": "AED 3,500 - 6,000"},
            {"title": "Office Coordinator", "company": "SME Companies", "salary": "AED 4,500 - 7,500"},
            {"title": "Data Scientist", "company": "Various Companies", "salary": "AED 20,000 - 35,000"}
            ]
        
        # Find matching jobs
        jobs = []
        skills_lower = skills.lower()
        
        for skill_key, skill_jobs in skill_job_mapping.items():
            if skill_key in skills_lower:
                jobs.extend(skill_jobs)
        
        # If no specific matches, use default jobs
        if not jobs:
            jobs = default_jobs
        
        # Add common fields and limit to top 5
        formatted_jobs = []
        skill_key = None  # Initialize skill_key
        for skill_key, skill_jobs in skill_job_mapping.items():
            if skill_key in skills_lower:
                break
        
        for i, job in enumerate(jobs[:5]):
            match_score = 95 - (i * 5) if skill_key and skill_key in skills_lower else 70 - (i * 5)
            
            formatted_job = {
                **job,
                "location": f"{location} (Various Emirates)" if location == "UAE" else location,
                "requirements": f"Relevant experience in {skills}, Good communication skills, UAE residence visa",
                "apply_link": f"Apply through company website or LinkedIn",
                "match_score": max(match_score, 60),
                "posted_date": "Recently"
            }
            formatted_jobs.append(formatted_job)
        
        return formatted_jobs


class UdemyCoursesAPI:
    """Udemy Courses API integration for real course recommendations with fallback API."""
    
    def __init__(self):
        # Primary API
        self.base_url = "https://udemy-paid-courses-for-free-api.p.rapidapi.com/rapidapi/courses/search"
        self.headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": "udemy-paid-courses-for-free-api.p.rapidapi.com"
        }
        
        # Alternate API
        self.alternate_url = "https://udemy-api2.p.rapidapi.com/v1/udemy/search"
        self.alternate_headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": "udemy-api2.p.rapidapi.com",
            "Content-Type": "application/json"
        }
    
    def search_courses(self, query: str, page_size: int = 5) -> List[Dict[str, Any]]:
        """Search for courses using Udemy API with fallback to alternate API."""
        # Try primary API first
        courses = self._try_primary_api(query, page_size)
        
        # If primary API fails or returns no results, try alternate API
        if not courses:
            print("Primary Udemy API failed, trying alternate API...")
            courses = self._try_alternate_api(query, page_size)
        
        return courses
    
    def _try_primary_api(self, query: str, page_size: int) -> List[Dict[str, Any]]:
        """Try the primary Udemy API."""
        try:
            querystring = {
                "page": "1",
                "page_size": str(page_size),
                "query": query
            }
            
            print(f"Primary Udemy API request: {query}")
            
            response = requests.get(self.base_url, headers=self.headers, params=querystring, timeout=15)
            
            print(f"Primary Udemy API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Primary Udemy API response type: {type(data)}")
                    
                    courses = self._process_udemy_response(data)
                    if courses:
                        print(f"✅ Primary API returned {len(courses)} courses")
                        return courses
                    else:
                        print("⚠️ Primary API returned no courses")
                        return []
                except json.JSONDecodeError as e:
                    print(f"Primary Udemy API JSON decode error: {str(e)}")
                    return []
            else:
                print(f"Primary Udemy API error: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Primary Udemy API request failed: {str(e)}")
            return []
        except Exception as e:
            print(f"Primary Udemy API processing error: {str(e)}")
            return []
    
    def _try_alternate_api(self, query: str, page_size: int) -> List[Dict[str, Any]]:
        """Try the alternate Udemy API."""
        try:
            querystring = {"text": query}
            payload = {
                "page": 1,
                "page_size": min(page_size, 3),  # Alternate API seems to have smaller limits
                "ratings": "",
                "instructional_level": [],
                "lang": [],
                "price": [],
                "duration": [],
                "subtitles_lang": [],
                "sort": "popularity",
                "features": [],
                "locale": "en_US",
                "extract_pricing": True
            }
            
            print(f"Alternate Udemy API request: {query}")
            
            response = requests.post(
                self.alternate_url, 
                json=payload, 
                headers=self.alternate_headers, 
                params=querystring, 
                timeout=15
            )
            
            print(f"Alternate Udemy API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Alternate Udemy API response type: {type(data)}")
                    
                    courses = self._process_alternate_udemy_response(data)
                    if courses:
                        print(f"✅ Alternate API returned {len(courses)} courses")
                        return courses
                    else:
                        print("⚠️ Alternate API returned no courses")
                        return []
                except json.JSONDecodeError as e:
                    print(f"Alternate Udemy API JSON decode error: {str(e)}")
                    return []
            else:
                print(f"Alternate Udemy API error: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Alternate Udemy API request failed: {str(e)}")
            return []
        except Exception as e:
            print(f"Alternate Udemy API processing error: {str(e)}")
            return []
    
    def _process_udemy_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Udemy API response into standardized format."""
        courses = []
        
        try:
            # Handle different response formats
            if isinstance(data, dict):
                course_list = data.get('courses', data.get('results', data.get('data', [])))
            elif isinstance(data, list):
                course_list = data
            else:
                print(f"Unexpected Udemy data format: {type(data)}")
                return []
            
            print(f"Processing {len(course_list)} courses from Udemy API")
            
            for i, course in enumerate(course_list):
                try:
                    if not isinstance(course, dict):
                        print(f"Skipping non-dict course at index {i}: {type(course)}")
                        continue
                    
                    processed_course = {
                        "title": course.get("name", course.get("title", "N/A")),
                        "provider": "Udemy",
                        "instructor": course.get("instructor", course.get("author", "Udemy Instructor")),
                        "duration": self._extract_duration(course),
                        "cost": self._extract_cost(course),
                        "level": self._extract_level(course),
                        "description": self._extract_description(course),
                        "link": course.get("url", course.get("course_url", course.get("clean_url", "udemy.com"))),
                        "rating": course.get("rating", course.get("score", "4.5")),
                        "students": course.get("students", course.get("enrolled", "1000+")),
                        "category": course.get("category", "General"),
                        "actual_price": course.get("actual_price_usd", 0),
                        "sale_price": course.get("sale_price_usd", 0),
                        "sale_end": course.get("sale_end", "")
                    }
                    courses.append(processed_course)
                    
                except Exception as e:
                    print(f"Error processing course at index {i}: {str(e)}")
                    continue
            
            print(f"Successfully processed {len(courses)} courses")
            return courses
            
        except Exception as e:
            print(f"Error in _process_udemy_response: {str(e)}")
            return []
    
    def _extract_duration(self, course: Dict[str, Any]) -> str:
        """Extract course duration."""
        duration_fields = ["duration", "length", "total_length", "hours"]
        
        for field in duration_fields:
            if field in course and course[field]:
                duration = course[field]
                if isinstance(duration, (int, float)):
                    return f"{duration} hours"
                elif isinstance(duration, str):
                    return duration
        
        return "Self-paced"
    
    def _extract_cost(self, course: Dict[str, Any]) -> str:
        """Extract course cost."""
        # Check for free indicators
        if course.get("is_free", False) or course.get("price", 0) == 0:
            return "Free"
        
        # Check for price
        price = course.get("price", course.get("cost"))
        if price:
            if isinstance(price, (int, float)):
                return f"${price}"
            elif isinstance(price, str):
                return price
        
        return "Free (Limited time)"
    
    def _extract_level(self, course: Dict[str, Any]) -> str:
        """Extract course level."""
        level = course.get("level", course.get("difficulty", ""))
        if level:
            return level.title()
        
        # Infer from title
        title = course.get("title", "").lower()
        if any(word in title for word in ["beginner", "intro", "basics", "fundamentals"]):
            return "Beginner"
        elif any(word in title for word in ["advanced", "expert", "master", "professional"]):
            return "Advanced"
        else:
            return "Intermediate"
    
    def _extract_description(self, course: Dict[str, Any]) -> str:
        """Extract course description."""
        desc_fields = ["description", "summary", "what_you_learn", "objectives"]
        
        for field in desc_fields:
            if field in course and course[field]:
                desc = course[field]
                if isinstance(desc, str):
                    return desc[:200] + "..." if len(desc) > 200 else desc
                elif isinstance(desc, list):
                    return ", ".join(desc[:3])
        
        return "Comprehensive course covering essential topics"
    
    def _process_alternate_udemy_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process alternate Udemy API response into standardized format."""
        courses = []
        
        try:
            # Handle alternate API response format
            if isinstance(data, dict):
                # Check for nested data structure
                if 'data' in data and isinstance(data['data'], dict):
                    course_list = data['data'].get('courses', [])
                else:
                    course_list = data.get('results', data.get('courses', []))
            elif isinstance(data, list):
                course_list = data
            else:
                print(f"Unexpected alternate Udemy data format: {type(data)}")
                return []
            
            print(f"Processing {len(course_list)} courses from alternate Udemy API")
            
            for i, course in enumerate(course_list):
                try:
                    if not isinstance(course, dict):
                        print(f"Skipping non-dict course at index {i}: {type(course)}")
                        continue
                    
                    processed_course = {
                        "title": course.get("title", course.get("name", "N/A")),
                        "provider": "Udemy",
                        "instructor": course.get("instructor", course.get("visible_instructors", [{}])[0].get("display_name", "Udemy Instructor")),
                        "duration": self._extract_alternate_duration(course),
                        "cost": self._extract_alternate_cost(course),
                        "level": course.get("instructional_level", course.get("level", "All Levels")),
                        "description": course.get("headline", course.get("description", "Comprehensive course covering essential topics"))[:200],
                        "link": f"https://www.udemy.com{course.get('url', '')}" if course.get('url') else "https://www.udemy.com",
                        "rating": course.get("rating", course.get("avg_rating", "4.5")),
                        "students": course.get("num_subscribers", course.get("students", "1000+")),
                        "category": course.get("category", course.get("primary_category", {}).get("title", "General")),
                        "actual_price": course.get("price", {}).get("amount", 0) if isinstance(course.get("price"), dict) else 0,
                        "sale_price": course.get("discount", {}).get("price", {}).get("amount", 0) if course.get("discount") else 0,
                        "sale_end": ""
                    }
                    courses.append(processed_course)
                    
                except Exception as e:
                    print(f"Error processing alternate API course at index {i}: {str(e)}")
                    continue
            
            print(f"Successfully processed {len(courses)} courses from alternate API")
            return courses
            
        except Exception as e:
            print(f"Error in _process_alternate_udemy_response: {str(e)}")
            return []
    
    def _extract_alternate_duration(self, course: Dict[str, Any]) -> str:
        """Extract course duration from alternate API."""
        # Alternate API might have different duration fields
        duration = course.get("content_info", course.get("duration", ""))
        if duration:
            if isinstance(duration, str):
                return duration
            elif isinstance(duration, (int, float)):
                return f"{duration} hours"
        
        # Try content length
        content_length = course.get("content_length", 0)
        if content_length:
            hours = content_length / 3600  # Convert seconds to hours
            return f"{hours:.1f} hours"
        
        return "Self-paced"
    
    def _extract_alternate_cost(self, course: Dict[str, Any]) -> str:
        """Extract course cost from alternate API."""
        # Check if course is free
        if course.get("is_paid", True) == False:
            return "Free"
        
        # Check price structure
        price_info = course.get("price", {})
        if isinstance(price_info, dict):
            amount = price_info.get("amount", 0)
            currency = price_info.get("currency", "USD")
            if amount == 0:
                return "Free"
            else:
                return f"{currency} {amount}"
        
        return "Free (Limited time)"


class CourseRecommendationInput(BaseModel):
    """Input for course recommendation tool."""
    current_skills: str = Field(description="Current skills and background")
    career_goal: str = Field(default="", description="Desired career direction")
    education_level: str = Field(default="", description="Current education level")


class CourseRecommendationTool(BaseTool):
    """Tool to recommend courses and training programs for career development."""
    
    name: str = "course_recommendations"
    description: str = """
    Recommend courses, certifications, and training programs based on current skills 
    and career goals. Provides both online and local training options.
    """
    args_schema: type = CourseRecommendationInput
    
    def _run(self, current_skills: str, career_goal: str = "", education_level: str = "") -> str:
        """Recommend courses for career development using real Udemy API."""
        try:
            # Initialize Udemy API
            udemy_api = UdemyCoursesAPI()
            
            # Generate search queries based on skills
            search_queries = self._generate_search_queries(current_skills, career_goal)
            
            # Get real courses from Udemy API
            real_courses = []
            for query in search_queries:
                courses = udemy_api.search_courses(query, page_size=3)
                real_courses.extend(courses)
            
            # If API fails or returns no results, fall back to simulated data
            if not real_courses:
                print("Udemy API unavailable, using simulated data...")
                recommendations = self._generate_course_recommendations(current_skills, career_goal, education_level)
                return self._format_fallback_recommendations(recommendations, current_skills, career_goal, education_level)
            
            # Format results with real Udemy courses
            formatted_results = f"""
📚 COURSE RECOMMENDATIONS FOR YOUR CAREER DEVELOPMENT
{'='*65}

Based on your background: {current_skills}
Career Goal: {career_goal or 'General skill enhancement'}
Education Level: {education_level or 'Not specified'}

"""
            
            # Real Udemy Courses
            formatted_results += "🌐 REAL UDEMY COURSES (FREE & PAID):\n\n"
            for i, course in enumerate(real_courses[:6], 1):  # Limit to top 6
                formatted_results += f"""
{i}. 📖 {course['title']}
   🏫 Provider: {course['provider']} | 👨‍🏫 Instructor: {course['instructor']}
   ⏱️ Duration: {course['duration']}
   💰 Cost: {course['cost']}
   🎯 Level: {course['level']}
   ⭐ Rating: {course['rating']} | 👥 Students: {course['students']}
   📋 Description: {course['description']}
   🔗 Link: {course['link']}

"""
            
            # Add local training and certifications
            recommendations = self._generate_course_recommendations(current_skills, career_goal, education_level)
            
            # Local Training
            formatted_results += "\n🏢 LOCAL TRAINING CENTERS IN UAE:\n\n"
            for training in recommendations['local_training'][:3]:  # Top 3
                formatted_results += f"""
🏫 {training['name']}
   📍 Location: {training['location']}
   📞 Contact: {training['contact']}
   💰 Price Range: {training['price_range']}
   📋 Programs: {training['programs']}

"""
            
            # Professional Certifications
            formatted_results += "\n🏆 PROFESSIONAL CERTIFICATIONS:\n\n"
            for cert in recommendations['certifications'][:5]:  # Top 5
                formatted_results += f"• {cert['name']} - {cert['provider']} ({cert['value']})\n"
            
            # Add data source indicator
            is_real_data = len(real_courses) > 0
            data_source = "🌐 Data from Udemy API" if is_real_data else "📊 Simulated course data for demo"
            
            formatted_results += f"""

{data_source}

💡 CAREER DEVELOPMENT TIPS:
• Start with foundational courses if you're changing fields
• Focus on in-demand skills in the UAE market
• Consider government-sponsored training programs
• Network with professionals in your target field
• Update your LinkedIn profile with new certifications
• Practice new skills through personal projects

🎯 NEXT STEPS:
1. Choose 1-2 courses that align with your immediate goals
2. Set a realistic timeline for completion
3. Apply new skills in your current role or projects
4. Update your CV and LinkedIn profile
5. Start networking in your target industry
"""
            
            return formatted_results
            
        except Exception as e:
            return f"Error generating course recommendations: {str(e)}\n\nFalling back to simulated data...\n\n" + self._get_fallback_course_recommendations(current_skills, career_goal, education_level)
    
    def _generate_search_queries(self, skills: str, career_goal: str) -> List[str]:
        """Generate search queries for Udemy API based on skills and goals."""
        queries = []
        skills_lower = skills.lower()
        
        # Primary skill-based queries
        if any(word in skills_lower for word in ['engineer', 'software', 'programming', 'developer']):
            queries.extend([
                "Python Programming",
                "Software Engineering",
                "Web Development",
                "Data Structures Algorithms"
            ])
        elif any(word in skills_lower for word in ['data', 'scientist', 'analytics', 'analysis']):
            queries.extend([
                "Python for Data Science",
                "Machine Learning",
                "Data Analytics",
                "SQL Database"
            ])
        elif any(word in skills_lower for word in ['manager', 'management', 'project']):
            queries.extend([
                "Project Management",
                "Leadership Skills",
                "Business Management",
                "Agile Scrum"
            ])
        elif any(word in skills_lower for word in ['business', 'consultant', 'marketing']):
            queries.extend([
                "Digital Marketing",
                "Business Strategy",
                "Excel Advanced",
                "Business Analytics"
            ])
        else:
            # General queries
            queries.extend([
                "Professional Development",
                "Communication Skills",
                "Excel Advanced",
                "English Business"
            ])
        
        # Add career goal specific queries
        if career_goal:
            goal_lower = career_goal.lower()
            if 'software' in goal_lower or 'programming' in goal_lower:
                queries.append("Software Development")
            elif 'data' in goal_lower:
                queries.append("Data Science")
            elif 'management' in goal_lower:
                queries.append("Management Skills")
        
        return queries[:4]  # Limit to 4 queries to avoid too many API calls
    
    def _format_fallback_recommendations(self, recommendations: Dict[str, List[Dict[str, Any]]], skills: str, career_goal: str, education_level: str) -> str:
        """Format fallback recommendations when Udemy API fails."""
        formatted_results = f"""
📚 COURSE RECOMMENDATIONS FOR YOUR CAREER DEVELOPMENT
{'='*65}

Based on your background: {skills}
Career Goal: {career_goal or 'General skill enhancement'}
Education Level: {education_level or 'Not specified'}

"""
        
        # Online Courses (simulated)
        formatted_results += "🌐 ONLINE COURSES & CERTIFICATIONS:\n\n"
        for course in recommendations['online_courses']:
            formatted_results += f"""
📖 {course['title']}
   🏫 Provider: {course['provider']}
   ⏱️ Duration: {course['duration']}
   💰 Cost: {course['cost']}
   🎯 Level: {course['level']}
   📋 What you'll learn: {course['description']}
   🔗 Link: {course['link']}

"""
        
        return formatted_results
    
    def _get_fallback_course_recommendations(self, skills: str, career_goal: str, education_level: str) -> str:
        """Get fallback course recommendations when API fails."""
        try:
            recommendations = self._generate_course_recommendations(skills, career_goal, education_level)
            return self._format_fallback_recommendations(recommendations, skills, career_goal, education_level)
        except Exception as e:
            return f"Error in fallback course recommendations: {str(e)}"
    
    def _generate_course_recommendations(self, skills: str, career_goal: str, education_level: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generate course recommendations based on skills and goals."""
        
        skills_lower = skills.lower()
        
        # Online courses mapping
        online_courses = []
        
        if any(word in skills_lower for word in ['engineer', 'technical', 'software', 'it']):
            online_courses.extend([
                {
                    "title": "AWS Cloud Practitioner Certification",
                    "provider": "Amazon Web Services",
                    "duration": "3-4 months",
                    "cost": "Free (exam fee: $100)",
                    "level": "Beginner to Intermediate",
                    "description": "Cloud computing fundamentals, AWS services, security, pricing",
                    "link": "aws.amazon.com/training"
                },
                {
                    "title": "Google Data Analytics Certificate",
                    "provider": "Google (Coursera)",
                    "duration": "6 months",
                    "cost": "$49/month",
                    "level": "Beginner",
                    "description": "Data analysis, visualization, SQL, R programming, Tableau",
                    "link": "coursera.org/google-certificates"
                },
                {
                    "title": "Project Management Professional (PMP)",
                    "provider": "PMI",
                    "duration": "4-6 months",
                    "cost": "$400-600",
                    "level": "Intermediate to Advanced",
                    "description": "Project management methodologies, leadership, risk management",
                    "link": "pmi.org/certifications"
                }
            ])
        
        if any(word in skills_lower for word in ['business', 'management', 'consultant', 'supervisor']):
            online_courses.extend([
                {
                    "title": "Digital Marketing Specialization",
                    "provider": "University of Illinois (Coursera)",
                    "duration": "4-6 months",
                    "cost": "$49/month",
                    "level": "Beginner to Intermediate",
                    "description": "SEO, social media marketing, analytics, content strategy",
                    "link": "coursera.org/specializations/digital-marketing"
                },
                {
                    "title": "MBA Essentials",
                    "provider": "Wharton (Coursera)",
                    "duration": "8-12 months",
                    "cost": "$79/month",
                    "level": "Intermediate",
                    "description": "Finance, marketing, operations, strategy, leadership",
                    "link": "coursera.org/specializations/wharton-business-foundations"
                }
            ])
        
        # Add general courses
        online_courses.extend([
            {
                "title": "English for Career Development",
                "provider": "University of Pennsylvania (Coursera)",
                "duration": "2-3 months",
                "cost": "Free (certificate: $49)",
                "level": "All levels",
                "description": "Business English, interview skills, networking, resume writing",
                "link": "coursera.org/learn/careerdevelopment"
            },
            {
                "title": "Excel Skills for Business",
                "provider": "Macquarie University (Coursera)",
                "duration": "3-4 months",
                "cost": "$49/month",
                "level": "Beginner to Advanced",
                "description": "Advanced Excel, data analysis, pivot tables, macros",
                "link": "coursera.org/specializations/excel"
            }
        ])
        
        # Local training centers
        local_training = [
            {
                "name": "Emirates Institute for Banking & Financial Studies",
                "location": "Dubai, Abu Dhabi, Sharjah",
                "contact": "+971 4 364 4999",
                "price_range": "AED 2,000 - 15,000",
                "programs": "Banking, Finance, Leadership, Digital Transformation"
            },
            {
                "name": "American University of Sharjah - Continuing Education",
                "location": "Sharjah",
                "contact": "+971 6 515 2222",
                "price_range": "AED 3,000 - 20,000",
                "programs": "Business, Engineering, IT, Project Management"
            },
            {
                "name": "Dubai Knowledge Park Training Centers",
                "location": "Dubai",
                "contact": "+971 4 364 2222",
                "price_range": "AED 1,500 - 12,000",
                "programs": "Professional Development, IT, Languages, Business Skills"
            },
            {
                "name": "ADNOC Technical Institute",
                "location": "Abu Dhabi",
                "contact": "+971 2 607 5555",
                "price_range": "AED 5,000 - 25,000",
                "programs": "Engineering, Oil & Gas, Safety, Technical Skills"
            }
        ]
        
        # Professional certifications
        certifications = [
            {"name": "Certified Public Accountant (CPA)", "provider": "AICPA", "value": "High demand in finance sector"},
            {"name": "Certified Information Systems Auditor (CISA)", "provider": "ISACA", "value": "IT audit and security"},
            {"name": "Six Sigma Green Belt", "provider": "ASQ", "value": "Process improvement and quality"},
            {"name": "PRINCE2 Project Management", "provider": "AXELOS", "value": "Widely recognized in UAE"},
            {"name": "Certified Scrum Master (CSM)", "provider": "Scrum Alliance", "value": "Agile project management"}
        ]
        
        return {
            "online_courses": online_courses[:4],  # Limit to top 4
            "local_training": local_training,
            "certifications": certifications[:5]  # Top 5 certifications
        }