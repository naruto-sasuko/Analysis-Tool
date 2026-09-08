import os
import pandas as pd


def run(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds one-to-many mismatches between alphanumeric Customer IDs and Borrower PANs:
    1. Same Alphanumeric CUST ID with different PANs
    2. Same PAN with different Alphanumeric CUST IDs
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()

    required_columns = [
        "Branch",
        "CUST ID/ Unique ID",
        "Loan Account No.",
        "Name of First Borrower/s",
        "PAN of First Borrower",
        "Name of Co-borrower/s",
        "PAN of Co-Borrower",
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"The following required columns were not found in your Excel file: {', '.join(missing_cols)}. "
            f"Please check column headers."
        )

    cust_col = "CUST ID/ Unique ID"
    pan_col = "PAN of First Borrower"

    # Step 1: Filter out invalid PAN entries (0, blank, nan, none)
    df["Clean_PAN_Str"] = df[pan_col].astype(str).str.strip().str.upper()
    mask_valid_pan = (~df[pan_col].isna()) & (~df["Clean_PAN_Str"].isin(["0", "0.0", "", "NAN", "NONE"]))
    df_filtered = df[mask_valid_pan].copy()

    if df_filtered.empty:
        return pd.DataFrame(columns=required_columns)

    # Step 2: Standardize Alphanumeric Customer IDs
    df_filtered["Clean_Cust_Str"] = (
        df_filtered[cust_col].astype(str).str.replace(r"\s+", "", regex=True).str.strip().str.upper()
    )

    # Step 3: Finding mismatched cases (One-to-Many combinations)
    case1_mask = df_filtered.groupby("Clean_Cust_Str")["Clean_PAN_Str"].transform("nunique") > 1
    df_case1 = df_filtered[case1_mask]

    case2_mask = df_filtered.groupby("Clean_PAN_Str")["Clean_Cust_Str"].transform("nunique") > 1
    df_case2 = df_filtered[case2_mask]

    # Step 4: Merging results and organizing target layout
    final_mismatches = pd.concat([df_case1, df_case2]).drop_duplicates()
    final_mismatches = final_mismatches[required_columns].copy()
    final_mismatches = final_mismatches.sort_values(by=pan_col, ascending=True)

    return final_mismatches


if __name__ == "__main__":
    input_file = "Dump_sample.xlsb" if os.path.exists("Dump_sample.xlsb") else "Dump_sample.xlsx"
    output_file = "UCIC_cases.xlsx"

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
        res.to_excel(output_file, index=False)
        print(f"🎉 Success! Exported {len(res)} rows to {output_file}")

