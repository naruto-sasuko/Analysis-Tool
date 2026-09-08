"""
Comprehensive verification test suite for Analysis Tool.
Validates imports, error handling, and business logic execution across all three processing modules.
"""

import sys
from pathlib import Path
import pandas as pd
import datetime

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from scripts import script_CRE_kyc, script_UCIC_cases, script_NPA_valuation


def test_cre_kyc():
    print("Testing CRE_kyc module...")
    # Synthetic dataset
    pan_target = "ABCDE1234F"
    pan_other = "XYZPQ5678R"
    data = {
        "Branch": ["B1", "B1", "B1", "B2"],
        "CUST ID/ Unique ID": ["C1", "C1", "C1", "C2"],
        "Loan Account No.": ["L1", "L2", "L3", "L4"],
        "Name of First Borrower/s": ["Borrower 1", "Borrower 1", "Borrower 1", "Borrower 2"],
        "PAN of First Borrower": [pan_target, pan_target, pan_target, pan_other],
        "Sanction date": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"],
        "Sanction amount": [100000, 200000, 300000, 400000],
        "Borrower Category (Individual, Non-Individual, Employee)": ["Individual"] * 4,
        "Loan Category (Housing or Non-Housing)": ["Housing", "home loan", "Housing", "Housing"],
        "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance": ["House Pur"] * 4,
        "Loan Sub Category (Balance Tranfer or fresh Case)": ["fresh Case"] * 4,
        "LTV (%) on Sanction": [75, 80, 70, 60],
        "O/S balance as on 31-03-2026 (IND-As)": [90000, 180000, 270000, 350000],
        "Provision made 31-03-2025 (%)": [0.4, 0.4, 0.4, 0.4],
        "Provision made 31-03-2026 (%)": [0.4, 0.4, 0.4, 0.4],
        "Risk Weight % as on 31.03.2025": [35, 35, 35, 35],
        "Risk Weight % as on 31.03.2026": [35, 35, 35, 35],
        "Address of Security/ Mortgage Property": ["Addr 1", "Addr 2", "Addr 3", "Addr 4"],
        "Asset ID": ["A1", "A2", "A3", "A4"],
    }
    df = pd.DataFrame(data)
    res = script_CRE_kyc.run(df)
    assert len(res) == 3, f"Expected 3 rows for {pan_target}, got {len(res)}"
    assert (res["PAN of First Borrower"] == pan_target).all()
    print("  ✅ CRE_kyc test passed!")


def test_ucic_cases():
    print("Testing UCIC_cases module...")
    # Case 1: Same CUST ID, different PANs
    # Case 2: Same PAN, different CUST IDs
    data = {
        "Branch": ["B1", "B1", "B2", "B2", "B3"],
        "CUST ID/ Unique ID": ["CUST100", "CUST100", "CUST201", "CUST202", "CUST300"],
        "Loan Account No.": ["L10", "L11", "L20", "L21", "L30"],
        "Name of First Borrower/s": ["Alice", "Bob", "Charlie", "Charlie", "David"],
        "PAN of First Borrower": ["PANAAA1111", "PANBBB2222", "PANCCC3333", "PANCCC3333", "PANDDD4444"],
        "Name of Co-borrower/s": ["", "", "", "", ""],
        "PAN of Co-Borrower": ["", "", "", "", ""],
    }
    df = pd.DataFrame(data)
    res = script_UCIC_cases.run(df)
    # CUST100 has 2 PANs (2 rows), PANCCC3333 has 2 CUST IDs (2 rows) -> 4 rows total
    assert len(res) == 4, f"Expected 4 mismatch rows, got {len(res)}"
    print("  ✅ UCIC_cases test passed!")


def test_npa_valuation():
    print("Testing NPA_valuation module...")
    data = {
        "Branch": ["B1", "B2"],
        "CUST ID/ Unique ID": ["C1", "C2"],
        "Loan Account No.": ["L1", "L2"],
        "Name of First Borrower/s": ["Borrower 1", "Borrower 2"],
        "PAN of First Borrower": ["PAN1111", "PAN2222"],
        "Sanction date": ["2020-01-01", "2020-01-01"],
        "Sanction amount": [500000, 500000],
        "Valuation of Property Considered (in Rs) (market value)": [600000, 600000],
        "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)": ["Sub-standard", "D1"],
        "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)": ["Sub-standard", "D1"],
        "Date of account becoming NPA": ["2024-01-01", "2023-01-01"],
        "Last Valuation date of the Property": [
            "2026-01-01",  # > 548 days after 2024-01-01 (731 days overdue) -> flagged
            "2026-01-01",  # > 820 days after 2023-01-01 (1096 days overdue) -> flagged
        ],
        "Last Valuation amount": [550000, 550000],
    }
    df = pd.DataFrame(data)
    res = script_NPA_valuation.run(df)
    assert len(res) == 2, f"Expected 2 overdue valuation rows, got {len(res)}"
    print("  ✅ NPA_valuation test passed!")


def test_empty_and_error_handling():
    print("Testing empty and boundary handling...")
    assert script_CRE_kyc.run(pd.DataFrame()).empty
    assert script_UCIC_cases.run(pd.DataFrame()).empty
    assert script_NPA_valuation.run(pd.DataFrame()).empty

    # Missing required columns should raise ValueError
    try:
        script_CRE_kyc.run(pd.DataFrame({"dummy": [1, 2]}))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        script_UCIC_cases.run(pd.DataFrame({"dummy": [1, 2]}))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    try:
        script_NPA_valuation.run(pd.DataFrame({"dummy": [1, 2]}))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  ✅ Error boundaries passed!")


def test_all_scenarios_registry():
    print("Testing 23-scenario registry and execution interface...")
    from scripts.scenario_registry import (
        SCENARIO_CATALOG,
        get_categories,
        get_scenarios_by_category,
        execute_scenario,
    )

    assert len(SCENARIO_CATALOG) == 23, f"Expected 23 scenarios, found {len(SCENARIO_CATALOG)}"
    cats = get_categories()
    assert len(cats) >= 4, f"Expected at least 4 categories, got {cats}"

    empty_df = pd.DataFrame()
    for sid in SCENARIO_CATALOG:
        res = execute_scenario(sid, empty_df)
        assert isinstance(res, pd.DataFrame), f"Scenario {sid} did not return a DataFrame, got {type(res)}"

    print("  ✅ All 23 scenarios verified and executable via run(df)!")


if __name__ == "__main__":
    test_cre_kyc()
    test_ucic_cases()
    test_npa_valuation()
    test_empty_and_error_handling()
    test_all_scenarios_registry()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

