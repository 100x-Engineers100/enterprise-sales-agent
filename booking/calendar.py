import logging
import os
from typing import List, Dict
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

class MeetingBooker:
    def __init__(self):
        self.calendar_api_key = os.getenv("CALENDAR_API_KEY")
        self.supported_calendar_providers = ['google', 'outlook', 'calendly']
        self.default_provider = 'google'
        logger.info("Initialized Meeting Booking System")

    def _validate_calendar_provider(self, provider: str) -> str:
        """Ensure selected calendar provider is supported"""
        if provider not in self.supported_calendar_providers:
            logger.warning(f"Calendar provider {provider} not supported. Defaulting to {self.default_provider}")
            return self.default_provider
        return provider

    def schedule_meeting(self, lead: Dict, provider: str = 'google') -> Dict:
        """Placeholder for calendar integration (Google Calendar, Calendly) to schedule meetings"""
        provider = self._validate_calendar_provider(provider)
        if not self.calendar_api_key:
            logger.warning(f"Skipping meeting scheduling for {lead.get('company_name')} - missing calendar API key")
            return {"scheduled": False, "message": "Missing API key"}

        try:
            # Placeholder: Integrate with calendar API (e.g., Google Calendar API, Calendly API)
            meeting_details = {
                "title": f"Discovery Call with {lead.get('company_name')}",
                "attendees": [lead.get('email')],
                "start_time": "2025-12-10T14:00:00Z",
                "end_time": "2025-12-10T14:30:00Z",
                "provider": provider,
                "meeting_link": "https://calendly.com/sales-team/discovery-call"
            }
            logger.info(f"Scheduled {provider} meeting for {lead.get('contact_name')} at {lead.get('company_name')}")
            return {"scheduled": True, "meeting_details": meeting_details}
        except Exception as e:
            logger.error(f"Failed to schedule meeting: {e}")
            return {"scheduled": False, "message": str(e)}

    def run(self, engaged_leads: List[Dict]) -> List[Dict]:
        """Execute meeting booking for engaged leads"""
        logger.info(f"Starting meeting booking for {len(engaged_leads)} engaged leads")
        booked_leads = []
        for lead in engaged_leads:
            # Only schedule meetings for leads who responded to engagement
            if lead.get("email_sequence_responded") or lead.get("voice_message_responded"):
                meeting_result = self.schedule_meeting(lead)
                lead["meeting_booking"] = meeting_result
            booked_leads.append(lead)

        logger.info(f"Meeting booking complete for {len(booked_leads)} leads")
        return booked_leads