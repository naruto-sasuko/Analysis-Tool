"""Scenario 9: Plot + Construction (P+C) Segregation"""
import os
import datetime
import pandas as pd

purp_col = "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance"
f_disb_col = "First Disb. Date"
cat_col = "Loan Category (Housing or Non-Housing)"
status_col = "Status in case of Plot purchase/P+C  cases (Open Plot/Constructed)"

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower", 
    "Sanction date", "Sanction amount", cat_col, purp_col, "Disb Status as on 31-03-2026", 
    f_disb_col, "Last Disb. Date", "Total Disb. as on 31-03-2026", 
    "Un-disbursed loan - Partially pending as on 31-03-2026", "Pre-EMI amount", "EMI Amt", 
    "O/S balance as on 31-03-2026 (IND-As)", "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)", 
    "Provision made 31-03-2026 (%)", "RWA Classification as on 31-03-2026 (LTS, HL1, HL2, HL3, HL4, HL5, RHL, OHL, OLA, LAD)", 
    "Address of Security/ Mortgage Property", "Asset ID", "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Isolates Plot + Construction loans disbursed before March 2023 that remain unconstructed or vacant."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    st_col = status_col
    if st_col not in df.columns:
        matched = [c for c in df.columns if "status in case of plot" in c.lower()]
        st_col = matched[0] if matched else st_col

    for c in [purp_col, f_disb_col, cat_col, st_col]:
        if c not in df.columns:
            df[c] = ""

    p_clean = df[purp_col].astype(str).str.replace(" ", "", regex=False).str.lower()
    c_clean = df[cat_col].astype(str).str.strip().str.lower()
    s_clean = df[st_col].astype(str).str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    f_disb_dt = pd.to_datetime(df[f_disb_col], errors="coerce", dayfirst=True)

    mask = (
        p_clean.isin(["p+c", "plot+construction"]) &
        c_clean.isin(["hl", "housing", "home loan"]) &
        s_clean.isin(["", "nan", "none", "open plot", "under construction"]) &
        (f_disb_dt < pd.Timestamp("2023-03-31"))
    )

    res = df[mask].copy()
    for c in required_columns:
        if c not in res.columns:
            res[c] = ""

    return res[required_columns]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "PC_Cases.xlsx"
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
            fallback = f"PC_Construction_Segregation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")