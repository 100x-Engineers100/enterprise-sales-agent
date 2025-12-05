import os
import logging
from dotenv import load_dotenv
from icp.wizard import ICPWizard
from icp.scoring import ICPScorer
from lead_discovery.sources import LeadDiscoveryEngine
from lead_discovery.data_processor import LeadDataProcessor
from pre_qualification.research_engine import ResearchEngine
from qualification.frameworks import QualificationManager
from engagement.orchestrator import EngagementOrchestrator
from booking.calendar import MeetingBooker
from handoff.crm import CRMHandler
from learning.engine import LearningEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnterpriseSalesAgent:
    def __init__(self):
        self.icp_wizard = ICPWizard()
        self.lead_discovery = LeadDiscoveryEngine()
        self.lead_data_processor = LeadDataProcessor()
        self.pre_qual_research = ResearchEngine()
        self.icp_scorer = None
        self.qualification_manager = QualificationManager()
        self.engagement_orchestrator = EngagementOrchestrator()
        self.meeting_booker = MeetingBooker()
        self.learning_engine = LearningEngine()
        self.crm_handler = CRMHandler(self.learning_engine)
        self.current_stage = "icp_definition"
        self.icp_definition = None
        self.processed_leads = None
        self.researched_leads = None
        self.qualified_leads = None
        self.engaged_leads = None
        self.booked_leads = None

    def run_workflow(self):
        """Execute the full enterprise sales agent workflow"""
        logger.info("Starting Enterprise Sales Agent workflow")
        while self.current_stage:
            if self.current_stage == "icp_definition":
                self.icp_definition = self.icp_wizard.run()
                self.icp_scorer = ICPScorer(self.icp_definition)
                logger.info(f"Initialized ICP Scorer with definition: {self.icp_definition}")
                self.current_stage = "lead_discovery"
            elif self.current_stage == "lead_discovery":
                raw_leads = self.lead_discovery.run()
                logger.info(f"Discovered {len(raw_leads)} raw leads")
                self.processed_leads = self.lead_data_processor.run(raw_leads)
                logger.info(f"Processed {len(self.processed_leads)} leads")
                # Score and categorize leads
                for lead in self.processed_leads:
                    lead["icp_score"] = self.icp_scorer.score_lead(lead)
                    lead["lead_bucket"] = self.icp_scorer.categorize_lead(lead["icp_score"])
                logger.info(f"Scored and categorized {len(self.processed_leads)} leads")
                self.current_stage = "pre_qualification_research"
            elif self.current_stage == "pre_qualification_research":
                self.researched_leads = self.pre_qual_research.run(self.processed_leads)
                logger.info(f"Enriched {len(self.researched_leads)} leads with pre-qualification data")
                self.current_stage = "qualification"
            elif self.current_stage == "qualification":
                self.qualified_leads = self.qualification_manager.run(self.researched_leads)
                logger.info(f"Filtered to {len(self.qualified_leads)} qualified leads")
                self.current_stage = "engagement"
            elif self.current_stage == "engagement":
                self.engaged_leads = self.engagement_orchestrator.run(self.qualified_leads)
                logger.info(f"Engaged with {len(self.engaged_leads)} qualified leads")
                self.current_stage = "booking"
            elif self.current_stage == "booking":
                self.booked_leads = self.meeting_booker.run(self.engaged_leads)
                logger.info(f"Processed meeting booking for {len(self.booked_leads)} engaged leads")
                self.current_stage = "handoff"
            elif self.current_stage == "handoff":
                self.crm_handler.run(self.booked_leads)
                logger.info(f"Completed CRM handoff for {len(self.booked_leads)} booked leads")
                self.current_stage = None
        logger.info("Enterprise Sales Agent workflow completed")

if __name__ == "__main__":
    agent = EnterpriseSalesAgent()
    agent.run_workflow()
