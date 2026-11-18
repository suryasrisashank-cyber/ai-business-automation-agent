import streamlit as st
import pandas as pd
import json
from datetime import datetime
from google import genai
from google.genai import types

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Business Automation Agent", page_icon="💼", layout="wide")

# --- SAMPLE BUSINESS DATA ---
CRM_DATA = [
    {"Lead": "TechNova Pvt Ltd", "Contact": "arjun@technova.in", "Deal_Value": 180000, "Stage": "Proposal Sent", "Last_Contact_Days": 6, "Notes": "Requested enterprise demo and custom pricing."},
    {"Lead": "GreenLeaf Retail", "Contact": "priya@greenleaf.com", "Deal_Value": 45000, "Stage": "Discovery", "Last_Contact_Days": 14, "Notes": "Budget approval pending next quarter."},
    {"Lead": "Apex Logistics", "Contact": "vikram@apexlog.co", "Deal_Value": 320000, "Stage": "Negotiation", "Last_Contact_Days": 2, "Notes": "Ready to sign if onboarding finishes in 2 weeks."}
]

HRMS_DATA = [
    {"Candidate": "Ananya Sharma", "Role": "AI Engineer", "Experience_Yrs": 3, "Skills": "Python, LLMs, FastAPI, Docker", "Status": "Applied"},
    {"Candidate": "Rohan Verma", "Role": "AI Engineer", "Experience_Yrs": 1, "Skills": "HTML, CSS, Basic Python", "Status": "Applied"},
    {"Candidate": "Sneha Reddy", "Role": "Product Manager", "Experience_Yrs": 5, "Skills": "Agile, CRM, Roadmap, SQL", "Status": "Interviewing"}
]

PMS_DATA = [
    {"Project": "Cloud Migration v2", "Owner": "Karthik", "Deadline_Days": 3, "Completion_Pct": 55, "Blocker": "Waiting on security audit sign-off"},
    {"Project": "Mobile App Redesign", "Owner": "Meera", "Deadline_Days": 12, "Completion_Pct": 85, "Blocker": "None"},
    {"Project": "ERP Billing Sync", "Owner": "Dev", "Deadline_Days": 1, "Completion_Pct": 40, "Blocker": "API rate limit errors in staging"}
]

# --- SESSION STATE INITIALIZATION ---
if "audit_log" not in st.session_state:
    st.session_state.audit_log = [
        {"Time": datetime.now().strftime("%H:%M:%S"), "Role": "System", "Action": "Agent initialized with CRM, HRMS, and PMS datasets."}
    ]
if "agent_output" not in st.session_state:
    st.session_state.agent_output = None

# --- SIDEBAR: ROLE-BASED ACCESS & API KEY ---
with st.sidebar:
    st.header("🔐 Security & Role Control")
    user_role = st.selectbox(
        "Active User Role",
        ["Admin (Full Access)", "Sales Manager (CRM Only)", "HR Recruiter (HRMS Only)", "Project Lead (PMS Only)"]
    )
    
    # Enforce Role-Based Data Access
    allowed_data = {}
    if "Admin" in user_role or "Sales" in user_role:
        allowed_data["CRM_Leads"] = CRM_DATA
    if "Admin" in user_role or "HR" in user_role:
        allowed_data["HRMS_Candidates"] = HRMS_DATA
    if "Admin" in user_role or "Project" in user_role:
        allowed_data["PMS_Projects"] = PMS_DATA

    st.info(f"**Accessible Modules:** {', '.join(allowed_data.keys())}")
    
    # API Key handling (works with Streamlit Secrets or manual paste on mobile)
    api_key = st.secrets.get("GEMINI_API_KEY", "") if "GEMINI_API_KEY" in st.secrets else ""
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste AIzaSy... key")

# --- HEADER ---
st.title("💼 AI Business Automation Agent")
st.caption("Unified CRM • HRMS • PMS Workflow Copilot with Role-Based Access & Auditability")

