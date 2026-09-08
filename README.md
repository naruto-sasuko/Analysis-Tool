# Analysis Tool ⚡

A modern, Streamlit-based web application and analytical pipeline designed for banking and loan portfolio risk analysis. It streamlines spreadsheet processing with automated routines for KYC cross-validation, customer ID deduplication, and NPA property valuation auditing.

---

## 🌟 Key Features

1. **CRE KYC Portfolio Analysis (`script_CRE_kyc`)**
   - Filters housing and home loan categories.
   - Identifies borrowers with repeated PAN entries ($\ge 3$) possessing multiple distinct mortgaged assets ($\ge 3$).
   - Formats and isolates matching records sorted by PAN.

2. **UCIC Discrepancy Finder (`script_UCIC_cases`)**
   - Cleans and standardizes alphanumeric Customer Unique Identification Codes (UCIC).
   - Detects complex one-to-many anomalies:
     - The same Customer ID associated with multiple distinct PANs.
     - The same PAN associated with multiple Customer IDs.
   - Exports isolated discrepancy records for deduplication and audit.

3. **NPA Valuation Compliance Checker (`script_NPA_valuation`)**
   - Applies regulatory property revaluation rules on Non-Performing Asset (NPA) accounts:
     - **Sub-standard assets** (NPA prior to March 31, 2025): Flags accounts with missing or overdue valuations (> 548 days).
     - **Other non-standard classifications**: Flags accounts with overdue valuations (> 820 days).

4. **Interactive Web Dashboard**
   - Built with Streamlit for intuitive file upload and real-time data preview.
   - Built-in Supabase authentication (Sign In & Sign Up) with guest mode for offline demonstrations.
   - Direct export of processed analysis reports to formatted Excel (`.xlsx`) files.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/naruto-sasuko/Analysis-Tool.git
cd Analysis-Tool

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Supabase (Optional)
To enable Supabase authentication, create `.streamlit/secrets.toml`:
```toml
SUPABASE_URL = "https://your-supabase-project.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
```
*(Or use "Continue as Guest" to test the data analysis pipeline directly).*

### 4. Run the Application
Launch via PyCharm or the command line:
```bash
# Using main launcher:
python main.py

# Or directly with Streamlit:
streamlit run app.py
# (or: streamlit run "Analysis tool.py")
```

---

## 🧪 Running Verification Tests

Run the included automated test suite:
```bash
python test_suite.py
```

---

## 📂 Project Structure

```
Analysis Tool/
├── app.py                  # Standard Streamlit entry point
├── Analysis tool.py        # Streamlit web application & UI
├── main.py                 # Application launcher
├── requirements.txt        # Python package dependencies
├── test_suite.py           # Unit and integration verification tests
├── README.md               # Project documentation
├── .gitignore              # Git ignore rules
├── .streamlit/
│   ├── secrets.toml        # Local secrets (ignored in git)
│   └── secrets.toml.example# Example secrets template
└── scripts/
    ├── __init__.py         # Modular package exports & backwards compatibility
    ├── script_CRE_kyc.py   # CRE KYC analysis module
    ├── script_UCIC_cases.py# UCIC deduplication and mismatch detector
    ├── script_NPA_valuation.py # NPA valuation compliance checker
    └── 01_ucic_mismatch.py ... 23_cersai_multi_cust.py # Comprehensive audit scripts
```

