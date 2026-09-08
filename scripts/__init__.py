"""
Scripts package for Excel Loan Portfolio Analysis Tool.
Exposes processing routines for CRE KYC, UCIC Cases, and NPA Valuation,
along with full alias coverage for all naming and casing conventions.
"""

from . import script_CRE_kyc
from . import script_UCIC_cases
from . import script_NPA_valuation

# Robust aliases for backward compatibility with all casing conventions and rename patterns
Script_CRE_kyc = script_CRE_kyc
script_cre_kyc = script_CRE_kyc
CRE_kyc = script_CRE_kyc
cre_kyc = script_CRE_kyc

Script_UCIC_cases = script_UCIC_cases
script_ucic_cases = script_UCIC_cases
UCIC_cases = script_UCIC_cases
ucic_cases = script_UCIC_cases

Script_NPA_valuation = script_NPA_valuation
script_npa_valuation = script_NPA_valuation
NPA_valuation = script_NPA_valuation
npa_valuation = script_NPA_valuation

from .scenario_registry import (
    SCENARIO_CATALOG,
    get_categories,
    get_scenarios_by_category,
    get_scenario,
    execute_scenario,
)

__all__ = [
    "script_CRE_kyc",
    "Script_CRE_kyc",
    "script_cre_kyc",
    "CRE_kyc",
    "cre_kyc",
    "script_UCIC_cases",
    "Script_UCIC_cases",
    "script_ucic_cases",
    "UCIC_cases",
    "ucic_cases",
    "script_NPA_valuation",
    "Script_NPA_valuation",
    "script_npa_valuation",
    "NPA_valuation",
    "npa_valuation",
    "SCENARIO_CATALOG",
    "get_categories",
    "get_scenarios_by_category",
    "get_scenario",
    "execute_scenario",
]


