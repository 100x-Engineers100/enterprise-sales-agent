from datetime import datetime, timedelta
import logging
import os
from typing import List, Dict
from dotenv import load_dotenv
import requests
from simple_salesforce import Salesforce

logger = logging.getLogger(__name__)
load_dotenv()

class CRMHandler:
    def __init__(self, learning_engine=None):
        self.crm_api_key = os.getenv("CRM_API_KEY")
        self.salesforce_username = os.getenv("SALESFORCE_USERNAME")
        self.salesforce_password = os.getenv("SALESFORCE_PASSWORD")
        self.salesforce_security_token = os.getenv("SALESFORCE_SECURITY_TOKEN")
        self.salesforce_instance_url = os.getenv("SALESFORCE_INSTANCE_URL")
        self.learning_engine = learning_engine
        self.supported_crm_providers = ['salesforce', 'hubspot', 'pipedrive']
        self.default_provider = 'salesforce'
        logger.info("Initialized CRM Handoff System")

    def _validate_crm_provider(self, provider: str) -> str:
        """Ensure selected CRM provider is supported"""
        if provider not in self.supported_crm_providers:
            logger.warning(f"CRM provider {provider} not supported. Defaulting to {self.default_provider}")
            return self.default_provider
        return provider

    def create_crm_deal(self, lead: Dict, provider: str = 'salesforce') -> Dict:
        """Create a CRM deal based on the specified provider."""
        provider = self._validate_crm_provider(provider)
        if not self.crm_api_key:
            logger.warning(f"Skipping CRM deal creation for {lead.get('company_name')} - missing CRM API key")
            return {"deal_created": False, "message": "Missing API key"}

        if provider == 'salesforce':
            return self._create_salesforce_deal(lead)
        elif provider == 'hubspot':
            return self._create_hubspot_deal(lead)
        else:
            logger.error(f"Unsupported CRM provider: {provider}")
            return {"deal_created": False, "message": f"Unsupported CRM provider: {provider}"}

    def _create_salesforce_deal(self, lead: Dict) -> Dict:
        """Salesforce API integration for creating deals/opportunities using simple_salesforce."""
        logger.info(f"Attempting to create Salesforce deal for {lead.get('company_name')}")

        try:
            # Authenticate with Salesforce
            sf = Salesforce(username=self.salesforce_username,
                            password=self.salesforce_password,
                            security_token=self.salesforce_security_token,
                            instance_url=self.salesforce_instance_url)

            # Constructing the payload for a Salesforce Opportunity
            deal_properties = {
                "Name": f"Discovery Call - {lead.get('company_name')}",
                "StageName": "Prospecting",  # Or another appropriate stage like 'Qualification'
                "CloseDate": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"), # Assuming a close date 30 days from now
                "Amount": float(str(lead.get('financials', {}).get('revenue_range', '0')).replace('-', '').split(' ')[0]) if str(lead.get('financials', {}).get('revenue_range', '0')).replace('-', '').split(' ')[0].isdigit() else 0.0,
                "LeadSource": "Enterprise Sales Agent",
                # Add other relevant fields from the lead data to Salesforce Opportunity fields
                # e.g., "Description": f"Lead from {lead.get('email')} at {lead.get('company_name')}",
                # "AccountId": lead.get('company_fit', {}).get('salesforce_account_id'), # If you have Salesforce Account ID
            }

            # Filter out None values from deal_properties
            deal_properties = {k: v for k, v in deal_properties.items() if v is not None}

            # Create the Opportunity
            sf_response = sf.Opportunity.create(deal_properties)
            
            deal_id = sf_response.get('id')
            deal_link = f"{os.getenv("SALESFORCE_INSTANCE_URL")}/{deal_id}" if deal_id else "N/A"

            logger.info(f"Successfully created Salesforce deal for {lead.get('contact_name')} at {lead.get('company_name')}")
            return {"deal_created": True, "deal_details": sf_response, "deal_link": deal_link}
        except Exception as e:
            logger.error(f"Failed to create Salesforce deal: {str(e)}")
            return {"deal_created": False, "message": str(e)}

    def _create_hubspot_deal(self, lead: Dict) -> Dict:
        """HubSpot API integration for creating deals."""
        logger.info(f"Attempting to create HubSpot deal for {lead.get('company_name')}")
        hubspot_api_url = "https://api.hubapi.com/crm/v3/objects/deals"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.crm_api_key}"
        }

        deal_properties = {
            "dealname": f"Discovery Call - {lead.get('company_name')}",
            "dealstage": "appointmentscheduled",  # Or another appropriate stage
            "pipeline": "default",  # Assuming a default pipeline
            "amount": str(lead.get('financials', {}).get('revenue_range', '0')).replace('-', '').split(' ')[0], # Extracting a numeric value from revenue range
            "hs_company_id": lead.get('company_fit', {}).get('company_id', None), # Assuming company_id is available
            "hs_contact_id": lead.get('persona_fit', {}).get('contact_id', None), # Assuming contact_id is available
            "lead_source": "Enterprise Sales Agent",
            "contact_email": lead.get('email'),
        }

        # Filter out None values from deal_properties
        deal_properties = {k: v for k, v in deal_properties.items() if v is not None}

        payload = {"properties": deal_properties}

        try:
            response = requests.post(hubspot_api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()  # Raise an exception for HTTP errors
            hubspot_deal = response.json()
            deal_link = f"https://app.hubspot.com/deals/{hubspot_deal.get('portalId', 'unknown')}/deal/{hubspot_deal.get('id')}"

            logger.info(f"Successfully created HubSpot deal for {lead.get('contact_name')} at {lead.get('company_name')}")
            return {"deal_created": True, "deal_details": hubspot_deal, "deal_link": deal_link}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create HubSpot deal: {str(e)}")
            return {"deal_created": False, "message": str(e)}

    def run(self, booked_leads: List[Dict]) -> List[Dict]:
        """Execute CRM handoff for booked leads"""
        logger.info(f"Starting CRM handoff for {len(booked_leads)} booked leads")
        handed_off_leads = []
        for lead in booked_leads:
            # Only create CRM deals for successfully booked leads
            if lead.get("meeting_booking", {}).get("scheduled"):
                deal_result = self.create_crm_deal(lead)
                lead["crm_deal"] = deal_result
                if self.learning_engine:
                    self.learning_engine.record_crm_outcome(lead, deal_result)
            handed_off_leads.append(lead)

        logger.info(f"CRM handoff complete for {len(handed_off_leads)} leads")
        return handed_off_leads