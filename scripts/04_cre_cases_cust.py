"""Scenario 4: CRE Cases by Customer ID (Count >= 3 and Unique Assets >= 3)"""
import os
import datetime
import pandas as pd

cust = "CUST ID/ Unique ID"
asset = "Asset ID"
l_cat = "Loan Category (Housing or Non-Housing)"

cols = [
    "Branch", cust, "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower",
    "Sanction date", "Sanction amount", "Borrower Category (Individual, Non-Individual, Employee)", l_cat, 
    "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance", 
    "Loan Sub Category (Balance Tranfer or fresh Case)", "LTV (%) on Sanction", "O/S balance as on 31-03-2026 (IND-As)", 
    "Provision made 31-03-2025 (%)", "Provision made 31-03-2026 (%)", "Risk Weight % as on 31.03.2025", 
    "Risk Weight % as on 31.03.2026", "Address of Security/ Mortgage Property", asset
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Identifies commercial real estate concentration where a Customer ID holds >=3 loans with >=3 unique assets."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    c_cust = df[cust].astype(str).str.strip()
    mask = (
        df[l_cat].astype(str).str.strip().str.lower().isin(["housing", "hl", "home loan"]) &
        df[cust].notna() &
        (~c_cust.isin(["0", "0.0", "", "nan", "none"]))
    )
    df_clean = df[mask].copy()
    if df_clean.empty:
        return pd.DataFrame(columns=cols)

    c_cust_clean = df_clean[cust].astype(str).str.strip()
    cust_counts = c_cust_clean.groupby(c_cust_clean).transform("count")
    unique_assets = df_clean.groupby(c_cust_clean)[asset].transform("nunique")

    res = df_clean[(cust_counts >= 3) & (unique_assets >= 3)][cols]
    res[cust] = res[cust].astype(str).str.strip()
    res = res.sort_values(by=cust, ascending=True)
    return res


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "CRE_cases_cust.xlsx"
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
            fallback = f"segregated_cust_asset_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")