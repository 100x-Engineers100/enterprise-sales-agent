import logging
import os
from typing import List, Dict
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, Voice, VoiceSettings

logger = logging.getLogger(__name__)
load_dotenv()

class EngagementOrchestrator:
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key) if self.elevenlabs_api_key else None
        self.supported_engagement_channels = ['email', 'voice']
        self.email_sequence_templates = {
            'hot_lead': [
                {"subject": "Custom Solution for Your Growth Goals", "delay_hours": 0},
                {"subject": "Follow-Up: Your Recent Platform Launch", "delay_hours": 24},
                {"subject": "Quick Question About Your Tech Stack", "delay_hours": 48}
            ],
            'warm_lead': [
                {"subject": "Resource for B2B SaaS Scaling", "delay_hours": 0},
                {"subject": "Follow-Up: Your Team's Hiring Needs", "delay_hours": 72}
            ]
        }
        logger.info("Initialized Multi-Channel Engagement Orchestrator")

    def _create_email_sequence(self, lead: Dict) -> List[Dict]:
        """Build personalized email sequence based on lead bucket"""
        bucket = lead.get("lead_bucket", "warm")
        template = self.email_sequence_templates.get(bucket, self.email_sequence_templates["warm_lead"])
        # Personalize templates with lead data
        personalized_sequence = [
            {
                "subject": msg["subject"].replace("Your", lead.get("company_name", "Your")),
                "body": f"Hi {lead.get('contact_name', 'Team')},\n\nI noticed your company {lead.get('company_name')} {lead.get('recent_news', [{}])[0].get('headline', 'has exciting updates')}. Let's connect to discuss how we can help.\n\nBest regards,\nThe Sales Team",
                "delay_hours": msg["delay_hours"]
            } for msg in template
        ]
        return personalized_sequence

    def _send_voice_message(self, lead: Dict) -> bool:
        """Send personalized voice message using ElevenLabs API"""
        if not self.elevenlabs_client or not lead.get("contact_phone"):
            logger.warning(f"Skipping voice message for {lead.get('company_name')} - missing API key or phone number")
            return False
        try:
            voice = Voice(
                voice_id="21m00Tcm4TlvDq8ikWAM", # Default voice (Rachel)
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            )
            audio = self.elevenlabs_client.generate(
                text=f"Hi {lead.get('contact_name')}, this is the Sales Team. We noticed your company {lead.get('company_name')} recently launched a new platform. We have a custom solution that can help you scale. Please give us a call back at your convenience.",
                voice=voice,
                model="eleven_multilingual_v2"
            )
            # Placeholder: Integrate with voice calling API to deliver audio (e.g., Twilio)
            logger.info(f"Generated voice message for {lead.get('contact_name')} at {lead.get('company_name')}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate voice message: {e}")
            return False

    def run(self, qualified_leads: List[Dict]) -> List[Dict]:
        """Execute multi-channel engagement on qualified leads (email sequences + voice agent)"""
        logger.info(f"Starting engagement for {len(qualified_leads)} qualified leads")
        engaged_leads = []
        for lead in qualified_leads:
            # Build and schedule email sequence
            lead["email_sequence"] = self._create_email_sequence(lead)
            logger.info(f"Scheduled {len(lead['email_sequence'])} email(s) for {lead.get('company_name')}")

            # Trigger voice message for hot leads only
            if lead.get("lead_bucket") == "hot":
                voice_success = self._send_voice_message(lead)
                lead["voice_message_sent"] = voice_success

            engaged_leads.append(lead)

        logger.info(f"Multi-channel engagement complete for {len(engaged_leads)} leads")
        return engaged_leads