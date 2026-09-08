"""Scenario 15: KYC Risk Divergence by Customer ID"""
import os
import datetime
import pandas as pd

cust_col = "CUST ID/ Unique ID"
pan_col = "PAN of First Borrower"
risk_col = "Revised Risk category as per KYC"
cols = [
    "Branch", cust_col, "Loan Account No.", "Name of First Borrower/s", pan_col,
    "Sanction date", "Sanction amount", "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    "Disb Status as on 31-03-2026", "Risk Categorization of the Borroweras per KYC on sanction date",
    "Date of last KYC risk review/KYC upadation", risk_col
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Detects divergent KYC risk categorizations under the same Customer Unique ID."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    r_col = risk_col
    if r_col not in df.columns:
        matched = [c for c in df.columns if "revised risk" in c.lower() or "risk category" in c.lower()]
        r_col = matched[0] if matched else r_col

    for c in cols:
        if c not in df.columns and c != risk_col:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    clean_cust = df[cust_col].astype(str).str.strip().str.upper()
    mask_valid = df[cust_col].notna() & (~clean_cust.isin(["0", "0.0", "", "NAN", "NONE"]))

    df_clean = df[mask_valid].copy()
    if df_clean.empty or r_col not in df_clean.columns:
        return pd.DataFrame(columns=cols)

    clean_cust = clean_cust[mask_valid]
    clean_risk = df_clean[r_col].astype(str).str.strip().str.upper()

    mask_divergent = clean_risk.groupby(clean_cust).transform("nunique") > 1
    res = df_clean[mask_divergent].sort_values(by=pan_col, ascending=True)

    for c in cols:
        if c not in res.columns:
            res[c] = ""

    return res[cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "KYC_div_cust.xlsx"
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
            res[cols].to_excel(out_f, index=False)
            print(f"🎉 Saved {len(res)} rows to {out_f}")
        except PermissionError:
            fallback = f"KYC_Risk_Discrepancies_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res[cols].to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")