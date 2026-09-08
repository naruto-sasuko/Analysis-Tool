"""Scenario 11: CKYC Delay Audit (Disbursed > 10 Days Before CKYC or Status Contradictions)"""
import os
import datetime
import pandas as pd

fd, cd, stat = "First Disb. Date", "CKYC DATE", "CKYC Done (Yes or No)"
purp = "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance"
cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower",
    "Sanction date", "Sanction amount", purp, "Disb Status as on 31-03-2026", fd, stat, cd,
    "CKYC Variance (Days)", "CKYC No."
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Flags loans disbursed >10 days before CKYC registration or contradictory CKYC completion flags."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in cols:
        if c not in df.columns and c != "CKYC Variance (Days)":
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    c_stat = df[stat].astype(str).str.strip().str.lower()
    c_date_str = df[cd].astype(str).str.strip().str.replace(" ", "", regex=False)

    f_dt = pd.to_datetime(df[fd], errors="coerce", dayfirst=True)
    c_dt = pd.to_datetime(df[cd], errors="coerce", dayfirst=True)
    df["CKYC Variance (Days)"] = (c_dt - f_dt).dt.days

    mask_days = df["CKYC Variance (Days)"] > 10
    mask_no = c_stat == "no"
    mask_contradiction = (c_stat == "yes") & (c_dt.isna() | c_date_str.isin(["", "-", "nan", "none"]))

    res = df[mask_days | mask_no | mask_contradiction].copy()
    for c in cols:
        if c not in res.columns:
            res[c] = ""

    return res[cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "CKYC_Cases.xlsx"
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
            fallback = f"CKYC_Exceptions_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res[cols].to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")