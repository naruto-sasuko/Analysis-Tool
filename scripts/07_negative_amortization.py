"""Scenario 7: Negative Amortization Audit"""
import os
import datetime
import pandas as pd

pos_25 = "O/s POS as on 31-03-25"
pos_26 = "O/s POS as on 31-03-26"
asset_25 = "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
asset_26 = "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)"
last_disb = "Last Disb. Date"
status_26 = "Disb Status as on 31-03-2026"

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower",
    "Sanction date", "Sanction amount", "Loan Category (Housing or Non-Housing)",
    "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    status_26, "First Disb. Date", last_disb, "Total Disb. as on 31-03-2025", "Total Disb. as on 31-03-2026",
    "Un-disbursed loan - Partially pending as on 31-03-2026", "Pre-EMI amount", "EMI Amt",
    pos_25, pos_26, "Difference", asset_25, asset_26
]


def find_col(df: pd.DataFrame, kws, fallback):
    for col in df.columns:
        if all(k in col.lower() for k in kws):
            return col
    return fallback


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Identifies standard loans where the principal outstanding increased over the fiscal year."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    c_p25 = find_col(df, ["pos", "25"], pos_25)
    c_p26 = find_col(df, ["pos", "26"], pos_26)
    c_a25 = find_col(df, ["asset", "25"], asset_25)
    c_a26 = find_col(df, ["asset", "26"], asset_26)
    c_ld = find_col(df, ["last", "disb"], last_disb)

    for col_name in [c_p25, c_p26, c_a25, c_a26, c_ld]:
        if col_name not in df.columns:
            df[col_name] = ""

    p25_vals = pd.to_numeric(df[c_p25].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)
    p26_vals = pd.to_numeric(df[c_p26].astype(str).str.replace(",", "", regex=True).str.strip(), errors="coerce").fillna(0)
    diff = (p26_vals - p25_vals).round(2)

    ld_dates = pd.to_datetime(df[c_ld], errors="coerce", format="mixed", dayfirst=True)

    mask = (
        (diff >= 0) &
        ~((p25_vals == 0) & (p26_vals == 0)) &
        (df[c_a25].astype(str).str.strip().str.lower() == "standard") &
        (df[c_a26].astype(str).str.strip().str.lower() == "standard") &
        (ld_dates < pd.Timestamp("2025-03-31"))
    )

    res = df[mask].copy()
    res[pos_25] = p25_vals[mask]
    res[pos_26] = p26_vals[mask]
    res["Difference"] = diff[mask]

    for c in required_columns:
        if c not in res.columns:
            res[c] = ""

    return res[required_columns]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Neg_amort.xlsx"
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
            fallback = f"Neg_amort_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")