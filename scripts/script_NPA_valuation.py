import os
import datetime
import pandas as pd


def run(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifies NPA cases where valuation dates violate overdue rules:
    - Sub-standard assets with NPA date prior to 2025-03-31 and valuation overdue > 548 days (or missing)
    - Other non-standard assets with valuation overdue > 820 days (or missing)
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    a25 = "Asset Classification as on 31-03-2025(Standard, Sub-standard, D1,D2,D3, Loss)"
    a26 = "Asset Classification as on 31-03-2026(Standard, Sub-standard, D1,D2,D3, Loss)"
    npa = "Date of account becoming NPA"
    val = "Last Valuation date of the Property"

    required_check = [a25, a26, npa, val]
    missing = [c for c in required_check if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for NPA Valuation: {', '.join(missing)}")

    # 1. Global Pre-filter: Exclude '0', blanks, and 'Standard' from both years
    for col in [a25, a26]:
        df = df[df[col].notna() & (~df[col].astype(str).str.strip().str.lower().isin(["0", "0.0", "", "standard", "nan", "none"]))]

    if df.empty:
        return pd.DataFrame()

    # 2. Parse Dates safely
    df[npa] = pd.to_datetime(df[npa], errors="coerce")
    df = df[df[npa].notna()]  # Remove rows with missing/0 NPA dates

    if df.empty:
        return pd.DataFrame()

    val_raw = df[val].astype(str).str.strip().str.lower()
    is_missing_val = df[val].isna() | val_raw.isin(["0", "0.0", "", "nan", "none"])
    df[val] = pd.to_datetime(df[val], errors="coerce")

    # 3. Apply core business logic parameters simultaneously
    is_substandard = df[a25].astype(str).str.strip().str.lower() == "sub-standard"
    is_npa_pre_2025 = df[npa] < pd.to_datetime("2025-03-31")

    rule_1 = is_substandard & is_npa_pre_2025 & ((df[val] > df[npa] + pd.to_timedelta(548, unit="D")) | is_missing_val)
    rule_2 = (~is_substandard) & ((df[val] > df[npa] + pd.to_timedelta(820, unit="D")) | is_missing_val)

    # 4. Isolate final layout dataset
    required_columns = [
        "Branch", "CUST ID/ Unique ID", "Loan Account No.", "Name of First Borrower/s",
        "PAN of First Borrower", "Sanction date", "Sanction amount",
        "Valuation of Property Considered (in Rs) (market value)", npa, a25, a26, val, "Last Valuation amount"
    ]
    output_cols = [c for c in required_columns if c in df.columns]
    if not output_cols:
        output_cols = df.columns.tolist()

    segregated_df = df[rule_1 | rule_2][output_cols].copy()
    return segregated_df


if __name__ == "__main__":
    input_file = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    output_file = "NPA_valuation.xlsx"
    if not os.path.exists(input_file):
        print(f"File '{input_file}' not found.")
    else:
        try:
            raw_df = pd.read_excel(input_file, engine="calamine")
        except Exception:
            try:
                raw_df = pd.read_excel(input_file, engine="pyxlsb")
            except Exception:
                raw_df = pd.read_excel(input_file, engine="openpyxl")
        res = run(raw_df)
        try:
            res.to_excel(output_file, index=False)
            print(f"🎉 Success! Exported {len(res)} matching cases to {output_file}")
        except PermissionError:
            fallback = f"segregated_valuation_cases_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            res.to_excel(fallback, index=False)
            print(f"⚠️ Locked! File saved instead to fallback file: {fallback}")

