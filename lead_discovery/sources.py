import requests
import os
import logging
from dotenv import load_dotenv
from serpapi import GoogleSearch
import uuid

load_dotenv()
logger = logging.getLogger(__name__)

class LeadDiscoveryEngine:
    def __init__(self):
        # Multi-source API support (follows codebase pattern)
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.tavily_base_url = "https://api.tavily.com/search"
        self.serpapi_api_key = os.getenv("SERPAPI_API_KEY")
        self.company_database_api_key = os.getenv("COMPANY_DATABASE_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.supported_web_search_types = ["company_listings", "intent_signals", "industry_news"]
        self.supported_web_search_sources = ["tavily", "serpapi"]
        self.supported_company_data_sources = ["company_database"]
        self.supported_voice_outreach_voices = ["eleven_monolingual_v1", "eleven_multilingual_v2"]
        if self.tavily_api_key:
            logger.info("Initialized Lead Discovery Engine with Tavily API support")
        else:
            logger.warning("Tavily API key not found - Tavily web search disabled")
        if self.serpapi_api_key:
            logger.info("Initialized Lead Discovery Engine with SERPAPI support")
        else:
            logger.warning("SERPAPI API key not found - SERPAPI web search disabled")
        if self.company_database_api_key:
            logger.info("Initialized Lead Discovery Engine with Company Database API support")
        else:
            logger.warning("Company Database API key not found - bulk company data retrieval disabled")
        if self.elevenlabs_api_key:
            logger.info("Initialized Lead Discovery Engine with ElevenLabs voice outreach support")
        else:
            logger.warning("ElevenLabs API key not found - voice outreach disabled")

    def discover_leads(self, icp_definition):
        leads = []
        # Multi-source lead discovery pipeline (follows codebase pattern)
        # 1. Web Search (Tavily/SerpAPI)
        # 2. Company Databases
        # 3. Job Boards (placeholder)

        logger.info(f"Discovering leads based on ICP: {icp_definition}")
        # Generate targeted search query from ICP (aligned with _generate_icp_search_query logic)
        search_query = self._generate_icp_search_query(icp_definition)

        # Fetch and normalize leads from all active sources
        web_leads = self._search_web(search_query)
        database_leads = self._search_company_database(search_query)
        leads.extend(web_leads + database_leads)

        # Generate voice outreach for normalized leads (Phase 4 integration)
        if self.elevenlabs_api_key:
            for lead in leads:
                voice_outreach = self._generate_voice_outreach(lead)
                if voice_outreach:
                    lead["voice_outreach"] = voice_outreach

        # Generate email and SMS outreach for normalized leads (Phase 4 integration)
        for lead in leads:
            email_outreach = self._generate_email_outreach(lead)
            if email_outreach:
                lead["email_outreach"] = email_outreach
            sms_outreach = self._generate_sms_outreach(lead)
            if sms_outreach:
                lead["sms_outreach"] = sms_outreach

        return leads

    def _generate_icp_search_query(self, icp_definition):
        """Generate targeted search query from ICP data (follows ICPScorer pattern for data parsing)"""
        industry = icp_definition.get("company_characteristics", {}).get("industry_vertical", "B2B companies")
        employee_range = icp_definition.get("company_characteristics", {}).get("company_size", "10-500 employees")
        tech_stack = icp_definition.get("company_characteristics", {}).get("technology_stack", "modern tech stack")
        return f"{industry} companies with {employee_range} using {tech_stack} - lead generation list"

    def _search_web(self, query, search_type="company_listings"):
        """SERPAPI integration for targeted web searches (follows codebase API pattern)"""
        if not self.serpapi_api_key:
            logger.warning("SERPAPI API key missing - cannot perform web search")
            return []

        if search_type not in self.supported_web_search_types:
            logger.warning(f"Unsupported search type {search_type} - defaulting to company_listings")
            search_type = "company_listings"

        try:
            logger.info(f"Performing SERPAPI {search_type} search for: {query}")
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_api_key,
                "engine": "google",
                "num": 10
            })
            results = search.get_dict()
            return self._parse_serpapi_results(results)
        except Exception as e:
            logger.error(f"SERPAPI request failed: {str(e)}")
            return []

    def _parse_serpapi_results(self, results):
        """Parse SERPAPI results into standardized lead format (aligned with Tavily parsing logic)"""
        parsed_leads = []
        if "organic_results" in results:
            for result in results["organic_results"]:
                parsed_leads.append({
                    "company_name": result.get("title", "Unknown Company"),
                    "website": result.get("link", "Unknown URL"),
                    "description": result.get("snippet", "No description available"),
                    "search_rank": result.get("position", 0),
                    "source": "SERPAPI Web Search"
                })
        logger.info(f"Parsed {len(parsed_leads)} leads from SERPAPI results")
        return self._normalize_lead_data(parsed_leads)

    def _search_linkedin(self, query):
        # Placeholder for LinkedIn Sales Navigator integration
        print(f"Searching LinkedIn for: {query}")
        return []

    def _search_company_database(self, query, source="company_database"):
        """Company Database API integration (follows codebase API pattern)"""
        if source not in self.supported_company_data_sources:
            logger.warning(f"Unsupported company data source {source} - defaulting to company_database")
            source = "company_database"

        if not self.company_database_api_key:
            logger.warning("Company Database API key missing - cannot perform bulk company data retrieval")
            return []

        try:
            logger.info(f"Performing bulk company data search for: {query}")
            # Follows codebase API call pattern (Tavily/SERPAPI) - placeholder for actual endpoint
            response = requests.post(
                "https://api.companydatabase.com/v1/search",
                json={
                    "api_key": self.company_database_api_key,
                    "query": query,
                    "result_limit": 20,
                    "include_financials": True,
                    "include_tech_stack": True
                },
                timeout=15
            )
            response.raise_for_status()
            database_results = response.json()
            return self._parse_company_database_results(database_results)
        except requests.exceptions.RequestException as e:
            logger.error(f"Company Database API request failed: {str(e)}")
            return []

    def _parse_company_database_results(self, database_results):
        """Parse company database results into standardized lead format (aligned with web search parsing)"""
        parsed_leads = []
        for result in database_results.get("companies", []):
            parsed_leads.append({
                "company_name": result.get("name", "Unknown Company"),
                "website": result.get("website", "Unknown URL"),
                "industry": result.get("industry", "Inferred from ICP"),
                "employee_count": result.get("employee_count", "Unknown"),
                "revenue_range": result.get("revenue_range", "Unknown"),
                "tech_stack": result.get("tech_stack", []),
                "source": "Company Database API"
            })
        logger.info(f"Parsed {len(parsed_leads)} leads from Company Database results")
        return self._normalize_lead_data(parsed_leads)

    def _normalize_lead_data(self, leads):
        """Normalize multi-source lead data to ICPScorer input format (follows icp/scoring.py criteria)"""
        normalized_leads = []
        for lead in leads:
            # Map lead fields to ICPScorer's 40/30/20/10 weighting categories (icp/scoring.py:12)
            normalized_lead = {
                "id": str(uuid.uuid4()), # Generate a unique ID for the lead
                "company_fit": {
                    "industry_vertical": lead.get("industry", "Unknown"),
                    "company_size": lead.get("employee_count", "Unknown"),
                    "revenue_range": lead.get("revenue_range", "Unknown"),
                    "tech_stack": lead.get("tech_stack", []),
                    "source": lead.get("source", "Unknown")
                },
                "persona_fit": {
                    "decision_maker_available": False,
                    "pain_points_available": False
                },
                "intent_signals": {
                    "search_rank": lead.get("search_rank", 0),
                    "description": lead.get("description", "No intent data available")
                },
                "timing_fit": {
                    "funding_events_available": False
                },
                "raw_lead_data": lead
            }
            normalized_leads.append(normalized_lead)
        logger.info(f"Normalized {len(normalized_leads)} leads for ICPScorer compatibility")
        return normalized_leads

    def _search_job_boards(self, query):
        # Placeholder for job board integration
        print(f"Searching job boards for: {query}")
        return []

    def _generate_voice_outreach(self, normalized_lead, voice_id="eleven_monolingual_v1"):
        """ElevenLabs voice outreach integration (follows codebase API pattern)"""
        if not self.elevenlabs_api_key:
            logger.warning("ElevenLabs API key missing - cannot generate voice outreach")
            return None

        if voice_id not in self.supported_voice_outreach_voices:
            logger.warning(f"Unsupported voice ID {voice_id} - defaulting to eleven_monolingual_v1")
            voice_id = "eleven_monolingual_v1"

        try:
            # Reuse existing elevenlabs library from requirements.txt (elevenlabs>=0.30.0)
            from elevenlabs import generate, set_api_key
            set_api_key(self.elevenlabs_api_key)

            # Tie script to ICP criteria (aligned with icp/wizard.py templates)
            outreach_script = f"""Hi, this is from the enterprise sales team. We noticed {normalized_lead['company_fit']['company_name']} operates in the {normalized_lead['company_fit']['industry_vertical']} space with {normalized_lead['company_fit']['company_size']} employees.
We have solutions to address common pain points like regulatory compliance and legacy system integration.
Would you be open to a 15-minute call next week to discuss?"""

            logger.info(f"Generating voice outreach for {normalized_lead['company_fit']['company_name']}")
            audio = generate(
                text=outreach_script,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            return {"audio_data": audio, "script": outreach_script, "lead_id": normalized_lead['raw_lead_data']['website']}
        except Exception as e:
            logger.error(f"ElevenLabs voice generation failed: {str(e)}")
            return None

    def _generate_email_outreach(self, normalized_lead):
        """Personalized email template tied to ICP criteria (icp/wizard.py pain points)"""
        # Reuse ICP pain points from Healthcare Tech/FinTech templates (icp/wizard.py:170+)
        pain_points = {"Healthcare Technology": "interoperability challenges and HIPAA compliance", "Financial Technology": "regulatory burden and fraud detection"}
        target_pain_point = pain_points.get(normalized_lead['company_fit']['industry_vertical'], "core operational challenges")

        return f"""Subject: Solutions for {normalized_lead['company_fit']['industry_vertical']} Companies

Hi [Decision Maker],

I noticed {normalized_lead['company_fit']['company_name']} operates in the {normalized_lead['company_fit']['industry_vertical']} space with {normalized_lead['company_fit']['company_size']} employees.

Many companies in your sector struggle with {target_pain_point}—our solutions are designed to address these exact challenges.

Would you be open to a 15-minute call next week to discuss how we can help?

Best regards,
Enterprise Sales Team"""

    def _generate_sms_outreach(self, normalized_lead):
        """Concise SMS template tied to ICP intent signals"""
        return f"Hi, this is from the enterprise sales team. We have solutions for {normalized_lead['company_fit']['industry_vertical']} companies like {normalized_lead['company_fit']['company_name']}. Can we chat briefly next week? Reply 'yes' for details."""

    def run(self):
        print("\n--- Lead Discovery Engine ---")
        print("Starting lead discovery...")
        # In a real scenario, ICP would be passed from ICPWizard
        dummy_icp = {"industry": "B2B SaaS", "employee_count_range": "50-200"}
        leads = self.discover_leads(dummy_icp)
        print(f"Discovered {len(leads)} leads.")
        return leads