# --- TOP ANALYTICS DASHBOARD ---
col1, col2, col3 = st.columns(3)
col1.metric("Pipeline Value (CRM)", f"₹{sum(x['Deal_Value'] for x in CRM_DATA):,}", "3 Active Leads")
col2.metric("Active Candidates (HRMS)", len(HRMS_DATA), "2 Open Roles")
col3.metric("At-Risk Projects (PMS)", sum(1 for x in PMS_DATA if x["Deadline_Days"] <= 3 and x["Completion_Pct"] < 70), "Immediate Action")

st.divider()

# --- NATURAL LANGUAGE COMMAND INTERFACE ---
st.subheader("🤖 Natural Language Workflow Command")
preset = st.selectbox(
    "Quick Test Prompts (or type your own below):",
    [
        "Custom command...",
        "Score all CRM leads from 1-100 and draft a follow-up email for the highest priority lead.",
        "Screen HRMS candidates for the AI Engineer role and rank them with justification.",
        "Identify high-risk PMS projects, explain blockers, and draft an escalation alert."
    ]
)

default_prompt = "" if preset == "Custom command..." else preset
user_command = st.text_area("Instruct the Agent:", value=default_prompt, height=90, placeholder="e.g., Score leads, screen resumes, check project delays, or draft follow-ups...")

if st.button("⚡ Execute Workflow", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar (tap '>' at top-left on mobile).")
    elif not user_command.strip():
        st.warning("Please enter a command or select a quick test prompt.")
    else:
        with st.spinner("Agent analyzing authorized business data..."):
            try:
                client = genai.Client(api_key=api_key)
                system_instruction = (
                    "You are an enterprise AI Business Automation Agent for CRM, HRMS, and PMS. "
                    "You MUST ONLY use the JSON data provided in the user's authorized scope. "
                    "If the user asks about a module not present in their authorized data, politely refuse due to Role-Based Access Control (RBAC). "
                    "Return structured, executive-ready outputs including: 1) Action Summary, 2) Structured Table/Scores, and 3) Ready-to-send Email/Alert Draft."
                )
                prompt_payload = f"Authorized Role: {user_role}\nAuthorized Data:\n{json.dumps(allowed_data, indent=2)}\n\nUser Command: {user_command}"
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_payload,
                    config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)
                )
                st.session_state.agent_output = response.text
                st.session_state.audit_log.append({
                    "Time": datetime.now().strftime("%H:%M:%S"),
                    "Role": user_role,
                    "Action": f"Executed: '{user_command[:50]}...'"
                })
            except Exception as e:
                st.error(f"Agent Error: {e}")

# --- WORKFLOW OUTPUT DISPLAY ---
if st.session_state.agent_output:
    st.success("✅ Workflow Completed")
    st.markdown(st.session_state.agent_output)

st.divider()

# --- TABS: LIVE DATA, CHARTS & AUDIT LOG ---
tab1, tab2, tab3 = st.tabs(["📊 Live Business Data", "📈 Analytics Chart", "🛡️ Audit Trail"])

with tab1:
    if "CRM_Leads" in allowed_data:
        st.markdown("**CRM Leads**")
        st.dataframe(pd.DataFrame(CRM_DATA), use_container_width=True)
    if "HRMS_Candidates" in allowed_data:
        st.markdown("**HRMS Candidates**")
        st.dataframe(pd.DataFrame(HRMS_DATA), use_container_width=True)
    if "PMS_Projects" in allowed_data:
        st.markdown("**PMS Projects**")
        st.dataframe(pd.DataFrame(PMS_DATA), use_container_width=True)

with tab2:
    st.markdown("**Deal Value by Lead (CRM)**")
    chart_df = pd.DataFrame(CRM_DATA).set_index("Lead")["Deal_Value"]
    st.bar_chart(chart_df)

with tab3:
    st.markdown("**Security & Action Audit Log**")
    st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True)
