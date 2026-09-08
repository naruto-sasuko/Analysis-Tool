"""
Scenario Registry for Analysis Tool.
Defines catalog metadata and dynamic execution for all 23 financial audit routines.
"""
import importlib
from typing import Dict, Any, List
import pandas as pd

SCENARIO_CATALOG: Dict[str, Dict[str, Any]] = {
    # --- Category 1: KYC & Identity Anomaly Detection ---
    "01_ucic_mismatch": {
        "id": "01_ucic_mismatch",
        "module": "01_ucic_mismatch",
        "title": "01. UCIC Mismatch",
        "category": "KYC & Identity",
        "description": "Detects one-to-many anomalies where a single Customer ID is mapped to multiple PANs or vice versa.",
    },
    "11_ckyc_delay": {
        "id": "11_ckyc_delay",
        "module": "11_ckyc_delay",
        "title": "11. CKYC Delay & Contradictions",
        "category": "KYC & Identity",
        "description": "Flags loans disbursed >10 days before CKYC registration or contradictory CKYC completion flags.",
    },
    "14_kyc_risk_div_pan": {
        "id": "14_kyc_risk_div_pan",
        "module": "14_kyc_risk_div_pan",
        "title": "14. KYC Risk Divergence by PAN",
        "category": "KYC & Identity",
        "description": "Identifies borrower PANs assigned conflicting KYC risk categories across multiple loan accounts.",
    },
    "15_kyc_risk_div_cust": {
        "id": "15_kyc_risk_div_cust",
        "module": "15_kyc_risk_div_cust",
        "title": "15. KYC Risk Divergence by Customer ID",
        "category": "KYC & Identity",
        "description": "Detects divergent KYC risk categorizations under the same Customer Unique ID.",
    },
    "19_re_kyc_analysis": {
        "id": "19_re_kyc_analysis",
        "module": "19_re_kyc_analysis",
        "title": "19. Re-KYC Updation Analysis",
        "category": "KYC & Identity",
        "description": "Evaluates timely re-KYC review against risk-based regulatory review intervals (Low/Med/High).",
    },

    # --- Category 2: Asset & Property Valuation Audits ---
    "02_npa_valuation": {
        "id": "02_npa_valuation",
        "module": "02_npa_valuation",
        "title": "02. NPA Property Valuation Audit",
        "category": "Asset & Valuation",
        "description": "Audits overdue property revaluations on NPA accounts under regulatory 183/548/820 day rules.",
    },
    "04_cre_cases_cust": {
        "id": "04_cre_cases_cust",
        "module": "04_cre_cases_cust",
        "title": "04. CRE Cases by Customer ID",
        "category": "Asset & Valuation",
        "description": "Identifies commercial real estate concentration where a Customer ID holds >=3 loans with >=3 unique assets.",
    },
    "05_cre_cases_pan": {
        "id": "05_cre_cases_pan",
        "module": "05_cre_cases_pan",
        "title": "05. CRE Cases by Borrower PAN",
        "category": "Asset & Valuation",
        "description": "Isolates borrower PANs with repeated housing loan accounts (>=3) and >=3 unique mortgaged assets.",
    },
    "16_asset_div_pan": {
        "id": "16_asset_div_pan",
        "module": "16_asset_div_pan",
        "title": "16. Asset Classification Divergence (PAN)",
        "category": "Asset & Valuation",
        "description": "Finds instances where the same borrower PAN is classified differently (e.g. Standard vs NPA) across loans.",
    },
    "17_asset_div_cust": {
        "id": "17_asset_div_cust",
        "module": "17_asset_div_cust",
        "title": "17. Asset Classification Divergence (Cust ID)",
        "category": "Asset & Valuation",
        "description": "Detects conflicting asset classifications (Standard, Sub-standard, D1) under the same Customer ID.",
    },
    "18_asset_div_coborr": {
        "id": "18_asset_div_coborr",
        "module": "18_asset_div_coborr",
        "title": "18. Cross-Linked Asset Divergence (Co-Borrowers)",
        "category": "Asset & Valuation",
        "description": "Flags asset classification divergence across primary borrowers and linked co-borrower PANs.",
    },
    "23_cersai_multi_cust": {
        "id": "23_cersai_multi_cust",
        "module": "23_cersai_multi_cust",
        "title": "23. CERSAI Multi-Customer Asset Mappings",
        "category": "Asset & Valuation",
        "description": "Uncovers collateral fraud where a single CERSAI security ID is registered against multiple Customer IDs.",
    },

    # --- Category 3: LTV, Exposure & Risk Weighting ---
    "03_ihl_non_ind": {
        "id": "03_ihl_non_ind",
        "module": "03_ihl_non_ind",
        "title": "03. IHL Loans to Non-Individuals",
        "category": "LTV & Risk Weight",
        "description": "Detects Individual Housing Loans erroneously extended to corporate/commercial entities (Pvt Ltd, Trading).",
    },
    "06_combined_ltv_rw_cases": {
        "id": "06_combined_ltv_rw_cases",
        "module": "06_combined_ltv_rw_cases",
        "title": "06. Combined LTV & Risk Weight Audit",
        "category": "LTV & Risk Weight",
        "description": "Aggregates borrower exposure across multiple accounts to recalculate true combined LTV and capital risk weights.",
    },
    "07_negative_amortization": {
        "id": "07_negative_amortization",
        "module": "07_negative_amortization",
        "title": "07. Negative Amortization Audit",
        "category": "LTV & Risk Weight",
        "description": "Identifies standard loans where the principal outstanding increased over the fiscal year despite repayment terms.",
    },
    "08_pre_emi_anomalies": {
        "id": "08_pre_emi_anomalies",
        "module": "08_pre_emi_anomalies",
        "title": "08. Pre-EMI Anomalies & Stagnant Loans",
        "category": "LTV & Risk Weight",
        "description": "Flags seasoned loans (>3 years) persisting indefinitely in Pre-EMI status with zero regular EMI amortization.",
    },
    "09_pc_cases": {
        "id": "09_pc_cases",
        "module": "09_pc_cases",
        "title": "09. Plot + Construction Anomalies",
        "category": "LTV & Risk Weight",
        "description": "Isolates Plot + Construction loans disbursed before March 2023 that remain unconstructed or vacant.",
    },
    "10_single_tranche": {
        "id": "10_single_tranche",
        "module": "10_single_tranche",
        "title": "10. Single Tranche Construction Loans",
        "category": "LTV & Risk Weight",
        "description": "Finds construction/P+C loans disbursed in a single 100% bullet disbursement instead of milestone tranches.",
    },

    # --- Category 4: Credit Quality & Early Warnings ---
    "12_quick_mortality": {
        "id": "12_quick_mortality",
        "module": "12_quick_mortality",
        "title": "12. Quick Mortality Early Warnings",
        "category": "Credit Quality",
        "description": "Identifies freshly sanctioned loans slipping into NPA within their first 12 months of origination.",
    },
    "13_over_disbursed": {
        "id": "13_over_disbursed",
        "module": "13_over_disbursed",
        "title": "13. Over-Disbursed Loans",
        "category": "Credit Quality",
        "description": "Detects underwriting governance violations where cumulative disbursements exceed total sanctioned credit limit.",
    },
    "20_multiple_housing_loans": {
        "id": "20_multiple_housing_loans",
        "module": "20_multiple_housing_loans",
        "title": "20. Multiple Housing Loans in Same Year",
        "category": "Credit Quality",
        "description": "Flags speculative borrowing where multiple fresh housing loans were sanctioned to the same PAN within 365 days.",
    },
    "21_evergreen_cases": {
        "id": "21_evergreen_cases",
        "module": "21_evergreen_cases",
        "title": "21. Evergreen / Refinanced Write-Offs",
        "category": "Credit Quality",
        "description": "Detects evergreening by cross-matching active borrowers against written-off or settled portfolio records.",
    },
    "22_collection_efficiency": {
        "id": "22_collection_efficiency",
        "module": "22_collection_efficiency",
        "title": "22. Collection Efficiency Intersections",
        "category": "Credit Quality",
        "description": "Evaluates recurring collection delinquency trends across consecutive quarterly cycles.",
    },
}


def get_categories() -> List[str]:
    """Returns unique sorted list of scenario categories."""
    cats = list(dict.fromkeys(s["category"] for s in SCENARIO_CATALOG.values()))
    return cats


def get_scenarios_by_category(category: str = None) -> List[Dict[str, Any]]:
    """Returns list of scenarios matching the given category, or all scenarios if None."""
    if not category or category == "All Categories":
        return list(SCENARIO_CATALOG.values())
    return [s for s in SCENARIO_CATALOG.values() if s["category"] == category]


def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """Returns scenario definition by ID."""
    return SCENARIO_CATALOG.get(scenario_id)


def execute_scenario(scenario_id: str, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Dynamically imports and executes the given scenario module on the provided dataframe."""
    scenario = SCENARIO_CATALOG.get(scenario_id)
    if not scenario:
        raise ValueError(f"Unknown scenario ID '{scenario_id}'")

    mod_name = f"scripts.{scenario['module']}"
    mod = importlib.import_module(mod_name)

    if not hasattr(mod, "run"):
        raise NotImplementedError(f"Module {mod_name} does not expose a 'run(df)' function.")

    return mod.run(df, **kwargs)
