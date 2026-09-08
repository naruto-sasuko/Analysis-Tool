"""Scenario 19: Re-KYC Updation Analysis (Due Date vs Last Updation Check)"""
import os
import datetime
import pandas as pd

sd = "Sanction date"
rc = "Risk Categorization of the Borroweras per KYC on sanction date"
lu = "Date of last KYC risk review/KYC upadation"
dd = "Due date of KYC updation"
kyc_flag = "Timely re-KYC updation"

cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower", 
    sd, "Sanction amount", "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance", 
    "Disb Status as on 31-03-2026", rc, lu, dd, "Revised Risk category as per KYC", kyc_flag
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluates timely re-KYC review against risk-based regulatory review intervals (Low/Med/High)."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    c_sd = sd if sd in df.columns else next((c for c in df.columns if "sanction date" in c.lower()), sd)
    c_rc = rc if rc in df.columns else next((c for c in df.columns if "risk categorization" in c.lower()), rc)
    c_lu = lu if lu in df.columns else next((c for c in df.columns if "last kyc" in c.lower() or "review" in c.lower()), lu)

    for c in [c_sd, c_rc, c_lu]:
        if c not in df.columns:
            df[c] = ""

    s_dt = pd.to_datetime(df[c_sd], errors="coerce", format="mixed", dayfirst=True)
    l_dt = pd.to_datetime(df[c_lu], errors="coerce", format="mixed", dayfirst=True)

    risk_clean = df[c_rc].astype(str).str.strip().str.upper()
    offset_days = risk_clean.map({"LOW": 3652, "MEDIUM": 2922, "HIGH": 730}).fillna(0).astype(int)

    valid_offsets = offset_days > 0
    df[dd] = pd.NaT
    df.loc[valid_offsets & s_dt.notna(), dd] = s_dt[valid_offsets] + pd.to_timedelta(offset_days[valid_offsets], unit="D")

    mask_valid = df[dd].notna() & l_dt.notna()
    df[kyc_flag] = "False"
    df.loc[mask_valid & (df[dd] >= l_dt), kyc_flag] = "True"

    for c in cols:
        if c not in df.columns:
            res_m = [col for col in df.columns if col.strip().lower().replace(" ", "") == c.strip().lower().replace(" ", "")]
            df[c] = df[res_m[0]] if res_m else ""

    return df[cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "KYC_Updation_Analysis.xlsx"
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
            fallback = f"KYC_Updation_Analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")