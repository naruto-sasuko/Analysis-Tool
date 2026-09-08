"""Scenario 13: Over-Disbursed Loans (Total Disbursement > Sanction Amount)"""
import os
import datetime
import pandas as pd

td = "Total Disb. as on 31-03-2026"
sa = "Sanction amount"

cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower", 
    "Sanction date", sa, "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance", 
    "Disb Status as on 31-03-2026", "First Disb. Date", "Last Disb. Date", td, 
    "O/S balance as on 31-03-2026 (IND-As)", "Date of account becoming NPA", 
    "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)", 
    "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)", "Risk Weight % as on 31.03.2026"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Detects underwriting governance violations where cumulative disbursements exceed total sanctioned credit limit."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    c_td = td if td in df.columns else next((c for c in df.columns if "total disb" in c.lower()), td)
    c_sa = sa if sa in df.columns else next((c for c in df.columns if "sanction amount" in c.lower()), sa)

    for c in cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower().replace(" ", "") == c.strip().lower().replace(" ", "")]
            df[c] = df[alt[0]] if alt else ""

    disb = pd.to_numeric(df[c_td].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)
    sanc = pd.to_numeric(df[c_sa].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)

    res = df[disb > sanc].copy()
    for c in cols:
        if c not in res.columns:
            res[c] = ""

    return res[cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Over_Disbursed.xlsx"
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
            fallback = f"Over_Disbursed_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res[cols].to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")