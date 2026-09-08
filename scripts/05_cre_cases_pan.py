"""Scenario 5: CRE Cases by PAN (Count >= 3 and Unique Assets >= 3)"""
import os
import datetime
import pandas as pd

pan = "PAN of First Borrower"
asset = "Asset ID"
l_cat = "Loan Category (Housing or Non-Housing)"

cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", pan,
    "Sanction date", "Sanction amount", "Borrower Category (Individual, Non-Individual, Employee)", l_cat,
    "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    "Loan Sub Category (Balance Tranfer or fresh Case)", "LTV (%) on Sanction", "O/S balance as on 31-03-2026 (IND-As)",
    "Provision made 31-03-2025 (%)", "Provision made 31-03-2026 (%)", "Risk Weight % as on 31.03.2025",
    "Risk Weight % as on 31.03.2026", "Address of Security/ Mortgage Property", asset
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Isolates borrower PANs with repeated housing loan accounts (>=3) and >=3 unique mortgaged assets."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    c_pan = df[pan].astype(str).str.strip().str.upper()
    mask = (
        df[l_cat].astype(str).str.strip().str.lower().isin(["housing", "hl", "home loan"]) &
        df[pan].notna() &
        (~c_pan.isin(["0", "0.0", "", "NAN", "NONE"]))
    )
    df_clean = df[mask].copy()
    if df_clean.empty:
        return pd.DataFrame(columns=cols)

    c_pan_clean = df_clean[pan].astype(str).str.strip().str.upper()
    pan_counts = c_pan_clean.groupby(c_pan_clean).transform("count")
    unique_assets = df_clean.groupby(c_pan_clean)[asset].transform("nunique")

    res = df_clean[(pan_counts >= 3) & (unique_assets >= 3)][cols]
    res = res.sort_values(by=pan, ascending=True)
    return res


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "CRE_cases_pan.xlsx"
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
            fallback = f"segregated_pan_asset_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")