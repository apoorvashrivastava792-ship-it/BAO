# """
# compare_csv.py
# --------------
# Compares a Source file (S, caret '^' delimited) and a Target file
# (T, comma delimited) that have different column headers/structures.
 
# Steps:
#   1. Read S with '^' delimiter and T with ',' delimiter.
#   2. Strip any leading '*' from Target's item column (export artifact).
#   3. Map each Source column to its Target counterpart (see COLUMN_MAP).
#   4. Convert Month to a common 'M' + 'MM-MMM-yyyy' format (e.g. M07-Jul-2026).
#   5. Normalize the price columns (float round-trip) so trailing-zero /
#      precision differences don't cause false mismatches, then treat as string.
#   6. Concatenate the 7 mapped columns per row into a pipe-delimited string
#      for both S and T (same structural order).
#   7. Output a single CSV with exactly 3 rows: Source, Target, Match --
#      spread horizontally, one column per row-pair. Unequal row counts are
#      padded with blanks.
 
# Usage:
#     python compare_csv.py source.csv target.csv output.csv
# """
 
# import sys
# import pandas as pd
 
 
# # --------------------------------------------------------------------------
# # Column mapping: Source column name -> Target column name
# # Order matters -- this defines the order of concatenation.
# # --------------------------------------------------------------------------
# COLUMN_MAP = [
#     ("Month",            "Time.[Month]"),
#     ("Item",             "Item.[Planning Item]"),
#     ("ShipToId",         "Region.[Planning Region]"),
#     ("W_EndMarketChild", "Demand Domain.[Planning Demand Domain]"),
#     ("SoldToId",         "Account.[Planning Account]"),
#     ("ShipFrom",         "Location.[Planning Location]"),
#     ("AvgSalesPrice",    "Unit Price WRK"),
# ]
 
# DELIMITER = "|"
 
 
# def format_month(series: pd.Series) -> pd.Series:
#     """
#     Convert a column of dates/month values into the standard
#     'M' + 'MM-MMM-yyyy' string format, e.g. M07-Jul-2026.
#     Values already in that format (Target side) pass through unchanged
#     because to_datetime can parse 'M07-Jul-2023' style strings too.
#     """
#     parsed = pd.to_datetime(series.astype(str).str.lstrip("M"), errors="coerce")
#     formatted = parsed.dt.strftime("M%m-%b-%Y")
#     return formatted.fillna("")
 
 
# def normalize_price(series: pd.Series) -> pd.Series:
#     """
#     Normalize numeric price strings so formatting differences (trailing
#     zeros, differing decimal places) don't cause false mismatches.
#     e.g. '0.012350000000000000' and '0.01235' both become '0.01235'.
#     Non-numeric/blank values are kept as empty strings.
#     """
#     numeric = pd.to_numeric(series, errors="coerce")
 
#     def fmt(x):
#         if pd.isna(x):
#             return ""
#         # Format with enough precision, then strip trailing zeros/dot
#         text = f"{x:.10f}".rstrip("0").rstrip(".")
#         return text if text else "0"
 
#     return numeric.map(fmt)
 
 
# def build_concat_column(df: pd.DataFrame, columns_in_order: list) -> pd.Series:
#     """
#     Given a dataframe and an ordered list of column names, build a single
#     pipe-delimited string per row from those columns (as strings).
#     """
#     str_cols = [df[col].astype(str).str.strip() for col in columns_in_order]
#     concatenated = str_cols[0]
#     for col in str_cols[1:]:
#         concatenated = concatenated.str.cat(col, sep=DELIMITER)
#     return concatenated
 
 
# def read_flexible_csv(path: str) -> pd.DataFrame:
#     """
#     Read a CSV trying a list of likely delimiters. Picks whichever
#     delimiter produces more than 1 column (i.e. actually splits the header).
#     Also strips whitespace/BOM characters from column names.
#     """
#     candidate_seps = ["^", ",", "\t", ";", "|"]
#     best_df = None
#     for sep in candidate_seps:
#         try:
#             df = pd.read_csv(path, sep=sep, dtype=str, engine="python")
#         except Exception:
#             continue
#         if df.shape[1] > 1:
#             best_df = df
#             break
#     if best_df is None:
#         # Fall back to comma so the error message below is meaningful
#         best_df = pd.read_csv(path, sep=",", dtype=str, engine="python")
 
