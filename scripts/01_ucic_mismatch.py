"""Scenario 1: UCIC Mismatch (One-to-Many PAN / Cust ID)"""
import os
import datetime
import pandas as pd

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.",
    "Name of First Borrower/s", "PAN of First Borrower",
    "Name of Co-borrower/s", "PAN of Co-Borrower"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Detects one-to-many anomalies where a single Customer ID is mapped to multiple PANs or vice versa."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    cust_col, pan_col = "CUST ID/ Unique ID", "PAN of First Borrower"

    for c in required_columns:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    clean_pan = df[pan_col].astype(str).str.strip().str.upper()
    clean_cust = df[cust_col].astype(str).str.replace(r"\s+", "", regex=True).str.strip().str.upper()

    mask_valid = df[pan_col].notna() & (~clean_pan.isin(["0", "0.0", "", "NAN", "NONE"]))
    df_sub = df[mask_valid].copy()
    c_pan = clean_pan[mask_valid]
    c_cust = clean_cust[mask_valid]

    case1_mask = c_pan.groupby(c_cust).transform("nunique") > 1
    case2_mask = c_cust.groupby(c_pan).transform("nunique") > 1

    final_mismatches = df_sub[case1_mask | case2_mask].drop_duplicates()
    final_mismatches = final_mismatches.sort_values(by=pan_col, ascending=True)
    return final_mismatches[required_columns]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "UCIC_cases.xlsx"
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
            fallback = f"UCIC_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")