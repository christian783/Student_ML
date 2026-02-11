#!/usr/bin/env python3
"""
add_normal_column.py

Reads an input CSV and writes an output CSV with an added column "normal".
"normal" is "yes" if all validations pass, otherwise "no".

Validations implemented:
- Required columns: study_hours, sleep_hours (case-insensitive search).
- study_hours must be numeric and in [0, 11].
- sleep_hours must be numeric and in [3, 10].
- study_hours + sleep_hours must be <= 24.
- If student has extracurricular activities (detected from a column named like
  "extracurricular"/"activities"/"has_activities" or given explicitly), then
  study_hours + sleep_hours must be < 24 (cannot equal 24).
- Missing or non-numeric values fail validation.
- Extra validations: negative values fail (covered by the numeric range checks),
  and columns are detected case-insensitively.

Usage:
    python add_normal_column.py input.csv output.csv
Optional args:
    --activities-col NAME   Specify column name for extracurricular flag if auto-detection fails.
    --verbose               Print row-level warnings and summary.
"""

import csv
import sys
import argparse
import os

# Acceptable truthy values for the extracurricular column
TRUTHY = {"1", "true", "t", "yes", "y", "on"}
FALSY = {"0", "false", "f", "no", "n", "off", ""}


def find_column(names, candidates):
    """
    Find the first column name from candidates that appears in names (case-insensitive).
    Returns the actual name from names or None.
    """
    lower_to_name = {n.lower(): n for n in names}
    for c in candidates:
        if c.lower() in lower_to_name:
            return lower_to_name[c.lower()]
    return None


def parse_float(value):
    if value is None:
        return None
    v = str(value).strip()
    if v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def parse_bool(value):
    if value is None:
        return None
    v = str(value).strip().lower()
    if v in TRUTHY:
        return True
    if v in FALSY:
        return False
    # If ambiguous (like "maybe"), return None
    return None


def is_normal_row(row, col_study, col_sleep, col_activity, verbose=False, rownum=None):
    """
    Return (bool is_normal, list_of_reasons_if_not).
    """
    reasons = []

    s_raw = row.get(col_study)
    sl_raw = row.get(col_sleep)
    # Parse numeric
    s = parse_float(s_raw)
    sl = parse_float(sl_raw)
    if s is None:
        reasons.append(f"study_hours missing/invalid ({s_raw})")
    if sl is None:
        reasons.append(f"sleep_hours missing/invalid ({sl_raw})")

    # If numeric present, check ranges
    if s is not None:
        if s < 0:
            reasons.append(f"study_hours negative ({s})")
        if s < 0 or s > 11:
            reasons.append(f"study_hours out of range [0,11] ({s})")
    if sl is not None:
        if sl < 0:
            reasons.append(f"sleep_hours negative ({sl})")
        if sl < 3 or sl > 10:
            reasons.append(f"sleep_hours out of range [3,10] ({sl})")

    # If either missing / invalid, it's not normal
    if s is None or sl is None:
        if verbose and rownum is not None:
            print(f"Row {rownum}: not normal -> {', '.join(reasons)}")
        return False, reasons

    total = s + sl

    # Sum check
    if total > 24:
        reasons.append(f"study+sleep exceeds 24 (sum={total})")

    # Determine extracurricular flag
    if col_activity is not None:
        activity_raw = row.get(col_activity)
        act = parse_bool(activity_raw)
        if act is None:
            # Ambiguous: treat ambiguous as True? We choose to treat ambiguous as False but warn.
            reasons.append(f"extracurricular value ambiguous ({activity_raw})")
            act = False
    else:
        act = False  # no column detected -> assume no extracurriculars

    if act and abs(total - 24) < 1e-9:
        # if extracurricular activities present, sum can't be equal to 24
        reasons.append("study+sleep equals 24 but student has extracurricular activities")

    if reasons:
        if verbose and rownum is not None:
            print(f"Row {rownum}: not normal -> {', '.join(reasons)}")
        return False, reasons

    # All checks passed
    if verbose and rownum is not None:
        print(f"Row {rownum}: normal")
    return True, []


def main():
    parser = argparse.ArgumentParser(description="Add 'normal' column to CSV according to rules.")
    parser.add_argument("input_csv", help="Input CSV file path")
    parser.add_argument("output_csv", help="Output CSV file path (will be overwritten)")
    parser.add_argument("--activities-col", help="Column name to use for extracurricular activities flag (optional)")
    parser.add_argument("--verbose", action="store_true", help="Print details during processing")
    args = parser.parse_args()

    in_path = args.input_csv
    out_path = args.output_csv

    if not os.path.exists(in_path):
        print(f"Error: input file not found: {in_path}", file=sys.stderr)
        sys.exit(2)

    with open(in_path, newline='', encoding='utf-8') as inf:
        reader = csv.DictReader(inf)
        rows = list(reader)
        if not reader.fieldnames:
            print("Error: input CSV has no header", file=sys.stderr)
            sys.exit(2)
        fieldnames = list(reader.fieldnames)

    # Detect study and sleep column names (case-insensitive)
    col_study = find_column(fieldnames, ["study_hours", "study hours", "study"])
    col_sleep = find_column(fieldnames, ["sleep_hours", "sleep hours", "sleep"])
    col_activity = None
    if args.activities_col:
        # If user specified name, check if it exists
        if args.activities_col in fieldnames:
            col_activity = args.activities_col
        else:
            # try case-insensitive match
            matched = find_column(fieldnames, [args.activities_col])
            if matched:
                col_activity = matched
            else:
                print(f"Warning: activities column '{args.activities_col}' not found; treating as no activities", file=sys.stderr)
                col_activity = None
    else:
        # auto-detect a likely activities column
        col_activity = find_column(fieldnames, ["extracurricular", "has_extracurricular", "activities", "has_activities", "extracurriculars", "has_extracurriculars"])

    if col_study is None or col_sleep is None:
        print("Error: could not find required columns for study_hours and/or sleep_hours. "
              "Expected column names like 'study_hours' and 'sleep_hours' (case-insensitive).", file=sys.stderr)
        print("Found columns:", ", ".join(fieldnames), file=sys.stderr)
        sys.exit(2)

    # Prepare output fieldnames: keep existing order, append "normal" if not present
    out_fieldnames = list(fieldnames)
    if "normal" not in out_fieldnames:
        out_fieldnames.append("normal")

    normal_yes = 0
    normal_no = 0
    total_rows = len(rows)

    # Process rows
    for i, row in enumerate(rows, start=1):
        is_norm, reasons = is_normal_row(row, col_study, col_sleep, col_activity, verbose=args.verbose, rownum=i)
        row["normal"] = "yes" if is_norm else "no"
        if is_norm:
            normal_yes += 1
        else:
            normal_no += 1

    # Write output CSV
    with open(out_path, "w", newline='', encoding='utf-8') as outf:
        writer = csv.DictWriter(outf, fieldnames=out_fieldnames)
        writer.writeheader()
        for row in rows:
            # Ensure all fieldnames present
            out_row = {k: row.get(k, "") for k in out_fieldnames}
            writer.writerow(out_row)

    # Summary
    print(f"Wrote {out_path}: {total_rows} rows (normal=yes: {normal_yes}, normal=no: {normal_no})")
    if col_activity:
        print(f"Using activity column: {col_activity}")
    else:
        print("No activity column detected; treating all students as having no extracurricular activities by default.")


if __name__ == "__main__":
    main()