#     # Clean up column names: strip whitespace and BOM artifacts
#     best_df.columns = [str(c).strip().lstrip("\ufeff") for c in best_df.columns]
#     return best_df
 
 
# def require_column(df: pd.DataFrame, col_name: str, file_label: str):
#     """Raise a clear, actionable error if an expected column is missing."""
#     if col_name not in df.columns:
#         raise KeyError(
#             f"\nColumn '{col_name}' not found in {file_label}.\n"
#             f"Columns actually found in {file_label}: {list(df.columns)}\n"
#             f"Fix: update COLUMN_MAP in the script to match the real header name above."
#         )
 
 
# def main(source_path: str, target_path: str, output_path: str):
#     print("[Step 1/8] Reading source and target files...")
#     source_df = read_flexible_csv(source_path)
#     target_df = read_flexible_csv(target_path)
#     print(f"[Step 1/8] Done. Source rows: {len(source_df)}, Target rows: {len(target_df)}")
 
#     print("[Step 2/8] Validating that all mapped columns exist...")
#     for src_col, tgt_col in COLUMN_MAP:
#         require_column(source_df, src_col, "source.csv")
#         require_column(target_df, tgt_col, "target.csv")
#     print("[Step 2/8] Done. All expected columns found.")
 
#     print("[Step 3/8] Cleaning Target item column (stripping leading '*')...")
#     item_col = "Item.[Planning Item]"
#     target_df[item_col] = target_df[item_col].astype(str).str.lstrip("*").str.strip()
#     print("[Step 3/8] Done.")
 
#     print("[Step 4/8] Formatting Month columns to 'M' + 'MM-MMM-yyyy'...")
#     source_df["Month"] = format_month(source_df["Month"])
#     target_df["Time.[Month]"] = format_month(target_df["Time.[Month]"])
#     print("[Step 4/8] Done.")
 
#     print("[Step 5/8] Normalizing price columns...")
#     source_df["AvgSalesPrice"] = normalize_price(source_df["AvgSalesPrice"])
#     target_df["Unit Price WRK"] = normalize_price(target_df["Unit Price WRK"])
#     print("[Step 5/8] Done.")
 
#     print("[Step 6/8] Concatenating mapped columns per row...")
#     source_cols_in_order = [pair[0] for pair in COLUMN_MAP]
#     target_cols_in_order = [pair[1] for pair in COLUMN_MAP]
#     source_concat = build_concat_column(source_df, source_cols_in_order)
#     target_concat = build_concat_column(target_df, target_cols_in_order)
#     print("[Step 6/8] Done.")
 
#     print("[Step 7/8] Aligning row counts and comparing Source vs Target...")
#     max_len = max(len(source_concat), len(target_concat))
#     source_concat = source_concat.reindex(range(max_len)).fillna("")
#     target_concat = target_concat.reindex(range(max_len)).fillna("")
#     match_flags = source_concat == target_concat
#     match_count = int(match_flags.sum())
#     print(f"[Step 7/8] Done. {match_count} of {max_len} rows matched.")
 
#     print("[Step 8/8] Writing output file...")
#     output_df = pd.DataFrame(
#         [source_concat.values, target_concat.values, match_flags.values],
#         index=["Source", "Target", "Match"],
#     )
#     output_df.columns = [f"Row_{i+1}" for i in range(max_len)]
#     output_df.to_csv(output_path, index=True)
#     print(f"[Step 8/8] Done. Output written to: {output_path}")
 
 
# if __name__ == "__main__":
#     if len(sys.argv) != 4:
#         print("Usage: python compare_csv.py <source.csv> <target.csv> <output.csv>")
#         sys.exit(1)
 
