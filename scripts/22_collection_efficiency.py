"""Scenario 22: Collection Efficiency (Multi-Tab Monthly Intersections)"""
import os
import pandas as pd

target_sheets = ["May June", "AUG SEPT", "NOV DEC", "FEB MARCH"]


def run(df_or_sheets) -> pd.DataFrame:
    """Evaluates recurring collection delinquency trends across consecutive quarterly cycles."""
    if df_or_sheets is None:
        return pd.DataFrame()

    dfs = []
    if isinstance(df_or_sheets, dict):
        for sheet in target_sheets:
            matched = [s for s in df_or_sheets.keys() if sheet.lower().replace(" ", "") in s.lower().replace(" ", "")]
            if not matched:
                continue
            df = df_or_sheets[matched[0]].copy()
            id_cols = [c for c in df.columns if str(c).strip().upper() in ['LOAN NO.', 'LAN', 'LOAN ACCOUNT NO.', 'LOAN NO']]
            if not id_cols or len(df.columns) < 4:
                continue
            df = df.rename(columns={id_cols[0]: 'COMMON_KEY'})
            c_col, d_col = df.columns[2], df.columns[3]
            v_c = pd.to_numeric(df[c_col], errors='coerce')
            v_d = pd.to_numeric(df[d_col], errors='coerce')
            mask = v_c.between(59, 91) & v_d.between(59, 91)
            df_filtered = df[mask].rename(columns={c: f"{c}_{sheet}" for c in df.columns if c != 'COMMON_KEY'})
            dfs.append(df_filtered)
    elif isinstance(df_or_sheets, pd.DataFrame):
        df = df_or_sheets.copy()
        id_cols = [c for c in df.columns if str(c).strip().upper() in ['LOAN NO.', 'LAN', 'LOAN ACCOUNT NO.', 'LOAN NO']]
        if id_cols and len(df.columns) >= 4:
            df = df.rename(columns={id_cols[0]: 'COMMON_KEY'})
            c_col, d_col = df.columns[2], df.columns[3]
            v_c = pd.to_numeric(df[c_col], errors='coerce')
            v_d = pd.to_numeric(df[d_col], errors='coerce')
            mask = v_c.between(59, 91) & v_d.between(59, 91)
            return df[mask].rename(columns={'COMMON_KEY': 'Loan No. / LAN'})
        return df

    if dfs:
        final_df = dfs[0]
        for nxt in dfs[1:]:
            final_df = pd.merge(final_df, nxt, on='COMMON_KEY', how='inner')
        return final_df.rename(columns={'COMMON_KEY': 'Loan No. / LAN'})

    return pd.DataFrame()


if __name__ == "__main__":
    in_f, out_f = "Collection Efficiency.xlsx", "Segregated_Common_Loans.xlsx"
    if not os.path.exists(in_f):
        print(f"Error: Could not find input file '{in_f}'")
    else:
        try:
            xl = pd.read_excel(in_f, sheet_name=None, engine="calamine")
        except Exception:
            xl = pd.read_excel(in_f, sheet_name=None, engine="openpyxl")
        res = run(xl)
        try:
            res.to_excel(out_f, index=False)
            print(f"🎉 Success! Exported {len(res)} common cases to {out_f}")
        except Exception as e:
            print(f"Export error: {e}")