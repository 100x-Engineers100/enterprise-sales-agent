import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class LearningEngine:
    def __init__(self):
        self.crm_outcomes = []
        logger.info("Initialized Learning Engine")

    def record_crm_outcome(self, lead: Dict, crm_result: Dict):
        """Records the outcome of a CRM deal creation for a lead."""
        outcome = {
            "lead_id": lead.get("id"), # Assuming leads have a unique ID
            "initial_icp_score": lead.get("icp_score"),
            "crm_deal_created": crm_result.get("deal_created"),
            "deal_details": crm_result.get("deal_details"),
            "deal_link": crm_result.get("deal_link"),
            "lead_data": lead # Store full lead data for later analysis
        }
        self.crm_outcomes.append(outcome)
        logger.info(f"Recorded CRM outcome for lead {lead.get("id")}: Deal Created = {crm_result.get("deal_created")}")

    def analyze_outcomes(self):
        """Analyzes recorded CRM outcomes to provide insights and suggestions for ICP refinement."""
        if not self.crm_outcomes:
            logger.info("No CRM outcomes recorded yet for analysis.")
            return {"insights": "No data to analyze.", "suggestions": []}

        successful_deals = [o for o in self.crm_outcomes if o.get("crm_deal_created")]
        failed_deals = [o for o in self.crm_outcomes if not o.get("crm_deal_created")]

        insights = {
            "total_outcomes": len(self.crm_outcomes),
            "successful_deals": len(successful_deals),
            "failed_deals": len(failed_deals),
            "success_rate": (len(successful_deals) / len(self.crm_outcomes)) * 100 if self.crm_outcomes else 0
        }

        suggestions = self._generate_suggestions(successful_deals, failed_deals)

        return {"insights": insights, "suggestions": suggestions}

    def _generate_suggestions(self, successful_deals: List[Dict], failed_deals: List[Dict]) -> List[str]:
        """Generates suggestions for ICP refinement based on successful and failed deals."""
        suggestions = []

        # Example: Analyze common characteristics of successful deals
        if successful_deals:
            # Placeholder for more sophisticated analysis
            avg_success_score = sum([o.get("initial_icp_score", 0) for o in successful_deals]) / len(successful_deals)
            suggestions.append(f"Average ICP score for successful deals: {avg_success_score:.2f}")
            # Further analysis could involve looking at common industries, company sizes, etc.

        if failed_deals:
            # Placeholder for more sophisticated analysis
            avg_fail_score = sum([o.get("initial_icp_score", 0) for o in failed_deals]) / len(failed_deals)
            suggestions.append(f"Average ICP score for failed deals: {avg_fail_score:.2f}")
            # Further analysis could involve identifying common pain points or missing criteria in failed leads

        if successful_deals and failed_deals:
            if avg_success_score > avg_fail_score * 1.2: # Arbitrary threshold for suggestion
                suggestions.append("Successful deals generally have higher ICP scores. Consider refining ICP to prioritize leads with higher scores.")
            elif avg_fail_score > avg_success_score * 1.2:
                suggestions.append("Failed deals sometimes have higher ICP scores. Review ICP criteria for potential misalignments or missing factors.")

        # More advanced suggestions would involve machine learning to find correlations
        # For now, these are rule-based and illustrative.
        return suggestions

    def run(self, crm_outcomes: List[Dict]):
        """Main entry point for the learning engine to process outcomes and provide feedback."""
        for outcome in crm_outcomes:
            self.crm_outcomes.append(outcome)
        
        analysis_results = self.analyze_outcomes()
        logger.info("Learning Engine Analysis Complete.")
        logger.info(f"Insights: {analysis_results["insights"]}")
        for suggestion in analysis_results["suggestions"]:
            logger.info(f"Suggestion: {suggestion}")
        return analysis_results