#     main(sys.argv[1], sys.argv[2], sys.argv[3])

#     # need to create a rejeted record csv 
    

# --testing for the new condition 

"""
compare_csv.py
--------------
Reconciles a Source file (S) and a Target file (T) that use different
column headers/structures, by MATCHING ROWS ON CONTENT (a business key),
not on row position. This is the correct approach when the two files list
the same kind of records but in a different order and/or different subset.

Key used for matching (6 fields, in this order):
    Month | Item | ShipToId/Region | EndMarketChild/DemandDomain
    | SoldToId/Account | ShipFrom/Location

Price (AvgSalesPrice / Unit Price WRK) is compared SEPARATELY, only for
keys that exist in both files -- since price is the value being checked,
not part of the identity of the record.

Output: one row per unique key found in either file, with columns:
    Key, Source_Price, Target_Price, Present_In, Price_Match

Usage:
    python compare_csv.py source.csv target.csv output.csv
"""

import sys
import pandas as pd


# --------------------------------------------------------------------------
# Key columns used to MATCH a Source row to a Target row (identity fields).
# Order matters -- this defines how the Key string is built.
# --------------------------------------------------------------------------
KEY_COLUMN_MAP = [
    ("Month", "Time.[Month]"),
    ("Item", "Item.[Planning Item]"),
    ("ShipToId", "Region.[Planning Region]"),
    ("W_EndMarketChild", "Demand Domain.[Planning Demand Domain]"),
    ("SoldToId", "Account.[Planning Account]"),
    ("ShipFrom", "Location.[Planning Location]"),
]

# The value being reconciled (NOT part of the matching key).
PRICE_COLUMN_MAP = ("AvgSalesPrice", "Unit Price WRK")

DELIMITER = "|"


def read_flexible_csv(path: str) -> pd.DataFrame:
    """Read a CSV, auto-detecting the delimiter from common candidates."""
    candidate_seps = ["^", ",", "\t", ";", "|"]
    best_df = None
    for sep in candidate_seps:
        try:
            df = pd.read_csv(path, sep=sep, dtype=str, engine="python")
        except Exception:
            continue
        if df.shape[1] > 1:
            best_df = df
            break
    if best_df is None:
        best_df = pd.read_csv(path, sep=",", dtype=str, engine="python")
    best_df.columns = [str(c).strip().lstrip("\ufeff") for c in best_df.columns]
    return best_df


def require_column(df: pd.DataFrame, col_name: str, file_label: str):
    """Raise a clear, actionable error if an expected column is missing."""
    if col_name not in df.columns:
        raise KeyError(
            f"\nColumn '{col_name}' not found in {file_label}.\n"
            f"Columns actually found in {file_label}: {list(df.columns)}\n"
            f"Fix: update KEY_COLUMN_MAP / PRICE_COLUMN_MAP to match the real header name above."
        )


def format_month(series: pd.Series) -> pd.Series:
    """Convert dates/month values to 'M' + 'MM-MMM-yyyy', e.g. M07-Jul-2026."""
    parsed = pd.to_datetime(series.astype(str).str.lstrip("M"), errors="coerce")
    formatted = parsed.dt.strftime("M%m-%b-%Y")
    return formatted.fillna("")


def normalize_price(series: pd.Series) -> pd.Series:
    """Normalize numeric price strings so trailing-zero/precision
    differences don't cause false mismatches."""
    numeric = pd.to_numeric(series, errors="coerce")

    def fmt(x):
        if pd.isna(x):
            return ""
        text = f"{x:.10f}".rstrip("0").rstrip(".")
        return text if text else "0"

    return numeric.map(fmt)


