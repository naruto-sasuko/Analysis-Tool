"""Scenario 23: Common CERSAI ID Mapped to Multiple Customer IDs"""
import os
import datetime
import pandas as pd

cersai_col = "CERSAI ID"
cust_col = "CUST ID/ Unique ID"

required_cols = [
    "Branch", cust_col, "Loan Account No.", "Name of First Borrower/s", "PAN of First Borrower",
    "Name of Co-borrower/s", "PAN of Co-Borrower", "Sanction date", "Sanction amount",
    "Loan Category (Housing or Non-Housing)",
    "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    "Total Disb. as on 31-03-2026", "Un-disbursed loan - Partially pending as on 31-03-2026",
    "O/S balance as on 31-03-2026 (IND-As)", "Amount Written off", "Date of W/O",
    "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)",
    "Provision made 31-03-2026 (%)",
    "RWA Classification as on 31-03-2026 (LTS, HL1, HL2, HL3, HL4, HL5, RHL, OHL, OLA, LAD)",
    "Address of Security/ Mortgage Property", "Asset ID",
    "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)",
    "CERSAI ID No", "Date of CERSAI"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Uncovers collateral fraud where a single CERSAI security ID is registered against multiple Customer IDs."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    c_col = cersai_col if cersai_col in df.columns else next((c for c in df.columns if "cersai" in c.lower()), cersai_col)
    u_col = cust_col if cust_col in df.columns else next((c for c in df.columns if "cust" in c.lower()), cust_col)

    for c in required_cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    if c_col not in df.columns or u_col not in df.columns:
        return pd.DataFrame(columns=required_cols)

    c_cersai = df[c_col].astype(str).str.replace(r"\s+", "", regex=True).str.strip().str.upper()
    c_cust = df[u_col].astype(str).str.replace(r"\s+", "", regex=True).str.strip().str.upper()

    invalid_tokens = {"0", "0.0", "", "NAN", "NONE", "NULL", "NA"}
    mask_valid = (~c_cersai.isin(invalid_tokens)) & (~c_cust.isin(invalid_tokens))

    df_valid = df[mask_valid].copy()
    if df_valid.empty:
        return pd.DataFrame(columns=required_cols)

    c_cersai_val = c_cersai[mask_valid]
    c_cust_val = c_cust[mask_valid]

    mask_multi = c_cust_val.groupby(c_cersai_val).transform("nunique") > 1
    res = df_valid[mask_multi].copy()
    if res.empty:
        return pd.DataFrame(columns=required_cols)

    res["_sort_c"] = c_cersai_val[mask_multi]
    res["_sort_u"] = c_cust_val[mask_multi]
    res = res.sort_values(by=["_sort_c", "_sort_u"], ascending=[True, True])

    left_cols = [c for c in required_cols if c in res.columns]
    return res[left_cols]


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "CERSAI_Multiple_Cust.xlsx"
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
            fallback = f"CERSAI_Multiple_Cust_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")