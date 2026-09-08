"""Scenario 20: Multiple Housing Loans in the Same Year (Excluding Balance Transfer)"""
import os
import datetime
import pandas as pd

pan_col = "PAN of First Borrower"
cat_col = "Loan Category (Housing or Non-Housing)"
sanc_date = "Sanction date"
purp_col = "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance"
subcat_col = "Loan Sub Category (Balance Tranfer or fresh Case)"

required_columns = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", pan_col,
    sanc_date, "Sanction amount", cat_col, subcat_col, purp_col, "Total Disb. as on 31-03-2026",
    "Un-disbursed loan - Partially pending as on 31-03-2026", "O/S balance as on 31-03-2026 (IND-As)",
    "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)",
    "Provision made 31-03-2026 (%)", "RWA Classification as on 31-03-2026 (LTS, HL1, HL2, HL3, HL4, HL5, RHL, OHL, OLA, LAD)",
    "Address of Security/ Mortgage Property", "Asset ID", "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)",
    "Pan count"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Flags speculative borrowing where multiple fresh housing loans were sanctioned to the same PAN within 365 days."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in [pan_col, cat_col, sanc_date, subcat_col]:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    cat_clean = df[cat_col].astype(str).str.strip().str.lower()
    mask_housing = cat_clean.isin(["housing", "hl", "housing loan", "home loan"])

    subcat_clean = df[subcat_col].astype(str).str.lower().str.replace(r"\s+", "", regex=True)
    mask_not_bt = ~subcat_clean.str.contains("balancetran|balancetransfer", na=False)

    clean_pan = df[pan_col].astype(str).str.strip().str.upper()
    mask_valid_pan = (~clean_pan.isin(["0", "0.0", "", "NAN", "NONE"])) & df[pan_col].notna()

    df_filtered = df[mask_housing & mask_not_bt & mask_valid_pan].copy()
    if df_filtered.empty:
        return pd.DataFrame(columns=required_columns)

    df_filtered["Clean_PAN"] = clean_pan[df_filtered.index]
    df_filtered[sanc_date] = pd.to_datetime(df_filtered[sanc_date], errors="coerce", format="mixed", dayfirst=True)
    df_filtered = df_filtered[df_filtered[sanc_date].notna()]

    if df_filtered.empty:
        return pd.DataFrame(columns=required_columns)

    df_filtered["Pan count"] = df_filtered.groupby("Clean_PAN")["Clean_PAN"].transform("count")

    s_min = df_filtered.groupby("Clean_PAN")[sanc_date].transform("min")
    s_max = df_filtered.groupby("Clean_PAN")[sanc_date].transform("max")
    mask_group = (df_filtered["Pan count"] >= 2) & ((s_max - s_min).dt.days <= 365)

    res = df_filtered[mask_group].sort_values(by=["Clean_PAN", sanc_date], ascending=[True, True])

    for c in required_columns:
        if c not in res.columns:
            res[c] = ""

    return res[required_columns]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "Multiple_Housing_Loans.xlsx"
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
            res[required_columns].to_excel(out_f, index=False)
            print(f"🎉 Saved {len(res)} rows to {out_f}")
        except PermissionError:
            fallback = f"Multiple_Housing_Loans_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res[required_columns].to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")