# Enterprise Sales Agent

This project implements a 5-phase autonomous SDR (Sales Development Representative) system designed to streamline the sales process from ICP (Ideal Customer Profile) definition to CRM handoff and continuous learning. The system automates key sales tasks, enabling efficient lead generation, qualification, engagement, and deal management.

## Project Overview

The Enterprise Sales Agent operates through five distinct phases:

1.  **ICP Builder**: Defines and refines the Ideal Customer Profile.
2.  **Lead Discovery**: Identifies and gathers potential leads based on the defined ICP.
3.  **Pre-Qualification & Qualification**: Researches and qualifies leads to ensure they align with the ICP.
4.  **Engagement**: Initiates and manages communication with qualified leads.
5.  **Handoff & Learning**: Transfers qualified and engaged leads to a CRM system and incorporates feedback for continuous improvement.

## Setup Instructions

To set up and run the Enterprise Sales Agent, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/enterprise-sales-agent.git
cd enterprise-sales-agent
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory of the project based on the `env.example` file. Fill in the necessary API keys and credentials for the services you intend to use.

```
# .env example
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_api_key_here
COMPANY_DATABASE_API_KEY=your_company_database_api_key_here
GITHUB_API_KEY=your_github_api_key_here
PRODUCT_HUNT_API_KEY=your_product_hunt_api_key_here
G2_API_KEY=your_g2_api_key_here
JOB_BOARD_API_KEY=your_job_board_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
SALESFORCE_INSTANCE_URL=your_salesforce_instance_url_here
SALESFORCE_USERNAME=your_salesforce_username_here
SALESFORCE_PASSWORD=your_salesforce_password_here
SALESFORCE_SECURITY_TOKEN=your_salesforce_security_token_here
PIPEDRIVE_API_KEY=your_pipedrive_api_key_here
PIPEDRIVE_COMPANY_DOMAIN=your_pipedrive_company_domain_here
PIPEDRIVE_DEFAULT_STAGE_ID=your_pipedrive_default_stage_id_here
```

### 5. Run the Agent

Execute the main script to start the autonomous SDR workflow:

```bash
python core.py
```

## Folder and File Structure

Here's an explanation of the main folders and files in the project:

*   **`core.py`**: The main entry point of the application. Orchestrates the entire 5-phase SDR workflow.
*   **`icp/`**: Contains modules related to Ideal Customer Profile (ICP) definition and scoring.
    *   `icp/wizard.py`: Handles the creation and management of ICP definitions.
    *   `icp/scoring.py`: Implements the logic for scoring leads against the defined ICP.
*   **`lead_discovery/`**: Modules for identifying and processing leads.
    *   `lead_discovery/sources.py`: Integrates with various data sources to discover raw leads.
    *   `lead_discovery/data_processor.py`: Cleans, normalizes, and enriches raw lead data.
*   **`pre_qualification/`**: Modules for initial lead research and pre-qualification.
    *   `pre_qualification/research_engine.py`: Conducts research to gather additional information about leads.
*   **`qualification/`**: Modules for qualifying leads based on ICP and research data.
    *   `qualification/frameworks.py`: Implements qualification frameworks and logic.
*   **`engagement/`**: Modules for engaging with qualified leads.
    *   `engagement/orchestrator.py`: Orchestrates communication strategies and outreach.
*   **`booking/`**: Modules for scheduling meetings with engaged leads.
    *   `booking/calendar.py`: Integrates with calendar services to book meetings.
*   **`handoff/`**: Modules for handing off qualified leads to CRM systems and learning from outcomes.
    *   `handoff/crm.py`: Manages integration with various CRM platforms (Salesforce, HubSpot, Pipedrive).
*   **`learning/`**: Contains the learning engine that analyzes CRM outcomes to refine the ICP and improve future SDR operations.
    *   `learning/engine.py`: Processes feedback from CRM outcomes and generates suggestions for ICP refinement.
*   **`requirements.txt`**: Lists all Python dependencies required for the project.
*   **`.env.example`**: An example file demonstrating the required environment variables.

