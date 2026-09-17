# Analysis tool.py
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import os
import io
import pandas as pd
import streamlit as st
from supabase import Client, create_client

# Script imports
from scripts import script_CRE_kyc, script_UCIC_cases, script_NPA_valuation
from scripts.scenario_registry import (
    SCENARIO_CATALOG,
    get_categories,
    get_scenarios_by_category,
    get_scenario,
    execute_scenario,
)


# 1. Page config MUST be the first Streamlit command
st.set_page_config(page_title="Analysis Tool", page_icon="⚡", layout="wide")

# Hide Streamlit header, GitHub icons, menu, deploy button, and viewer badges
st.markdown(
    """
    <style>
    /* Hide top header, toolbar, hamburger menu, and footer */
    #MainMenu {visibility: hidden !important; display: none !important;}
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stHeader"] {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
    [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
    .stAppDeployButton {visibility: hidden !important; display: none !important;}
    
    /* Hide all GitHub links, icons, and Streamlit Cloud viewer badges */
    a[href*="github.com"] {visibility: hidden !important; display: none !important;}
    .viewerBadge_container__1QSob, .viewerBadge_link__1S137, [class*="viewerBadge"] {
        visibility: hidden !important;
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 2. Initialize Supabase Client with safe fallback
def get_secret(key: str, default: str) -> str:
    env_val = os.environ.get(key)
    if env_val:
        return env_val
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

SUPABASE_URL = get_secret("SUPABASE_URL", "https://hlcbxoullislabvwoshm.supabase.co")
SUPABASE_KEY = get_secret("SUPABASE_KEY", "sb_publishable_ModfMKP3wO6OWDHW96aQWg_qEHhRCC8")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as init_err:
    supabase = None

# 3. User Authentication State
if "user" not in st.session_state:
    st.session_state.user = None

# --- AUTHENTICATION SCREEN ---
if not st.session_state.user:
    st.title("⚡ Analysis SaaS Portal")
    auth_tab1, auth_tab2, auth_tab3 = st.tabs(["Login", "Sign Up", "Demo Mode"])

    with auth_tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In", type="primary"):
            if not supabase:
                st.error("Supabase client not initialized. Check your credentials.")
            else:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

    with auth_tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Create Free Account"):
            if not supabase:
                st.error("Supabase client not initialized. Check your credentials.")
            else:
                try:
                    supabase.auth.sign_up({"email": new_email, "password": new_password})
                    st.success("Account created! Check your email to confirm or log in.")
                except Exception as e:
                    st.error(f"Sign up error: {e}")

    with auth_tab3:
        st.write("Explore Analysis without Supabase credentials.")
        if st.button("Continue as Guest (Demo Mode)", type="secondary"):
            class GuestUser:
                email = "guest@demo.local"
            st.session_state.user = GuestUser()
            st.rerun()

# --- MAIN SAAS DASHBOARD ---
else:
    st.sidebar.write(f"Logged in as: **{st.session_state.user.email}**")
    if st.sidebar.button("Log Out"):
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        st.session_state.user = None
        st.session_state.pop("result", None)
        st.session_state.pop("script_name", None)
        st.rerun()

    st.title("📂 Process Data")
    uploaded_file = st.file_uploader("Upload Excel Spreadsheet (.xlsb, .xlsx, .xls)", type=["xlsb", "xlsx", "xls"])

    if uploaded_file is not None:
        fname = getattr(uploaded_file, "name", "").lower()
        engines = ["calamine", "pyxlsb", "openpyxl"] if fname.endswith(".xlsb") else ["openpyxl", "calamine", "pyxlsb", None]
        df = None
        last_err = None
        for eng in engines:
            try:
                uploaded_file.seek(0)
                kwargs = {"engine": eng} if eng else {}
                df = pd.read_excel(uploaded_file, **kwargs)
                break
            except Exception as read_err:
                last_err = read_err
                continue

        if df is None and last_err is not None:
            st.error(f"Failed to read Excel file: {last_err}")


        if df is not None:
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")

            st.divider()
            
            # --- SECTION 1: QUICK ACTIONS ---
            st.subheader("⚡ Quick Audit Actions")
            col1, col2, col3 = st.columns(3)

            # Button 1: CRE_kyc
            with col1:
                st.markdown("### 📊 CRE KYC")
                st.write("Repeated accounts (≥3) with multiple unique dwellings.")
                if st.button("Run CRE_kyc Script", type="primary", use_container_width=True):
                    with st.spinner("Processing CRE KYC..."):
                        try:
                            result_df = script_CRE_kyc.run(df)
                            st.session_state["result"] = result_df
                            st.session_state["script_name"] = "CRE_kyc"
                        except Exception as e:
                            st.error(f"CRE_kyc processing error: {e}")

            # Button 2: UCIC_cases
            with col2:
                st.markdown("### 🧹 UCIC Discrepancies")
                st.write("One-to-many mismatches between Customer IDs and KYC.")
                if st.button("Run UCIC_cases Script", type="primary", use_container_width=True):
                    with st.spinner("Processing UCIC cases..."):
                        try:
                            result_df = script_UCIC_cases.run(df)
                            st.session_state["result"] = result_df
                            st.session_state["script_name"] = "UCIC_cases"
                        except Exception as e:
                            st.error(f"UCIC_cases processing error: {e}")

            # Button 3: NPA_valuation
            with col3:
                st.markdown("### ⚖️ NPA Valuation")
                st.write("Overdue property valuations based on NPA date rules.")
                if st.button("Run NPA Valuation Script", type="primary", use_container_width=True):
                    with st.spinner("Processing NPA Valuation..."):
                        try:
                            result_df = script_NPA_valuation.run(df)
                            st.session_state["result"] = result_df
                            st.session_state["script_name"] = "NPA_valuation"
                        except Exception as e:
                            st.error(f"NPA Valuation processing error: {e}")

            st.divider()

            # --- SECTION 2: COMPREHENSIVE 23-SCENARIO SUITE ---
            st.subheader("🔍 Complete Regulatory & Portfolio Audit Suite (23 Routines)")
            st.write("Select any of the 23 dedicated analytical routines to audit KYC, property valuations, LTV compliance, and credit anomalies.")

            all_cats = ["All Categories"] + get_categories()
            selected_cat = st.radio("Filter by Category:", all_cats, horizontal=True)

            scenarios_in_cat = get_scenarios_by_category(selected_cat)
            scenario_options = {s["title"]: s["id"] for s in scenarios_in_cat}

            selected_title = st.selectbox("Select Audit Scenario:", list(scenario_options.keys()))
            selected_id = scenario_options[selected_title]
            scenario_meta = get_scenario(selected_id)

            st.info(f"**Audit Description**: {scenario_meta['description']}")

            if st.button(f"🚀 Run {scenario_meta['title']}", type="primary", use_container_width=True):
                with st.spinner(f"Executing {scenario_meta['title']}..."):
                    try:
                        res = execute_scenario(selected_id, df)
                        st.session_state["result"] = res
                        st.session_state["script_name"] = selected_id
                    except Exception as e:
                        st.error(f"Execution failed for {selected_id}: {e}")

            # Results display & download

            if "result" in st.session_state:
                st.divider()
                st.subheader("✅ Processed Result")
                out_df = st.session_state["result"]
                st.dataframe(out_df, use_container_width=True)
                st.caption(f"Processed Rows: {len(out_df)}")

                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    out_df.to_excel(writer, index=False)

                st.download_button(
                    label="📥 Download Output Excel",
                    data=buffer.getvalue(),
                    file_name=f"output_{st.session_state.get('script_name', 'data')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                )