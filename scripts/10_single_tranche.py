"""Scenario 10: Single-Tranche / Bullet Payment Construction Loans"""
import os
import datetime
import pandas as pd

f_disb, l_disb = "First Disb. Date", "Last Disb. Date"
status_col = "Disb Status as on 31-03-2026"
purp_col = "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance"

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower",
    "Sanction date", "Sanction amount", "Loan Category (Housing or Non-Housing)", purp_col, status_col,
    f_disb, l_disb, "Total Disb. as on 31-03-2026", "Un-disbursed loan - Partially pending as on 31-03-2026",
    "O/S balance as on 31-03-2026 (IND-As)", "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)",
    "Provision made 31-03-2026 (%)", "RWA Classification as on 31-03-2026 (LTS, HL1, HL2, HL3, HL4, HL5, RHL, OHL, OLA, LAD)",
    "Address of Security/ Mortgage Property", "Asset ID", "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Finds construction/P+C loans disbursed in a single 100% bullet disbursement instead of milestone tranches."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in [status_col, purp_col, f_disb, l_disb]:
        if c not in df.columns:
            df[c] = ""

    status_clean = df[status_col].astype(str).str.strip().str.lower()
    mask_status = status_clean.isin(["fully disbursed", "full", "disbursed"])

    p_clean = df[purp_col].astype(str).str.lower().str.strip()
    p_clean = p_clean.str.replace(r"[\s\+\&/\-_]", "", regex=True)
    mask_purp = p_clean.isin(["construction", "plotconstruction", "pc", "constructionofproperty"])

    candidate_idx = df[mask_status & mask_purp].index
    f_dt = pd.to_datetime(df.loc[candidate_idx, f_disb], errors="coerce", format="mixed", dayfirst=True)
    l_dt = pd.to_datetime(df.loc[candidate_idx, l_disb], errors="coerce", format="mixed", dayfirst=True)
    mask_days = (l_dt - f_dt).dt.days == 0

    res = df.loc[candidate_idx[mask_days]].copy()
    for c in required_columns:
        if c not in res.columns:
            res[c] = ""

    return res[required_columns]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Single_tranche.xlsx"
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
            fallback = f"Single_tranche_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")