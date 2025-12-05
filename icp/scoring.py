import json
import re

class ICPScorer:
    def __init__(self, icp_definition):
        self.raw_icp_definition = icp_definition
        self.parsed_icp = self._parse_icp_definition(icp_definition)

    def _parse_icp_definition(self, icp_definition):
        parsed = {
            "company_characteristics": {},
            "buyer_persona": {},
            "engagement_signals": {}
        }

        # Company Characteristics
        cc = icp_definition.get("company_characteristics", {})
        parsed["company_characteristics"]["industry_vertical"] = [i.strip().lower() for i in re.split(r'[,/]', cc.get("industry_vertical", "")) if i.strip()]

        company_size_str = cc.get("company_size", "")
        employee_match = re.search(r'(\d+)-(\d+)\s*employees', company_size_str, re.IGNORECASE)
        revenue_match = re.search(r'\$(\d+)[MKB]?-\$(?:(\d+)[MKB]?)?\s*revenue', company_size_str, re.IGNORECASE)
        
        employee_min, employee_max = None, None
        if employee_match:
            employee_min = int(employee_match.group(1))
            employee_max = int(employee_match.group(2))
        parsed["company_characteristics"]["employee_count_range"] = {"min": employee_min, "max": employee_max}

        revenue_min, revenue_max = None, None
        if revenue_match:
            revenue_min = int(revenue_match.group(1)) * (10**6 if 'M' in revenue_match.group(0) else 10**3 if 'K' in revenue_match.group(0) else 1)
            if revenue_match.group(2):
                revenue_max = int(revenue_match.group(2)) * (10**6 if 'M' in revenue_match.group(0) else 10**3 if 'K' in revenue_match.group(0) else 1)
        parsed["company_characteristics"]["revenue_range"] = {"min": revenue_min, "max": revenue_max}

        parsed["company_characteristics"]["geography"] = [g.strip().lower() for g in re.split(r'[,/]', cc.get("geography", "")) if g.strip()]
        parsed["company_characteristics"]["technology_stack"] = [t.strip().lower() for t in re.split(r'[,/]', cc.get("technology_stack", "")) if t.strip()]
        parsed["company_characteristics"]["business_model"] = [b.strip().lower() for b in re.split(r'[,/]', cc.get("business_model", "")) if b.strip()]
        parsed["company_characteristics"]["funding_growth"] = [f.strip().lower() for f in re.split(r'[,/]', cc.get("funding_growth", "")) if f.strip()]

        # Buyer Persona
        bp = icp_definition.get("buyer_persona", {})
        parsed["buyer_persona"]["decision_maker_profile"] = [d.strip().lower() for d in re.split(r'[,/]', bp.get("decision_maker_profile", "")) if d.strip()]
        parsed["buyer_persona"]["pain_points"] = [p.strip().lower() for p in re.split(r'[,/]', bp.get("pain_points", "")) if p.strip()]
        parsed["buyer_persona"]["buying_behavior"] = [b.strip().lower() for b in re.split(r'[,/]', bp.get("buying_behavior", "")) if b.strip()]

        # Engagement Signals
        es = icp_definition.get("engagement_signals", {})
        parsed["engagement_signals"]["intent_signals"] = [i.strip().lower() for i in re.split(r'[,/]', es.get("intent_signals", "")) if i.strip()]
        parsed["engagement_signals"]["content_engagement"] = [c.strip().lower() for c in re.split(r'[,/]', es.get("content_engagement", "")) if c.strip()]

        return parsed

    def score_lead(self, lead_data):
        company_fit_score = self._calculate_company_fit(lead_data)
        persona_fit_score = self._calculate_persona_fit(lead_data)
        intent_signal_score = self._calculate_intent_signal_score(lead_data)
        timing_score = self._calculate_timing_score(lead_data)

        # Normalize scores to 0-100 if they exceed 100, though individual criteria sum to 100
        company_fit_score = min(100, company_fit_score)
        persona_fit_score = min(100, persona_fit_score)
        intent_signal_score = min(100, intent_signal_score)
        timing_score = min(100, timing_score)

        total_icp_score = (
            company_fit_score * 0.4 +
            persona_fit_score * 0.3 +
            intent_signal_score * 0.2 +
            timing_score * 0.1
        )
        return round(total_icp_score, 2)

    def _calculate_company_fit(self, lead_data):
        score = 0
        icp_cc = self.parsed_icp["company_characteristics"]
        lead_company = lead_data.get("company", {})

        # Industry match: 25 points
        lead_industry = lead_company.get("industry", "").lower()
        if lead_industry and any(i in lead_industry for i in icp_cc["industry_vertical"]):
            score += 25

        # Size match: 20 points (employee count and revenue range)
        lead_employee_count = lead_company.get("employee_count")
        icp_emp_range = icp_cc["employee_count_range"]
        if lead_employee_count and icp_emp_range["min"] is not None and icp_emp_range["max"] is not None:
            if icp_emp_range["min"] <= lead_employee_count <= icp_emp_range["max"]:
                score += 10 # Half for employee count

        lead_revenue = lead_company.get("revenue_estimate")
        icp_rev_range = icp_cc["revenue_range"]
        if lead_revenue and icp_rev_range["min"] is not None and icp_rev_range["max"] is not None:
            if icp_rev_range["min"] <= lead_revenue <= icp_rev_range["max"]:
                score += 10 # Half for revenue

        # Geography match: 15 points
        lead_geography = lead_company.get("geography", "").lower()
        if lead_geography and any(g in lead_geography for g in icp_cc["geography"]):
            score += 15

        # Tech stack match: 20 points
        lead_tech_stack = [t.lower() for t in lead_company.get("tech_stack", [])]
        if lead_tech_stack and any(t in lead_tech_stack for t in icp_cc["technology_stack"]):
            score += 20

        # Growth indicators: 20 points (simplified for now, based on presence of any indicator)
        lead_growth_indicators = [g.lower() for g in lead_company.get("growth_indicators", [])]
        if lead_growth_indicators and any(g in lead_growth_indicators for g in icp_cc["funding_growth"]):
            score += 20

        return score

    def _calculate_persona_fit(self, lead_data):
        score = 0
        icp_bp = self.parsed_icp["buyer_persona"]
        lead_contact = lead_data.get("contact", {})

        # Title match: 30 points
        lead_title = lead_contact.get("title", "").lower()
        if lead_title and any(t in lead_title for t in icp_bp["decision_maker_profile"]):
            score += 30

        # Seniority match: 25 points (simplified, assuming seniority is part of decision_maker_profile string)
        lead_seniority = lead_contact.get("seniority", "").lower()
        if lead_seniority and any(s in lead_seniority for s in icp_bp["decision_maker_profile"]):
            score += 25

        # Department match: 25 points
        lead_department = lead_contact.get("department", "").lower()
        if lead_department and any(d in lead_department for d in icp_bp["decision_maker_profile"]):
            score += 25

        # Authority level: 20 points (simplified, assuming authority is part of buying_behavior string)
        lead_authority = lead_contact.get("authority_level", "").lower()
        if lead_authority and any(a in lead_authority for a in icp_bp["buying_behavior"]):
            score += 20

        return score

    def _calculate_intent_signal_score(self, lead_data):
        score = 0
        icp_es = self.parsed_icp["engagement_signals"]
        lead_signals = lead_data.get("signals", {})

        # Recent funding: 30 points
        if lead_signals.get("recent_funding") and "funding announcements" in icp_es["intent_signals"]:
            score += 30

        # Hiring for relevant roles: 25 points
        if lead_signals.get("hiring_relevant_roles") and "job postings" in icp_es["intent_signals"]:
            score += 25

        # Tech stack changes: 20 points
        if lead_signals.get("tech_stack_changes") and "technology changes" in icp_es["intent_signals"]:
            score += 20

        # Competitor mentions: 15 points
        if lead_signals.get("competitor_mentions") and "competitive wins/losses" in icp_es["intent_signals"]:
            score += 15

        # Product launches: 10 points
        if lead_signals.get("product_launches") and "product launches" in icp_es["intent_signals"]:
            score += 10

        return score

    def _calculate_timing_score(self, lead_data):
        score = 0
        # ICP definition doesn't explicitly define timing criteria for scoring, so we'll use general indicators
        # Fiscal calendar alignment: 30 points
        if lead_data.get("timing", {}).get("fiscal_calendar_alignment"):
            score += 30

        # Recent trigger events: 40 points
        if lead_data.get("timing", {}).get("recent_trigger_events"):
            score += 40

        # Seasonal factors: 30 points
        if lead_data.get("timing", {}).get("seasonal_factors"):
            score += 30

        return score

    def validate_icp(self):
        # Basic validation: check if key sections have some defined criteria
        if not any(self.parsed_icp["company_characteristics"].values()):
            return {"is_valid": False, "message": "Company characteristics are not sufficiently defined in the ICP."}
        if not any(self.parsed_icp["buyer_persona"].values()):
            return {"is_valid": False, "message": "Buyer persona is not sufficiently defined in the ICP."}
        if not any(self.parsed_icp["engagement_signals"].values()):
            return {"is_valid": False, "message": "Engagement signals are not sufficiently defined in the ICP."}
        
        # More specific checks could be added here, e.g., if industry_vertical is empty
        if not self.parsed_icp["company_characteristics"].get("industry_vertical"):
            return {"is_valid": False, "message": "ICP is missing target industries."}
        
        if not self.parsed_icp["buyer_persona"].get("decision_maker_profile"):
            return {"is_valid": False, "message": "ICP is missing target decision maker profiles."}
        return {"is_valid": True, "message": "ICP looks good!"}

    def _estimate_market_size(self):
        # This is a placeholder. In a real scenario, this would involve
        # querying a company database (e.g., Clearbit, ZoomInfo) with the ICP criteria
        # to get an estimated number of matching companies.
        # For now, we'll return a dummy value based on the complexity of the ICP.
        
        # A more complex ICP (more defined criteria) would likely result in a smaller market size.
        # A simpler ICP would result in a larger market size.
        
        # Count the number of defined criteria
        defined_criteria_count = 0
        for category in self.parsed_icp:
            for key, value in self.parsed_icp[category].items():
                if isinstance(value, list) and value:
                    defined_criteria_count += 1
                elif isinstance(value, dict) and any(v is not None for v in value.values()):
                    defined_criteria_count += 1
                elif value:
                    defined_criteria_count += 1
        
        if defined_criteria_count < 3:
            return "10,000,000+" # Very broad
        elif 3 <= defined_criteria_count < 6:
            return "1,000,000 - 10,000,000" # Broad
        elif 6 <= defined_criteria_count < 9:
            return "100,000 - 1,000,000" # Medium
        elif 9 <= defined_criteria_count < 12:
            return "10,000 - 100,000" # Niche
        else:
            return "1,000 - 10,000" # Very Niche

    def check_icp_quality(self):
        market_size = self._estimate_market_size()
        quality_check_results = {
            "market_size_estimate": market_size,
            "breadth_narrowness": "",
            "suggestions": []
        }

        # Placeholder for actual breadth/narrowness logic
        # In a real system, this would compare the market_size against predefined thresholds
        # and potentially analyze the specificity of the ICP criteria.
        
        if "10,000,000+" in market_size:
            quality_check_results["breadth_narrowness"] = "Too Broad"
            quality_check_results["suggestions"].append("Consider adding more specific criteria for industry, company size, or geography to narrow down the ICP.")
        elif "1,000 - 10,000" in market_size:
            quality_check_results["breadth_narrowness"] = "Very Niche"
            quality_check_results["suggestions"].append("Your ICP is very niche. Ensure this is intentional. You might consider broadening some criteria to increase the addressable market.")
        else:
            quality_check_results["breadth_narrowness"] = "Well-defined"
            quality_check_results["suggestions"].append("Your ICP appears well-defined. Continue to monitor lead quality and adjust as needed.")
            
        return quality_check_results

    def categorize_lead(self, total_score):
        if total_score >= self.bucket_thresholds["hot"]:
            return "hot"
        elif total_score >= self.bucket_thresholds["warm"]:
            return "warm"
        else:
            return "cold"

        return {"is_valid": True, "message": "ICP definition looks good for scoring."}