def build_key(df: pd.DataFrame, columns_in_order: list) -> pd.Series:
    """Build a single pipe-delimited key string per row from given columns."""
    str_cols = [df[col].astype(str).str.strip() for col in columns_in_order]
    key = str_cols[0]
    for col in str_cols[1:]:
        key = key.str.cat(col, sep=DELIMITER)
    return key


def main(source_path: str, target_path: str, output_path: str):
    print("[Step 1/7] Reading source and target files...")
    source_df = read_flexible_csv(source_path)
    target_df = read_flexible_csv(target_path)
    print(f"[Step 1/7] Done. Source rows: {len(source_df)}, Target rows: {len(target_df)}")

    print("[Step 2/7] Validating that all mapped columns exist...")
    for src_col, tgt_col in KEY_COLUMN_MAP + [PRICE_COLUMN_MAP]:
        require_column(source_df, src_col, "source.csv")
        require_column(target_df, tgt_col, "target.csv")
    print("[Step 2/7] Done. All expected columns found.")

    print("[Step 3/7] Cleaning Target item column (stripping leading '*')...")
    item_col = "Item.[Planning Item]"
    target_df[item_col] = target_df[item_col].astype(str).str.lstrip("*").str.strip()
    print("[Step 3/7] Done.")

    print("[Step 4/7] Formatting Month columns and normalizing price columns...")
    source_df["Month"] = format_month(source_df["Month"])
    target_df["Time.[Month]"] = format_month(target_df["Time.[Month]"])
    source_df["AvgSalesPrice"] = normalize_price(source_df["AvgSalesPrice"])
    target_df["Unit Price WRK"] = normalize_price(target_df["Unit Price WRK"])
    print("[Step 4/7] Done.")

    print("[Step 5/7] Building match keys for both files...")
    source_key_cols = [pair[0] for pair in KEY_COLUMN_MAP]
    target_key_cols = [pair[1] for pair in KEY_COLUMN_MAP]
    source_df["_Key"] = build_key(source_df, source_key_cols)
    target_df["_Key"] = build_key(target_df, target_key_cols)
    print("[Step 5/7] Done.")

    # print("[Step 6/7] Matching Source and Target by key (outer join)...")
    # src_slim = source_df[["_Key", "AvgSalesPrice"]].rename(
    #     columns={"AvgSalesPrice": "Source_Price"}
    # )
    # tgt_slim = target_df[["_Key", "Unit Price WRK"]].rename(
    #     columns={"Unit Price WRK": "Target_Price"}
    # )

    # merged = src_slim.merge(
    #     tgt_slim, on="_Key", how="outer", indicator=True
    # )

    # present_map = {
    #     "both": "Both",
    #     "left_only": "Source Only",
    #     "right_only": "Target Only",
    # }
    # # merged["Present_In"] = merged["_merge"].map(present_map)
    # # applying present in condition testing
    # merged["Present_In"] = merged["_merge"].map(present_map)

    # mask = (
    #     (merged["Present_In"] == "Both") &
    #     (merged["Source_Price"] != merged["Target_Price"])
    # )

    # merged.loc[mask, "Present_In"] = "Price Mismatch"

    # merged["Price_Match"] = (merged["Present_In"] == "Both") & (
    #     merged["Source_Price"] == merged["Target_Price"]
    # )
    # merged = merged.drop(columns=["_merge"])
    # merged = merged.rename(columns={"_Key": "Key"})

    # both_count = int((merged["Present_In"] == "Both").sum())
    # src_only_count = int((merged["Present_In"] == "Source Only").sum())
    # tgt_only_count = int((merged["Present_In"] == "Target Only").sum())
    # match_count = int(merged["Price_Match"].sum())
    # print(
    #     f"[Step 6/7] Done. {both_count} keys in both files "
    #     f"({match_count} with matching price), "
    #     f"{src_only_count} Source-only, {tgt_only_count} Target-only."
    # )
    print("[Step 6/7] Matching Source and Target by key (outer join)...")

    src_slim = source_df[["_Key", "AvgSalesPrice"]].rename(
        columns={"AvgSalesPrice": "Source_Price"}
    )

    tgt_slim = target_df[["_Key", "Unit Price WRK"]].rename(
        columns={"Unit Price WRK": "Target_Price"}
    )

    merged = src_slim.merge(
        tgt_slim,
        on="_Key",
        how="outer",
        indicator=True
    )

    # Clean prices
    merged["Source_Price"] = (
        merged["Source_Price"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    merged["Target_Price"] = (
        merged["Target_Price"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # Key presence validation
    present_map = {
        "both": "Both",
        "left_only": "Source Only",
        "right_only": "Target Only",
    }

    merged["Present_In"] = merged["_merge"].map(present_map).astype(str)

    # Reconciliation status
    merged["Status"] = merged["Present_In"]

    price_match_mask = (
        (merged["Present_In"] == "Both") &
        (merged["Source_Price"] == merged["Target_Price"])
    )

    price_mismatch_mask = (
        (merged["Present_In"] == "Both") &
        (merged["Source_Price"] != merged["Target_Price"])
    )

    merged.loc[price_match_mask, "Status"] = "Price Match"
    merged.loc[price_mismatch_mask, "Status"] = "Price Mismatch"

    merged["Price_Match"] = price_match_mask
    # test3
    # Key validation
    merged["Key_Validation"] = "Valid"

    merged.loc[
        merged["Present_In"] != "Both",
        "Key_Validation"
    ] = "Missing"
    # new reject 
    # Reject reason
    merged["Reject_Reason"] = ""

    merged.loc[
        merged["Present_In"] == "Source Only",
        "Reject_Reason"
    ] = "Key exists only in Source"

    merged.loc[
        merged["Present_In"] == "Target Only",
        "Reject_Reason"
    ] = "Key exists only in Target"

    merged.loc[
        merged["Status"] == "Price Mismatch",
        "Reject_Reason"
    ] = "Price mismatch between Source and Target"
# test ends here 

    print("\n===== RECONCILIATION SUMMARY =====")
    print(f"Price Matches    : {int(price_match_mask.sum())}")
    print(f"Price Mismatches : {int(price_mismatch_mask.sum())}")
    print(f"Source Only      : {int((merged['Present_In'] == 'Source Only').sum())}")
    print(f"Target Only      : {int((merged['Present_In'] == 'Target Only').sum())}")

    if price_mismatch_mask.any():
        print("\nSample mismatches:")
        print(
            merged.loc[
                price_mismatch_mask,
                ["_Key", "Source_Price", "Target_Price"]
            ].head(10)
        )

    merged = merged.drop(columns=["_merge"])
    merged = merged.rename(columns={"_Key": "Key"})

    both_count = int((merged["Present_In"] == "Both").sum())
    src_only_count = int((merged["Present_In"] == "Source Only").sum())
    tgt_only_count = int((merged["Present_In"] == "Target Only").sum())
    match_count = int(price_match_mask.sum())
    mismatch_count = int(price_mismatch_mask.sum())

    print(
        f"[Step 6/7] Done. "
        f"{both_count} keys found in both files, "
        f"{match_count} price matches, "
        f"{mismatch_count} price mismatches, "
        f"{src_only_count} source-only, "
        f"{tgt_only_count} target-only."
    )
    # Create rejected records file
    rejected_df = merged[
        merged["Reject_Reason"] != ""
    ].copy()

    rejected_output = "rejected_records.csv"

    rejected_df.to_csv(rejected_output, index=False)

    print(
        f"Rejected records written to: {rejected_output}"
    )

    print(
        f"Rejected record count: {len(rejected_df)}"
    )
    print("[Step 7/7] Writing output file...")
    merged.to_csv(output_path, index=False)
    print(f"[Step 7/7] Done. Output written to: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python compare_csv.py <source.csv> <target.csv> <output.csv>")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
