import logging
from typing import Dict, List
from collections import Counter

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

        # Analyze common characteristics of successful deals
        if successful_deals:
            successful_industries = Counter([
                deal["lead_data"].get("company_fit", {}).get("industry")
                for deal in successful_deals
                if deal["lead_data"].get("company_fit", {}).get("industry")
            ])
            if successful_industries:
                most_common_successful_industry = successful_industries.most_common(1)[0][0]
                suggestions.append(f"Most common industry in successful deals: {most_common_successful_industry}. Consider prioritizing leads from this industry.")

            # Analyze company size (revenue range)
            successful_revenue_ranges = [
                deal["lead_data"].get("financials", {}).get("revenue_range")
                for deal in successful_deals
                if deal["lead_data"].get("financials", {}).get("revenue_range")
            ]
            if successful_revenue_ranges:
                # Simple aggregation for now, more advanced would involve parsing ranges
                suggestions.append(f"Common revenue ranges in successful deals: {', '.join(list(set(successful_revenue_ranges)))}. Refine ICP to target these ranges.")

            # Analyze pain points (if available)
            successful_pain_points = Counter()
            for deal in successful_deals:
                pain_points = deal["lead_data"].get("pain_points")
                if pain_points and isinstance(pain_points, list):
                    successful_pain_points.update(pain_points)
            if successful_pain_points:
                most_common_successful_pain_point = successful_pain_points.most_common(1)[0][0]
                suggestions.append(f"Most common pain point in successful deals: '{most_common_successful_pain_point}'. Emphasize solutions for this pain point in outreach.")

        # Analyze common characteristics of failed deals
        if failed_deals:
            failed_industries = Counter([
                deal["lead_data"].get("company_fit", {}).get("industry")
                for deal in failed_deals
                if deal["lead_data"].get("company_fit", {}).get("industry")
            ])
            if failed_industries:
                most_common_failed_industry = failed_industries.most_common(1)[0][0]
                suggestions.append(f"Most common industry in failed deals: {most_common_failed_industry}. Consider de-prioritizing leads from this industry or re-evaluating your approach.")

            failed_pain_points = Counter()
            for deal in failed_deals:
                pain_points = deal["lead_data"].get("pain_points")
                if pain_points and isinstance(pain_points, list):
                    failed_pain_points.update(pain_points)
            if failed_pain_points:
                most_common_failed_pain_point = failed_pain_points.most_common(1)[0][0]
                suggestions.append(f"Most common pain point in failed deals: '{most_common_failed_pain_point}'. Review if your solution effectively addresses this, or if these leads are a poor fit.")

        # Compare successful and failed deals for more nuanced suggestions
        if successful_deals and failed_deals:
            avg_success_score = sum([o.get("initial_icp_score", 0) for o in successful_deals]) / len(successful_deals)
            avg_fail_score = sum([o.get("initial_icp_score", 0) for o in failed_deals]) / len(failed_deals)

            if avg_success_score > avg_fail_score * 1.1: # A slightly more robust threshold
                suggestions.append("Successful deals generally have significantly higher ICP scores. Focus on refining ICP criteria to better identify high-scoring leads.")
            elif avg_fail_score > avg_success_score * 1.1:
                suggestions.append("Some failed deals have high ICP scores. This suggests a potential mismatch between your ICP criteria and actual deal success. Re-evaluate your ICP scoring weights or criteria.")

        if not suggestions:
            suggestions.append("No specific patterns detected yet. Continue gathering more CRM outcome data for better insights.")

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
