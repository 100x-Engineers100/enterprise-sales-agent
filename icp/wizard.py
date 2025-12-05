import json
import csv
from icp.scoring import ICPScorer

class ICPWizard:
    def __init__(self):
        self.icp_data = {
            "company_characteristics": {},
            "buyer_persona": {},
            "engagement_signals": {}
        }
        self.questions = {
            "company_characteristics": {
                "industry_vertical": {
                    "question": "What is the primary industry and sub-vertical of your ideal customer?",
                    "examples": "e.g., B2B SaaS, D2C E-commerce, Manufacturing. Excludes: Competitors, Non-fits."
                },
                "company_size": {
                    "question": "What is the employee count range and revenue range of your ideal customer?",
                    "examples": "e.g., 10-50 employees, $1M-$10M revenue. Growth stage: Seed, Series A, B, C."
                },
                "geography": {
                    "question": "What are the target countries/regions, timezone considerations, and language requirements for your ideal customer?",
                    "examples": "e.g., USA (EST), English speaking."
                },
                "technology_stack": {
                    "question": "What must-have and nice-to-have tools should your ideal customer be using? Are there any specific technology indicators?",
                    "examples": "e.g., Salesforce, HubSpot. Cloud-native, API-first."
                },
                "business_model": {
                    "question": "What is the business model of your ideal customer and their revenue/sales motion?",
                    "examples": "e.g., B2B, B2C, B2B2C. Subscription, transactional. PLG, sales-led, hybrid."
                },
                "funding_growth": {
                    "question": "What is the funding stage, recent funding events, and growth indicators for your ideal customer?",
                    "examples": "e.g., Seed, Series A, hiring, expansion."
                }
            },
            "buyer_persona": {
                "decision_maker_profile": {
                    "question": "What are the typical job titles, seniority levels, department, and reporting structure of decision-makers you target?",
                    "examples": "e.g., VP Sales, CRO, CEO. Senior, Mid-level. Sales, Marketing."
                },
                "pain_points": {
                    "question": "What are the primary challenges or pain points your ideal customer faces? What current solutions do they use, and why would they switch?",
                    "examples": "e.g., Inefficient lead generation. Using spreadsheets. Need automation."
                },
                "buying_behavior": {
                    "question": "Describe the typical decision-making process, sales cycle length, budget authority, and evaluation criteria of your ideal customer.",
                    "examples": "e.g., Committee decision. 3-6 month cycle. VP-level budget. ROI-driven."
                }
            },
            "engagement_signals": {
                "intent_signals": {
                    "question": "What intent signals indicate a good prospect?",
                    "examples": "e.g., Job postings for X role, funding announcements, executive changes, product launches."
                },
                "content_engagement": {
                    "question": "What content engagement indicates a good prospect?",
                    "examples": "e.g., Website visits, content downloads, event attendance, social media activity."
                }
            },
            "Enterprise Software (Large Accounts)": {
                "company_characteristics": {
                    "industry_vertical": "Enterprise Software, Cybersecurity",
                    "company_size": "1000+ employees, $500M+ revenue",
                    "geography": "Global",
                    "technology_stack": "AWS, Azure, Kubernetes, Splunk",
                    "business_model": "B2B, Enterprise License",
                    "funding_growth": "Publicly Traded, Consistent Revenue Growth"
                },
                "buyer_persona": {
                    "decision_maker_profile": "CISO, VP IT, Director of Security Operations",
                    "pain_points": "Data breaches, Compliance issues, Vendor sprawl, Talent shortage",
                    "buying_behavior": "9-12 month sales cycle, C-level approval, Multi-million dollar budget"
                },
                "engagement_signals": {
                    "intent_signals": "Regulatory changes, Major security incidents, Competitor product recalls",
                    "content_engagement": "Attended industry conferences, Read Gartner reports, Engaged with security webinars"
                }
            }
        }
        self.templates = self._load_templates()

    def _load_templates(self):
        """Load pre-built industry ICP templates"""
        return {
            "B2B SaaS (SMB)": {
                "company_characteristics": {
                    "industry_vertical": "B2B SaaS, Project Management",
                    "company_size": "10-50 employees, $1M-$10M revenue",
                    "geography": "North America, Europe (UTC-5 to UTC+2)",
                    "technology_stack": "Salesforce, HubSpot, Slack",
                    "business_model": "B2B, Subscription-based",
                    "funding_growth": "Seed, Series A, Hiring Sales Team"
                },
                "buyer_persona": {
                    "decision_maker_profile": "VP Operations, Director of Project Management, Mid-Senior",
                    "pain_points": "Inefficient team collaboration, Lack of project visibility, High tool fragmentation",
                    "buying_behavior": "6-8 week sales cycle, Cross-departmental approval, $5k-$20k annual budget"
                },
                "engagement_signals": {
                    "intent_signals": "Job postings for project managers, Recent funding announcements, Tech stack changes to collaboration tools",
                    "content_engagement": "Downloaded project management whitepapers, Attended collaboration webinars"
                }
            },
            "D2C E-commerce (Fashion)": {
                "company_characteristics": {
                    "industry_vertical": "D2C E-commerce, Sustainable Fashion",
                    "company_size": "50-200 employees, $10M-$50M revenue",
                    "geography": "North America, Australia (UTC-8 to UTC+10)",
                    "technology_stack": "Shopify, Klaviyo, Instagram Shopping",
                    "business_model": "D2C, Direct-to-consumer",
                    "funding_growth": "Series A, Series B, Expanding to new markets"
                },
                "buyer_persona": {
                    "decision_maker_profile": "CMO, Director of E-commerce, Senior",
                    "pain_points": "Low customer retention, High cart abandonment, Ineffective email marketing",
                    "buying_behavior": "4-6 week sales cycle, Marketing team approval, $10k-$50k annual budget"
                },
                "engagement_signals": {
                    "intent_signals": "Hiring for e-commerce marketers, Recent product launches, Competitor discount campaigns",
                    "content_engagement": "Viewed sustainable fashion case studies, Signed up for email newsletters"
                }
            },
            "Healthcare Tech (B2B)": {
                "company_characteristics": {
                    "industry_vertical": "Healthcare Technology, Digital Health",
                    "company_size": "100-500 employees, $20M-$100M revenue",
                    "geography": "USA (EST, PST), Canada",
                    "technology_stack": "HL7, FHIR, AWS, Epic, Cerner",
                    "business_model": "B2B, SaaS, Enterprise",
                    "funding_growth": "Series B, Series C, Expanding product lines"
                },
                "buyer_persona": {
                    "decision_maker_profile": "CIO, VP Product, Head of Digital Health, Director of IT, Senior",
                    "pain_points": "Interoperability challenges, Regulatory compliance (HIPAA), Data security, Legacy system integration",
                    "buying_behavior": "6-12 month sales cycle, Clinical and IT stakeholder approval, $50k-$200k annual budget"
                },
                "engagement_signals": {
                    "intent_signals": "New healthcare regulations, Hospital system mergers, EHR upgrades, Funding for digital health initiatives",
                    "content_engagement": "Downloaded healthcare IT whitepapers, Attended HIMSS conference, Engaged with health tech webinars"
                }
            },
            "FinTech (B2B)": {
                "company_characteristics": {
                    "industry_vertical": "Financial Technology, RegTech, Payments",
                    "company_size": "50-300 employees, $10M-$75M revenue",
                    "geography": "Global (London, New York, Singapore)",
                    "technology_stack": "AWS, Azure, Kubernetes, Kafka, Murex",
                    "business_model": "B2B, SaaS, API-first",
                    "funding_growth": "Series A, Series B, Expanding into new markets"
                },
                "buyer_persona": {
                    "decision_maker_profile": "CTO, Head of Compliance, VP Risk, Director of Payments, Senior",
                    "pain_points": "Regulatory burden (GDPR, PSD2), Fraud detection, Legacy infrastructure, Scalability issues",
                    "buying_behavior": "8-14 month sales cycle, Legal and Security review, $75k-$300k annual budget"
                },
                "engagement_signals": {
                    "intent_signals": "New financial regulations, Major security breaches in finance, Partnership announcements, Funding for FinTech startups",
                    "content_engagement": "Read FinTech trend reports, Attended Money20/20, Engaged with regulatory compliance webinars"
                }
            }
        }


    def _ask_question(self, question_data):
        question = question_data["question"]
        examples = question_data.get("examples", "")
        while True:
            print(f"\n{question}")
            if examples:
                print(f"({examples})")
            response = input("Your answer: ").strip()
            if response:
                return response
            else:
                print("Input cannot be empty. Please provide a response.")

    def run(self):
        print("\n--- ICP Definition Wizard ---")
        print("Let's define your Ideal Customer Profile (ICP) step-by-step.")

        while True:
            print("\nDo you want to:")
            print("1. Create a new ICP from scratch")
            print("2. Load an existing template")
            choice = input("Enter your choice (1 or 2): ").strip()

            if choice == '1':
                self._define_icp_from_scratch()
                break
            elif choice == '2':
                self._load_icp_from_template()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

        print("\n--- ICP Summary ---")
        print(json.dumps(self.icp_data, indent=2))

        # Validate and check ICP quality using ICPScorer
        print("\n--- ICP Validation & Quality Check ---")
        scorer = ICPScorer(self.icp_data)
        validation_result = scorer.validate_icp()
        print(f"Validation Status: {'Passed' if validation_result['is_valid'] else 'Failed'}")
        print(f"Validation Message: {validation_result['message']}")

        if validation_result['is_valid']:
            quality_result = scorer.check_icp_quality()
            print(f"Market Size Estimate: {quality_result['market_size_estimate']}")
            print(f"ICP Breadth/Narrowness: {quality_result['breadth_narrowness']}")
            print("Suggestions:")
            for idx, suggestion in enumerate(quality_result['suggestions'], 1):
                print(f"  {idx}. {suggestion}")

            # Allow user to adjust ICP if needed
            while True:
                adjust = input("\nWould you like to adjust your ICP based on this feedback? (yes/no): ").lower().strip()
                if adjust == 'yes':
                    print("\nLet's update your ICP step-by-step.")
                    self._update_icp()
                    return self.run()  # Re-run wizard with updated data
                elif adjust == 'no':
                    break

        # ICP Data Export Option
        while True:
            export_choice = input("\nWould you like to export your ICP data? (yes/no): ").lower().strip()
            if export_choice == 'yes':
                print("\nAvailable export formats: 1. JSON 2. CSV")
                format_choice = input("Select export format (1 or 2): ").strip()
                self._export_icp_data(format_choice)
                break
            elif export_choice == 'no':
                break
            else:
                print("Invalid choice. Please enter yes or no.")

        print("\nThank you for defining your ICP!")
        return self.icp_data

    def _define_icp_from_scratch(self):
        for category, sub_questions in self.questions.items():
            print(f"\n--- {category.replace('_', ' ').title()} ---")
            for key, question_data in sub_questions.items():
                response = self._ask_question(question_data)
                self.icp_data[category][key] = response

    def _load_icp_from_template(self):
        print("\nAvailable Templates:")
        for i, template_name in enumerate(self.templates.keys()):
            print(f"{i+1}. {template_name}")

        while True:
            try:
                choice = int(input("Select a template by number: ").strip())
                if 1 <= choice <= len(self.templates):
                    selected_template_name = list(self.templates.keys())[choice - 1]
                    self.icp_data = self.templates[selected_template_name]
                    print(f"Loaded template: {selected_template_name}")
                    break
                else:
                    print("Invalid template number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def _update_icp(self):
        """Allow user to update existing ICP fields"""
        for category, sub_questions in self.questions.items():
            print(f"\n--- Update {category.replace('_', ' ').title()} ---\n")
            for key, question_data in sub_questions.items():
                current_value = self.icp_data[category].get(key, "")
                print(f"Current value for '{key.replace('_', ' ')}': {current_value}")
                response = input(f"{question_data['question']} (leave blank to keep current value): ").strip()
                if response:
                    self.icp_data[category][key] = response
                else:
                    pass

    def _export_icp_data(self, format_choice):
        """Export ICP data to JSON or CSV format (reuses existing json.dumps logic from ICP Summary)"""
        if format_choice == '1':
            # JSON export (reuses json.dumps from line 175 of icp/wizard.py)
            file_path = input("Enter JSON file path to save (e.g., icp_export.json): ").strip()
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.icp_data, f, indent=2)
                print(f"Successfully exported ICP data to {file_path}")
            except IOError as e:
                print(f"Failed to export JSON file: {str(e)}")
        elif format_choice == '2':
            # CSV export (handles nested icp_data by flattening with category prefixes)
            file_path = input("Enter CSV file path to save (e.g., icp_export.csv): ").strip()
            try:
                # Flatten nested icp_data structure (e.g., company_characteristics.industry_vertical)
                flattened_data = {}
                for category, sub_data in self.icp_data.items():
                    for key, value in sub_data.items():
                        flattened_key = f"{category}.{key}"
                        flattened_data[flattened_key] = value
                # Write to CSV
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=flattened_data.keys())
                    writer.writeheader()
                    writer.writerow(flattened_data)
                print(f"Successfully exported ICP data to {file_path}")
            except IOError as e:
                print(f"Failed to export CSV file: {str(e)}")
        else:
            print("Invalid export format choice")

if __name__ == "__main__":
    wizard = ICPWizard()
    wizard.run()
    wizard = ICPWizard()
    wizard.run()
