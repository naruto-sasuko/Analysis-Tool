"""Scenario 3: Individual Housing Loan (IHL) to Non-Individual"""
import os
import datetime
import pandas as pd

l_cat = "Loan Category (Housing or Non-Housing)"
b_cat = "Borrower Category (Individual, Non-Individual, Employee)"
name = "Name of First Borrower/s"

cols = [
    "Branch", "CUST ID/ Unique ID", "Loan Account No.", name, "PAN of First Borrower",
    "Sanction date", "Sanction amount", b_cat, l_cat,
    "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
    "Loan Sub Category (Balance Tranfer or fresh Case)", "O/S balance as on 31-03-2026 (IND-As)",
    "Provision made 31-03-2026 (%)", "Risk Weight % as on 31.03.2026",
    "Address of Security/ Mortgage Property", "Asset ID"
]


def run(df: pd.DataFrame) -> pd.DataFrame:
    """Detects Individual Housing Loans erroneously extended to corporate/commercial entities."""
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    for c in cols:
        if c not in df.columns:
            alt = [col for col in df.columns if col.strip().lower() == c.strip().lower()]
            df[c] = df[alt[0]] if alt else ""

    mask_hl = df[l_cat].astype(str).str.strip().str.lower().isin(["housing", "hl", "home loan"])
    mask_ind = df[b_cat].astype(str).str.strip().str.lower() == "individual"

    candidate_idx = df[mask_hl & mask_ind].index
    kw = r"shop|trading|trade|\bltd\b|limited|private|\bpvt\b|company|dairy|garments?|fish|traders"
    name_match = df.loc[candidate_idx, name].astype(str).str.contains(kw, case=False, na=False)

    res = df.loc[candidate_idx[name_match], cols]
    return res


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "IHL_to_non Ind.xlsx"
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
            fallback = f"segregated_borrower_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! Saved to fallback: {fallback}")