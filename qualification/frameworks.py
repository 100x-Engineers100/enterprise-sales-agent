import logging

logger = logging.getLogger(__name__)

class QualificationManager:
    def __init__(self, active_framework='BANT'):
        self.supported_frameworks = ['BANT', 'MEDDIC', 'CHAMP', 'Custom']
        self.active_framework = self._validate_framework(active_framework)
        logger.info(f"Initialized Qualification Manager with active framework: {self.active_framework}")

    def _validate_framework(self, framework):
        """Ensure selected framework is supported"""
        if framework not in self.supported_frameworks:
            logger.warning(f"Framework {framework} not supported. Defaulting to BANT")
            return 'BANT'
        return framework

    def set_framework(self, framework):
        """Allow dynamic framework selection"""
        self.active_framework = self._validate_framework(framework)
        logger.info(f"Switched to qualification framework: {self.active_framework}")

    def _qualify_with_bant(self, lead):
        """BANT Framework: Budget, Authority, Need, Timeline"""
        bant_score = 0
        # Budget check (30% weight)
        if lead.get('budget_indicated'):
            bant_score += 30
        # Authority check (30% weight)
        if lead.get('contact_authority') in ['Decision Maker', 'Influencer']:
            bant_score += 30
        # Need check (25% weight)
        if lead.get('identified_need'):
            bant_score += 25
        # Timeline check (15% weight)
        if lead.get('purchase_timeline') in ['0-3 months', '3-6 months']:
            bant_score += 15
        lead['qualification_score'] = bant_score
        lead['qualified'] = bant_score >= 70
        return lead

    def _qualify_with_meddic(self, lead):
        """MEDDIC Framework: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion"""
        meddic_score = 0
        # Metrics check (20% weight)
        if lead.get('business_metrics'):
            meddic_score += 20
        # Economic Buyer check (20% weight)
        if lead.get('contact_role') == 'Economic Buyer':
            meddic_score += 20
        # Decision Criteria check (15% weight)
        if lead.get('decision_criteria'):
            meddic_score += 15
        # Decision Process check (15% weight)
        if lead.get('decision_process'):
            meddic_score += 15
        # Pain check (15% weight)
        if lead.get('identified_pain'):
            meddic_score += 15
        # Champion check (15% weight)
        if lead.get('internal_champion'):
            meddic_score += 15
        lead['qualification_score'] = meddic_score
        lead['qualified'] = meddic_score >= 80
        return lead

    def _qualify_with_champ(self, lead):
        """CHAMP Framework: Challenges, Authority, Money, Prioritization"""
        champ_score = 0
        # Challenges check (30% weight)
        if lead.get('identified_challenges'):
            champ_score += 30
        # Authority check (30% weight)
        if lead.get('contact_authority') == 'Decision Maker':
            champ_score += 30
        # Money check (25% weight)
        if lead.get('budget_approved'):
            champ_score += 25
        # Prioritization check (15% weight)
        if lead.get('initiative_priority') == 'High':
            champ_score += 15
        lead['qualification_score'] = champ_score
        lead['qualified'] = champ_score >= 75
        return lead

    def _qualify_with_custom(self, lead):
        """Custom Framework: Placeholder for user-defined criteria"""
        # Will be extended with user-configurable rules in later iterations
        lead['qualification_score'] = 0
        lead['qualified'] = False
        logger.warning("Custom framework not yet implemented. Lead marked as unqualified")
        return lead

    def run(self, processed_leads):
        """Execute qualification using active framework on processed leads"""
        logger.info(f"Starting qualification for {len(processed_leads)} scored leads with {self.active_framework} framework")
        qualified_leads = []
        for lead in processed_leads:
            if self.active_framework == 'BANT':
                qualified_lead = self._qualify_with_bant(lead)
            elif self.active_framework == 'MEDDIC':
                qualified_lead = self._qualify_with_meddic(lead)
            elif self.active_framework == 'CHAMP':
                qualified_lead = self._qualify_with_champ(lead)
            elif self.active_framework == 'Custom':
                qualified_lead = self._qualify_with_custom(lead)
            qualified_leads.append(qualified_lead)
        # Filter qualified leads for downstream engagement
        filtered_leads = [lead for lead in qualified_leads if lead['qualified']]
        logger.info(f"Qualification complete: {len(filtered_leads)} of {len(processed_leads)} leads qualified")
        return filtered_leads