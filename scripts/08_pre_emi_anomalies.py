"""Scenario 8: Pre-EMI Anomalies (Sanctioned & Disbursed Pre-2023 with Zero EMI)"""
import os
import datetime
import pandas as pd

sanc_out = "Sanction date"
pre_emi_out = "Pre-EMI amount"
emi_out = "EMI Amt"
a25_out = "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
a26_out = "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)"
p25_out = "O/s POS as on 31-03-25"
p26_out = "O/s POS as on 31-03-26"
ld_out = "Last Disb. Date"
purp_out = "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance"

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower", 
    sanc_out, "Sanction amount", "Loan Category (Housing or Non-Housing)", 
    purp_out, "Disb Status as on 31-03-2026", "First Disb. Date", ld_out, 
    "Total Disb. as on 31-03-2025", "Total Disb. as on 31-03-2026", 
    "Un-disbursed loan - Partially pending as on 31-03-2026", pre_emi_out, emi_out, 
    p25_out, p26_out, "Difference", a25_out, a26_out
]


def get_col(df: pd.DataFrame, kws, fallback):
    for col in df.columns:
        if all(k in col.lower() for k in kws):
            return col
    return fallback


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Flags seasoned loans (>3 years) persisting indefinitely in Pre-EMI status with zero regular EMI amortization."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    c_sanc = get_col(df, ["sanction", "date"], sanc_out)
    c_pre = get_col(df, ["pre", "emi"], pre_emi_out)
    c_emi = get_col(df, ["emi"], emi_out)
    c_a25 = get_col(df, ["asset", "25"], a25_out)
    c_a26 = get_col(df, ["asset", "26"], a26_out)
    c_p25 = get_col(df, ["pos", "25"], p25_out)
    c_p26 = get_col(df, ["pos", "26"], p26_out)
    c_ld = get_col(df, ["last", "disb"], ld_out)
    c_purp = get_col(df, ["purpose"], purp_out)

    for col_name in [c_sanc, c_pre, c_emi, c_a25, c_a26, c_p25, c_p26, c_ld, c_purp]:
        if col_name not in df.columns:
            df[col_name] = ""

    sanc_dt = pd.to_datetime(df[c_sanc], errors="coerce", dayfirst=True)
    ld_dt = pd.to_datetime(df[c_ld], errors="coerce", dayfirst=True)
    pre_vals = pd.to_numeric(df[c_pre].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)
    raw_emi = df[c_emi].astype(str).str.replace(",", "", regex=True).str.strip()
    emi_vals = pd.to_numeric(raw_emi, errors="coerce")

    cutoff = pd.Timestamp("2023-03-31")
    clean_purp = df[c_purp].astype(str).str.replace(" ", "", regex=False).str.lower()

    mask = (
        (sanc_dt < cutoff) &
        (ld_dt < cutoff) &
        (pre_vals > 0) &
        ((emi_vals == 0) | emi_vals.isna() | raw_emi.isin(["", "nan", "none"])) &
        (df[c_a25].astype(str).str.strip().str.lower() == "standard") &
        (df[c_a26].astype(str).str.strip().str.lower() == "standard") &
        (clean_purp != "plot+construction")
    )

    res = df[mask].copy()
    res[pre_emi_out] = pre_vals[mask]
    res[emi_out] = emi_vals[mask].fillna(0)
    res[p25_out] = pd.to_numeric(res[c_p25].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)
    res[p26_out] = pd.to_numeric(res[c_p26].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)
    res["Difference"] = (res[p26_out] - res[p25_out]).round(2)

    for c in required_columns:
        if c not in res.columns:
            res[c] = ""

    return res[required_columns]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Pre_EMI_Anomalies.xlsx"
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
            fallback = f"Pre_EMI_Anomalies_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")