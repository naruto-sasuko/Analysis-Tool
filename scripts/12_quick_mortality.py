"""Scenario 12: Quick Mortality Audit (Sanctioned >= 31-03-2025 & Slipped to Sub-Standard)"""
import os
import datetime
import pandas as pd

sd = "Sanction date"
ac26 = "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)"
ac25 = "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
npa_d = "Date of account becoming NPA"

cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower",
    sd, "Sanction amount", "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    "O/S balance as on 31-03-2026 (IND-As)", npa_d, ac25, ac26, "Risk Weight % as on 31.03.2026"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Identifies freshly sanctioned loans slipping into NPA within their first 12 months of origination."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    clean_ac26 = df[ac26].astype(str).str.lower().str.replace(r"[\s\-]", "", regex=True)
    mask_asset = clean_ac26.str.contains("sub", na=False)

    sub_idx = df[mask_asset].index
    s_dt = pd.to_datetime(df.loc[sub_idx, sd], errors="coerce", format="mixed", dayfirst=True)
    n_dt = pd.to_datetime(df.loc[sub_idx, npa_d], errors="coerce", format="mixed", dayfirst=True)

    cutoff = pd.Timestamp("2025-03-31")
    mask_dates = (n_dt > cutoff) & (s_dt >= cutoff)

    res = df.loc[sub_idx[mask_dates]].copy()
    for c in cols:
        if c not in res.columns:
            res[c] = ""

    return res[cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Quick_mort.xlsx"
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
            fallback = f"Quick_mort_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res[cols].to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")