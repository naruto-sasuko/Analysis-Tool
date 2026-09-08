"""Scenario 2: NPA Valuation Audit (183 / 548 / 820 Day Check)"""
import os
import datetime
import pandas as pd

a25 = "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
a26 = "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)"
npa, val = "Date of account becoming NPA", "Last Valuation date of the Property"

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s",
    "PAN of First Borrower", "Sanction date", "Sanction amount",
    "Valuation of Property Considered (in Rs) (market value)", npa, a25, a26, val, "Last Valuation amount"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Audits overdue property revaluations on NPA accounts under regulatory 183/548/820 day rules."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in required_columns:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    c_a25 = df[a25].astype(str).str.strip().str.lower()
    c_a26 = df[a26].astype(str).str.strip().str.lower()
    invalid_vals = {"0", "0.0", "", "standard", "nan", "none"}

    valid_mask = (
        df[a25].notna() & df[a26].notna() &
        (~c_a25.isin(invalid_vals)) & (~c_a26.isin(invalid_vals))
    )
    df_npa = df[valid_mask].copy()
    if df_npa.empty:
        return pd.DataFrame(columns=required_columns)

    npa_dt = pd.to_datetime(df_npa[npa], errors="coerce")
    valid_npa_date = npa_dt.notna()
    df_npa = df_npa[valid_npa_date]
    npa_dt = npa_dt[valid_npa_date]

    val_str = df_npa[val].astype(str).str.strip().str.lower()
    is_missing_val = df_npa[val].isna() | val_str.isin(["0", "0.0", "", "nan", "none"])
    val_dt = pd.to_datetime(df_npa[val], errors="coerce")

    substandard = c_a25[df_npa.index] == "sub-standard"
    npa_pre_2025 = npa_dt < pd.Timestamp("2025-03-31")

    rule_1 = substandard & npa_pre_2025 & ((val_dt > npa_dt + pd.Timedelta(days=548)) | is_missing_val)
    rule_2 = (~substandard) & ((val_dt > npa_dt + pd.Timedelta(days=820)) | is_missing_val)

    segregated_df = df_npa[rule_1 | rule_2][required_columns]
    return segregated_df


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "NPA_valuation.xlsx"
    if not os.path.exists(in_f):
        print(f"Error: Could not find input file '{in_f}'")
    else:
        try:
            raw_df = pd.read_excel(in_f, engine="calamine")
        except Exception:
            try:
                raw_df = pd.read_excel(in_f, engine="pyxlsb")
            except Exception:
                raw_df = pd.read_excel(in_f, engine="openpyxl")
        res = run(raw_df)
        try:
            res.to_excel(out_f, index=False)
            print(f"🎉 Saved {len(res)} rows to {out_f}")
        except PermissionError:
            fallback = f"segregated_valuation_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")