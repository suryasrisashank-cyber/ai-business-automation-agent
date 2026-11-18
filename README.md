# AI Business Automation Agent (CRM + HRMS + PMS)

An enterprise AI agent built with **Streamlit** and **Google Gemini 2.5 Flash** that automates sales lead scoring, HR resume screening, and project risk management with Role-Based Access Control (RBAC) and full action auditability.

## Features
- **Natural Language Command Interface:** Execute workflows across CRM, HRMS, and PMS using plain English.
- **Role-Based Access Control (RBAC):** Switch between *Admin*, *Sales Manager*, *HR Recruiter*, and *Project Lead* to enforce strict module-level data permissions.
- **Automated Action Outputs:** Generates priority scores, candidate rankings, project risk alerts, and ready-to-send emails.
- **Analytics & Audit Trail:** Live metrics, visual charts, and a timestamped security log of every executed command.

## Quick Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run locally: `streamlit run app.py`
3. Enter your Gemini API Key in the sidebar (or set `GEMINI_API_KEY` in Streamlit Secrets).
