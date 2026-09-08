"""Scenario 17: Asset Classification Divergence by Customer ID"""
import os
import datetime
import pandas as pd

cust_col = "CUST ID/ Unique ID"
pan_col = "PAN of First Borrower"
ac25 = "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
ac26 = "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)"

cols = [
    "Branch", cust_col, "Loan Account No.", "Name of First Borrower/s", pan_col,
    "Sanction date", "Sanction amount", "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    "Disb Status as on 31-03-2026", "Total Disb. as on 31-03-2026", "O/S balance as on 31-03-2026 (IND-As)",
    ac25, ac26, "Provision made 31-03-2026 (%)", "Risk Weight % as on 31.03.2026",
    "Address of Security/ Mortgage Property", "Asset ID"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Detects conflicting asset classifications (Standard, Sub-standard, D1) under the same Customer ID."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    c_ac26 = ac26 if ac26 in df.columns else next((c for c in df.columns if "asset" in c.lower() and "26" in c.lower()), ac26)
    c_ac25 = ac25 if ac25 in df.columns else next((c for c in df.columns if "asset" in c.lower() and "25" in c.lower()), ac25)

    for c in cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    clean_ac26 = df[c_ac26].astype(str).str.lower().str.replace(r"[\s\-]", "", regex=True)
    mask_active = ~clean_ac26.isin(["closed/writeoff", "closed", "writeoff"])

    clean_cust = df[cust_col].astype(str).str.strip().str.upper()
    mask_valid = mask_active & df[cust_col].notna() & (~clean_cust.isin(["0", "0.0", "", "NAN", "NONE"]))

    df_clean = df[mask_valid].copy()
    if df_clean.empty:
        return pd.DataFrame(columns=cols)

    c_cust = clean_cust[mask_valid]
    c_asset = df_clean[c_ac26].astype(str).str.strip().str.lower()

    mask_divergent = c_asset.groupby(c_cust).transform("nunique") > 1
    res = df_clean[mask_divergent].sort_values(by=pan_col, ascending=True)

    for c in cols:
        if c not in res.columns:
            res[c] = ""

    return res[cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Asset_div_borr_cust.xlsx"
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
            fallback = f"Asset_div_borr_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res[cols].to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")