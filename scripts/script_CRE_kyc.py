import os
import datetime
import pandas as pd


def run(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters housing/home loans, isolates borrowers with repeated PANs (>=3)
    and multiple unique assets (>=3), and returns sorted cases.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    pan = "PAN of First Borrower"
    asset = "Asset ID"
    l_cat = "Loan Category (Housing or Non-Housing)"

    required_check = [pan, asset, l_cat]
    missing = [c for c in required_check if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for CRE_kyc: {', '.join(missing)}")

    cols = [
        "Branch",
        "CUST ID/ Unique ID",
        "Loan Account No.",
        "Name of First Borrower/s",
        pan,
        "Sanction date",
        "Sanction amount",
        "Borrower Category (Individual, Non-Individual, Employee)",
        l_cat,
        "Purpose (Plot pur, P+C, House Pur, Rennovation, Extension, Top up, LAP, BuilderFinance",
        "Loan Sub Category (Balance Tranfer or fresh Case)",
        "LTV (%) on Sanction",
        "O/S balance as on 31-03-2026 (IND-As)",
        "Provision made 31-03-2025 (%)",
        "Provision made 31-03-2026 (%)",
        "Risk Weight % as on 31.03.2025",
        "Risk Weight % as on 31.03.2026",
        "Address of Security/ Mortgage Property",
        asset,
    ]
    # Keep whichever target columns are present in the dataframe
    output_cols = [c for c in cols if c in df.columns]
    if not output_cols:
        output_cols = df.columns.tolist()

    # 1. Base Cleanup: Housing or Home Loan only, drop rows where PAN is '0' or blank
    valid_category = df[l_cat].astype(str).str.strip().str.lower().isin(["housing", "home loan"])
    valid_pan = df[pan].notna() & (~df[pan].astype(str).str.strip().isin(["0", "0.0", "", "nan", "none"]))
    df_clean = df[valid_category & valid_pan].copy()

    if df_clean.empty:
        return pd.DataFrame(columns=output_cols)

    # 2. Grouping logic to count instances and find unique variations per PAN
    pan_counts = df_clean.groupby(pan)[pan].transform("count")
    unique_assets = df_clean.groupby(pan)[asset].transform("nunique")

    # 3. Slice dataset matching criteria and sort by PAN in ascending order
    res = df_clean[(pan_counts >= 3) & (unique_assets >= 3)][output_cols]
    res = res.sort_values(by=pan, ascending=True)

    return res


if __name__ == "__main__":
    in_f = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    out_f = "CRE_cases_pan.xlsx"
    if not os.path.exists(in_f):
        print(f"File '{in_f}' not found in current directory.")
    else:
        try:
            raw_df = pd.read_excel(in_f, engine="calamine")
        except Exception:
            try:
                raw_df = pd.read_excel(in_f, engine="pyxlsb")
            except Exception:
                raw_df = pd.read_excel(in_f, engine="openpyxl")
        result = run(raw_df)
        try:
            result.to_excel(out_f, index=False)
        except PermissionError:
            out_f = f"segregated_pan_asset_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            result.to_excel(out_f, index=False)
        print(f"🎉 Processed, sorted, and isolated {len(result)} matching cases to {out_f}.")

