import re
from urllib.parse import urlparse

class LeadDataProcessor:
    def __init__(self):
        pass

    def process_lead_data(self, raw_lead_data):
        processed_leads = []
        for lead in raw_lead_data:
            processed_lead = self._normalize_company_info(lead)
            processed_lead = self._extract_contact_info(processed_lead)
            processed_leads.append(processed_lead)
        return processed_leads

    def _normalize_company_info(self, lead):
        # Placeholder for company information normalization
        # Example: Extract domain from website, standardize industry names, etc.
        if "website" in lead and lead["website"]:
            parsed_url = urlparse(lead["website"])
            lead["domain"] = parsed_url.netloc
        return lead

    def _extract_contact_info(self, lead):
        # Placeholder for contact information extraction and normalization
        # This would involve more sophisticated parsing for names, titles, emails, etc.
        if "contact_raw" in lead:
            # Example: simple regex for email extraction
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', lead["contact_raw"])
            if emails: # Check if emails list is not empty
                lead["email"] = emails[0]
            else:
                lead["email"] = None
        return lead

    def run(self, raw_leads):
        print("\n--- Lead Data Processor ---")
        print(f"Processing {len(raw_leads)} raw leads...")
        processed_leads = self.process_lead_data(raw_leads)
        print(f"Processed {len(processed_leads)} leads.")
        return processed_leads
