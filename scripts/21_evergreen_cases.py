"""Scenario 21: Evergreen Case Audit (Active vs Closed File Cross-Match)"""
import os
import datetime
import pandas as pd

pan1_col, pan2_col = "PAN of First Borrower", "PAN of Co-Borrower"

required_cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s", pan1_col,
    "Name of Co-borrower/s", pan2_col,
    "Sanction date", "Sanction amount", "Loan Category (Housing or Non-Housing)",
    "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance", 
    "Total Disb. as on 31-03-2026", "Un-disbursed loan - Partially pending as on 31-03-2026",
    "O/S balance as on 31-03-2026 (IND-As)", "Amount Written off", "Date of W/O",
    "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)",
    "Provision made 31-03-2026 (%)", "RWA Classification as on 31-03-2026 (LTS, HL1, HL2, HL3, HL4, HL5, RHL, OHL, OLA, LAD)",
    "Address of Security/ Mortgage Property", "Asset ID", "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
]


def clean_p(s):
    res = s.astype(str).str.strip().str.upper()
    return res.replace(["0", "0.0", "", "NAN", "NONE"], pd.NA)


def run(df: pd.DataFrame, df_closed: pd.DataFrame = None) -> pd.DataFrame:
    """Detects evergreening by cross-matching active borrowers against written-off or settled portfolio records."""
    if df is None or df.empty:
        return pd.DataFrame()

    df1 = df.copy()
    df1.columns = df1.columns.astype(str).str.strip()

    for c in required_cols:
        if c not in df1.columns:
            alt = [col for col in df1.columns if col.strip().lower() == c.strip().lower()]
            df1[c] = df1[alt[0]] if alt else ""

    if df_closed is not None and not df_closed.empty:
        df2 = df_closed.copy()
        df2.columns = df2.columns.astype(str).str.strip()
        for c in required_cols:
            if c not in df2.columns:
                alt = [col for col in df2.columns if col.strip().lower() == c.strip().lower()]
                df2[c] = df2[alt[0]] if alt else ""
    else:
        # Check internal write-off / closed indicators if only single file uploaded
        wo_amt = pd.to_numeric(df1["Amount Written off"].astype(str).str.replace(",", "", regex=True), errors="coerce").fillna(0)
        is_wo = (wo_amt > 0) | df1["Date of W/O"].notna()
        if is_wo.any():
            df2 = df1[is_wo].copy()
            df1 = df1[~is_wo].copy()
        else:
            return pd.DataFrame(columns=required_cols)

    df1["P1"] = clean_p(df1[pan1_col])
    df1["P2"] = clean_p(df1[pan2_col]) if pan2_col in df1.columns else pd.NA
    df2["P1"] = clean_p(df2[pan1_col])
    df2["P2"] = clean_p(df2[pan2_col]) if pan2_col in df2.columns else pd.NA

    m1 = pd.merge(df1.dropna(subset=["P1"]), df2.dropna(subset=["P1"]), left_on="P1", right_on="P1", suffixes=("", "_CLOSED"))
    m2 = pd.merge(df1.dropna(subset=["P1"]), df2.dropna(subset=["P2"]), left_on="P1", right_on="P2", suffixes=("", "_CLOSED"))
    m3 = pd.merge(df1.dropna(subset=["P2"]), df2.dropna(subset=["P1"]), left_on="P2", right_on="P1", suffixes=("", "_CLOSED"))

    merged = pd.concat([m1, m2, m3], ignore_index=True)
    if merged.empty:
        return pd.DataFrame(columns=required_cols)

    merged = merged.drop_duplicates(subset=["Loan Account No.", "Loan Account No._CLOSED"])

    left_side = [c for c in required_cols if c in merged.columns]
    right_side = [f"{c}_CLOSED" for c in required_cols if f"{c}_CLOSED" in merged.columns]
    final_out = merged[left_side + right_side].sort_values(by=pan1_col, ascending=True)
    return final_out


if __name__ == "__main__":
    f_active = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    f_closed = "Dump_closed.xlsb" if os.path.exists("Dump_closed.xlsb") else "Dump_closed.xlsx"
    out_f = "Evergreen_Case.xlsx"
    if not os.path.exists(f_active):
        print(f"Error: Could not find required file: '{f_active}'")
    else:
        try:
            d1 = pd.read_excel(f_active, engine="calamine")
        except Exception:
            try:
                d1 = pd.read_excel(f_active, engine="pyxlsb")
            except Exception:
                d1 = pd.read_excel(f_active, engine="openpyxl")
        d2 = None
        if os.path.exists(f_closed):
            try:
                d2 = pd.read_excel(f_closed, engine="calamine")
            except Exception:
                d2 = pd.read_excel(f_closed, engine="openpyxl")
        res = run(d1, d2)
        try:
            res.to_excel(out_f, index=False)
            print(f"🎉 Saved {len(res)} rows to {out_f}")
        except PermissionError:
            fallback = f"Evergreen_Case_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")