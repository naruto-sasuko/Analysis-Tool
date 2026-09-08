"""Scenario 6: Combined LTV Calculations and Multi-Tab Risk Weight Breaches"""
import os
import datetime
import pandas as pd
import numpy as np

pan, asset, acc_col = "PAN of First Borrower", "Asset ID", "Loan Account No."
exp_cols = ["O/S POS as on 31-03-2026", "other charges 31-03-26", "interest accrued as on 31-03-2026"]
val_cols = ["Valuation of Property FY 24-25 (in Rs)", "Valuation of Property FY 25-26 (in Rs)", "Last Valuation amount"]

required_columns = [
    "Branch", "CUST ID/ Unique ID", acc_col, "Name of First Borrower/s", pan, 
    "Sanction date", "Sanction amount", "Borrower Category (Individual, Non-Individual, Employee)", 
    "Loan Category (Housing or Non-Housing)", "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance", 
    "Loan Sub Category (Balance Tranfer or fresh Case)", "LTV (%) on Sanction", "O/S balance as on 31-03-2026 (IND-As)", 
    "interest accrued as on 31-03-2026", "other charges 31-03-26", "O/S POS as on 31-03-2026", 
    "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)", 
    "Provision made 31-03-2025 (%)", "Provision made 31-03-2026 (%)", "Risk Weight % as on 31.03.2025", 
    "Risk Weight % as on 31.03.2026", "Loan Account Count on asset ID", "Address of Security/ Mortgage Property", asset, 
    "Valuation of Property FY 24-25 (in Rs)", "Valuation of Property FY 25-26 (in Rs)", "Last Valuation amount",
    "Total Exposure", "Maximum valuation", "combined LTV"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates borrower exposure across multiple accounts to recalculate true combined LTV and capital risk weights."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in required_columns:
        if c not in df.columns and c not in ["Loan Account Count on asset ID", "Total Exposure", "Maximum valuation", "combined LTV"]:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else 0

    for c in exp_cols + val_cols + ["Risk Weight % as on 31.03.2025", "Risk Weight % as on 31.03.2026"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)

    s_pan = df[pan].astype(str).str.strip()
    s_asset = df[asset].astype(str).str.strip()
    is_p_blank = s_pan.isin(["", "0", "0.0", "nan", "None"])
    is_a_blank = s_asset.isin(["", "0", "0.0", "nan", "None"])

    grp = "PAN_" + s_pan + "_AST_" + s_asset
    grp = np.where(is_p_blank, "AST_" + s_asset, grp)
    grp = np.where(is_a_blank, "PAN_" + s_pan, grp)
    grp = np.where(is_p_blank & is_a_blank, "ACC_" + df[acc_col].astype(str), grp)

    present_exp = [c for c in exp_cols if c in df.columns]
    present_val = [c for c in val_cols if c in df.columns]

    row_exp = df[present_exp].sum(axis=1) if present_exp else pd.Series(0, index=df.index)
    row_max_val = df[present_val].max(axis=1) if present_val else pd.Series(0, index=df.index)

    grp_s = pd.Series(grp, index=df.index)
    df["Total Exposure"] = row_exp.groupby(grp_s).transform("sum")
    df["Maximum valuation"] = row_max_val.groupby(grp_s).transform("max")
    df["Loan Account Count on asset ID"] = df[acc_col].groupby(grp_s).transform("count")

    df["Total Exposure"] = np.where(df["Total Exposure"] == 0, row_exp, df["Total Exposure"])
    df["Maximum valuation"] = np.where(df["Maximum valuation"] == 0, row_max_val, df["Maximum valuation"])

    with np.errstate(divide="ignore", invalid="ignore"):
        df["combined LTV"] = np.where(df["Maximum valuation"] > 0, (df["Total Exposure"] / df["Maximum valuation"]) * 100, 0.0)

    for c in required_columns:
        if c not in df.columns:
            df[c] = ""

    res = df[required_columns].sort_values(by=pan, ascending=True)
    return res


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "segregated_combined_ltv.xlsx"
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
            print(f"🎉 Generated combined LTV output: {out_f}")
        except PermissionError:
            fallback = f"segregated_combined_ltv_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")