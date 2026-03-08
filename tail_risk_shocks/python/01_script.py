"""
SCRIPT 01: DATA DOWNLOAD  (FRED + LSEG EXCEL)
=============================================
Downloads daily financial variables for the thesis VAR model.

Sources: FRED (online) and LSEG Excel workbook only.

─────────────────────────────────────────────────────────────────────────────
FINAL VARIABLE SET
─────────────────────────────────────────────────────────────────────────────
BASELINE VAR — 12 variables (analytical sample: 1997-01-02 → 2024-12-31)

  Channel           Variable   Source    Notes
  ──────────────── ─────────  ────────  ──────────────────────────────────
  Equity (broad)   SP500      LSEG      S&P 500 index level
  Equity (fin.)    SP5EFIN    LSEG      S&P 500 Financial Sector index
  Volatility       VIX        FRED      CBOE VIX
  Credit risk      CSPREAD    FRED      BBB yield − AAA yield (computed)
                   AAA        FRED      ICE BofA AAA corporate yield
                   BBB        FRED      ICE BofA BBB corporate yield
  Interest rates   DGS10      FRED      10-year Treasury yield
                   SLOPE      FRED      DGS10 − DGS2 (term spread, computed)
  FX / Dollar      DXY        LSEG      US Dollar Index
                   EURUSD     LSEG      EUR/USD spot rate
  Money market     DTB3       FRED      3-month T-Bill rate
                   FEDFUNDS   FRED      Fed Funds rate (daily DFF)

ROBUSTNESS — 5 variables (kept in master, excluded from baseline VAR)

  Variable   Source    Notes
  ─────────  ────────  ──────────────────────────────────────────────────
  DAX        LSEG      German equity index (global dimension)
  XLF        LSEG      Financial Select Sector ETF (from 1998-12-22)
  DGS2       FRED      2-year Treasury (component of SLOPE, kept for transparency)
  TED        FRED      TED spread — DISCONTINUED Jan 2023; use 1990-2022 subsample only

─────────────────────────────────────────────────────────────────────────────
SOURCE RULES
─────────────────────────────────────────────────────────────────────────────
  LSEG preferred  : SP500, SP5EFIN, DAX, DXY, EURUSD, XLF
  FRED fallback   : EURUSD → DEXUSEU (from 1999)
                    SP500, SP5EFIN, DAX, XLF have NO free fallback.
                    If their LSEG sheet is missing, the script warns and
                    leaves those columns as NaN.

─────────────────────────────────────────────────────────────────────────────
OUTPUTS
─────────────────────────────────────────────────────────────────────────────
  financial_data_raw.csv           raw merge on original (irregular) date index
  financial_data_master_daily.csv  forced to full daily calendar 1990-2025;
                                   NaN on weekends/holidays — handled in script 02
  data_metadata.csv                coverage stats per variable
─────────────────────────────────────────────────────────────────────────────
NOTE ON SAMPLE
  The master file preserves the full history (1990-2025).
  The analytical sample cut (1997-01-02 → 2024-12-31) is applied in script 02,
  where AAA/BBB/CSPREAD become fully available.  Is NOT truncate here.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import pandas as pd
import numpy as np
from fredapi import Fred
import warnings
warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION
# ============================================================================

START_DATE = "1990-01-02"
END_DATE   = "2025-01-01"

FRED_API_KEY = os.getenv("FRED_API_KEY", "FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

LSEG_FILE = "LSEGdata1.xlsx"

# Map: LSEG sheet name → variable name in final dataset
LSEG_SHEET_MAP = {
    "S&P500 daily": "SP500",
    "S&P FinSect":  "SP5EFIN",
    "DAX":          "DAX",
    "DIX":          "DXY",
    "EUR-USD":      "EURUSD",
    "XLF":          "XLF",
}

print("=" * 80)
print("SCRIPT 01 — DATA DOWNLOAD  (FRED + LSEG EXCEL)")
print("=" * 80)
print(f"Target range: {START_DATE} → {END_DATE}\n")

# ============================================================================
# HELPERS
# ============================================================================

def download_fred(series_id: str, name: str, start: str = START_DATE) -> pd.Series:
    """Download one series from FRED."""
    try:
        print(f"  FRED  {name:<12s} ({series_id}) ... ", end="")
        s = fred.get_series(series_id, observation_start=start, observation_end=END_DATE)
        s = s.dropna().sort_index()
        s.name = name
        print(f"✓  {len(s):,} obs  [{s.index[0].date()} → {s.index[-1].date()}]")
        return s
    except Exception as e:
        print(f"✗  ERROR: {e}")
        return pd.Series(dtype=float, name=name)


def read_lseg_sheet(path: str, sheet: str, name: str) -> pd.Series:
    """
    Read one sheet from the LSEG Excel workbook.

    Expected layout:
      Rows 1-5 : metadata  (Start / End / Frequency / Name / Code)
      After the row where col A == 'Code':
        col A : dates  (dd/mm/yy  or  dd/mm/yyyy)
        col B : values (may use comma as decimal separator)
    """
    df = pd.read_excel(path, sheet_name=sheet, header=None)

    # Locate the 'Code' header row
    col0 = df.iloc[:, 0].astype(str).str.strip().str.lower()
    code_rows = df.index[col0 == "code"].tolist()
    if not code_rows:
        raise ValueError(f"Sheet '{sheet}': row with 'Code' in column A not found.")
    data_start = code_rows[0] + 1

    dates = pd.to_datetime(df.iloc[data_start:, 0], dayfirst=True, errors="coerce")
    vals  = (
        df.iloc[data_start:, 1]
        .astype(str)
        .str.replace(r"\s", "", regex=True)
        .str.replace(",", ".", regex=False)
    )
    vals = pd.to_numeric(vals, errors="coerce")

    s = pd.Series(vals.values, index=dates, name=name, dtype="float64")
    s = s[~s.index.isna()].dropna().sort_index()
    return s


def load_lseg_workbook(path: str, sheet_map: dict) -> dict:
    """Load all mapped sheets from the LSEG workbook into a dict of Series."""
    out = {}
    if not os.path.exists(path):
        print(f"\n  [!] LSEG workbook not found: '{path}' — all LSEG series will be NaN.\n")
        return out

    print("\nLoading LSEG Excel workbook ...")
    xls       = pd.ExcelFile(path)
    available = set(xls.sheet_names)

    for sheet, name in sheet_map.items():
        if sheet not in available:
            print(f"  ○  Sheet '{sheet}' not found in workbook — {name} skipped.")
            continue
        try:
            s = read_lseg_sheet(path, sheet, name)
            out[name] = s
            print(f"  ✓  {name:<10s} from '{sheet}':  "
                  f"{s.index.min().date()} → {s.index.max().date()}  ({len(s):,} obs)")
        except Exception as e:
            print(f"  ✗  '{sheet}' → {name}:  {e}")
    return out


def pick_series(name: str, lseg_key: str, lseg: dict,
                fallback: pd.Series = None) -> pd.Series:
    """
    Return the LSEG series if available.
    Fall back to a FRED series with a warning if LSEG is missing.
    If neither is available, return an empty Series with a warning.
    """
    if lseg_key in lseg and len(lseg[lseg_key]) > 0:
        s = lseg[lseg_key].rename(name)
        print(f"  ✓  {name:<10s} → LSEG  ({len(s):,} obs)")
        return s
    if fallback is not None and len(fallback) > 0:
        print(f"  [!] {name:<10s} LSEG missing → FRED fallback  ({len(fallback):,} obs)")
        return fallback.rename(name)
    print(f"  [!] {name:<10s} LSEG missing, no fallback → column will be all-NaN.")
    return pd.Series(dtype=float, name=name)


# ============================================================================
# STEP 0 — LOAD LSEG EXCEL
# ============================================================================

lseg = load_lseg_workbook(LSEG_FILE, LSEG_SHEET_MAP)

# ============================================================================
# STEP 1 — FRED DOWNLOADS
# ============================================================================

print("\n" + "=" * 80)
print("FRED DOWNLOADS")
print("=" * 80)

# Volatility
vix   = download_fred("VIXCLS",       "VIX")

# Interest rates
dgs10 = download_fred("DGS10",  "DGS10")
dgs2  = download_fred("DGS2",   "DGS2")
dtb3  = download_fred("DTB3",   "DTB3")

slope = (dgs10 - dgs2).dropna().rename("SLOPE")
print(f"  Computed  SLOPE (10Y−2Y): {len(slope):,} obs")

# Credit spreads (ICE BofA, available from end-1996)
bbb     = download_fred("BAMLC0A4CBBB", "BBB", start="1996-12-31")
aaa     = download_fred("BAMLC0A1CAAA", "AAA", start="1996-12-31")
cspread = (bbb - aaa).dropna().rename("CSPREAD")
print(f"  Computed  CSPREAD (BBB−AAA): {len(cspread):,} obs")

# Federal Funds Effective Rate (Daily DFF)
fedfunds = (
    download_fred("DFF", "FEDFUNDS", start="1990-01-01").sort_index()
)
print(
    f"Loaded FEDFUNDS (DFF daily): {len(fedfunds)} obs "
    f"[{fedfunds.index[0].date()} → {fedfunds.index[-1].date()}]"
)

# TED spread — DISCONTINUED January 2023
# Kept in master for robustness on 1990-2022 subsample only
ted = download_fred("TEDRATE", "TED", start="1986-01-02")

# FRED fallbacks for LSEG series
# EURUSD: starts 1999-01-04
eurusd_fred = download_fred("DEXUSEU", "EURUSD_FRED", start="1999-01-04")
# SP500, SP5EFIN, DAX, XLF, DIX: no reliable free alternative → no fallback

# ============================================================================
# STEP 2 — APPLY SOURCE RULES
# ============================================================================

print("\n" + "=" * 80)
print("SOURCE ASSIGNMENT  (LSEG preferred, FRED fallback where defined)")
print("=" * 80)

SP500   = pick_series("SP500",   "SP500",   lseg, fallback=None)
SP5EFIN = pick_series("SP5EFIN", "SP5EFIN", lseg, fallback=None)
DAX     = pick_series("DAX",     "DAX",     lseg, fallback=None)
DXY     = pick_series("DXY",     "DXY",     lseg, fallback=None)
EURUSD  = pick_series("EURUSD",  "EURUSD",  lseg, fallback=eurusd_fred)
XLF     = pick_series("XLF",     "XLF",     lseg, fallback=None)

# Always FRED
VIX      = vix.rename("VIX")
DGS10    = dgs10.rename("DGS10")
DGS2     = dgs2.rename("DGS2")
DTB3     = dtb3.rename("DTB3")
SLOPE    = slope.rename("SLOPE")
BBB      = bbb.rename("BBB")
AAA      = aaa.rename("AAA")
CSPREAD  = cspread.rename("CSPREAD")
FEDFUNDS = fedfunds.rename("FEDFUNDS")
TED      = ted.rename("TED")

# ============================================================================
# STEP 3 — MERGE INTO MASTER DATASET
# ============================================================================

print("\n" + "=" * 80)
print("MERGING")
print("=" * 80)

# Baseline first (12), robustness after (5)
series_dict = {
    # ── BASELINE (12 vars for VAR) ───────────────────────────────────────────
    "SP500":    SP500,      # Equity — broad market
    "SP5EFIN":  SP5EFIN,    # Equity — financial sector
    "VIX":      VIX,        # Volatility / uncertainty
    "CSPREAD":  CSPREAD,    # Credit risk (BBB−AAA)
    "AAA":      AAA,        # AAA yield (component, also robustness check)
    "BBB":      BBB,        # BBB yield (component, also robustness check)
    "DGS10":    DGS10,      # Long-term interest rate
    "SLOPE":    SLOPE,      # Term spread (10Y−2Y)
    "DXY":      DXY,        # US Dollar Index
    "EURUSD":   EURUSD,     # EUR/USD exchange rate
    "DTB3":     DTB3,       # Short-term rate / money market
    "FEDFUNDS": FEDFUNDS,   # Monetary policy rate
    # ── ROBUSTNESS (5 vars) ──────────────────────────────────────────────────
    "DAX":      DAX,        # Global equity — Europe
    "XLF":      XLF,        # Financial ETF (from 1998-12-22)
    "DGS2":     DGS2,       # 2Y yield (component of SLOPE)
    "TED":      TED,        # Money market stress (discontinued 2023)
}

data_raw = pd.concat(series_dict.values(), axis=1).sort_index()
print(f"✓ Raw merge:    {data_raw.shape[0]:,} rows × {data_raw.shape[1]} variables")

# Force onto full daily calendar
# Every calendar day gets a row; missing days (weekends, holidays) = NaN
# These NaNs are resolved by forward-fill in script 02
master_index = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
data_master  = data_raw.reindex(master_index)
print(f"✓ Master daily: {data_master.shape[0]:,} days × {data_master.shape[1]} variables")
print( "  (NaN on weekends / holidays is expected — resolved in script 02)")

# ============================================================================
# STEP 4 — SAVE OUTPUTS
# ============================================================================

print("\n" + "=" * 80)
print("SAVING")
print("=" * 80)

data_raw.to_csv("financial_data_raw.csv")
print("✓ financial_data_raw.csv")

data_master.to_csv("financial_data_master_daily.csv")
print("✓ financial_data_master_daily.csv")

_roles = ["BASELINE"] * 12 + ["ROBUSTNESS"] * 4
_sources = [
    "LSEG", "LSEG", "FRED", "FRED", "FRED", "FRED",
    "FRED", "FRED", "LSEG", "LSEG", "FRED", "FRED",
    "LSEG", "LSEG", "FRED", "FRED"
]
metadata = pd.DataFrame({
    "Variable":    list(series_dict.keys()),
    "Role":        _roles,
    "Source":      _sources,
    "First_Date":  [
        data_master[c].dropna().index.min().date()
        if data_master[c].notna().any() else None
        for c in series_dict
    ],
    "Last_Date":   [
        data_master[c].dropna().index.max().date()
        if data_master[c].notna().any() else None
        for c in series_dict
    ],
    "N_Obs":       [int(data_master[c].notna().sum()) for c in series_dict],
    "Missing_Pct": [round(data_master[c].isna().mean() * 100, 2) for c in series_dict],
})
metadata.to_csv("data_metadata.csv", index=False)
print("✓ data_metadata.csv")

# ============================================================================
# STEP 5 — QUALITY REPORT
# ============================================================================

print("\n" + "=" * 80)
print("DATA QUALITY REPORT — MASTER DAILY")
print("=" * 80)
print(f"\n  Full master:        {data_master.index.min().date()} → "
      f"{data_master.index.max().date()}  "
      f"({data_master.shape[0]:,} calendar days × {data_master.shape[1]} vars)")
print(f"  Analytical sample:  1997-01-02 → 2024-12-31  (applied in script 02)\n")

hdr = f"  {'Var':<10} {'Role':<12} {'Src':<5}  {'N_obs':>7}  {'Miss%':>6}  {'Start':<12} {'End':<12}"
print(hdr)
print("  " + "─" * (len(hdr) - 2))
for _, row in metadata.iterrows():
    flag = "✓" if row["Missing_Pct"] < 35 else ("○" if row["Missing_Pct"] < 55 else "⚠")
    print(f"  {row['Variable']:<10} {row['Role']:<12} {row['Source']:<5}  "
          f"{row['N_Obs']:>7,}  {row['Missing_Pct']:>5.1f}%  "
          f"{str(row['First_Date']):<12} {str(row['Last_Date']):<12}  {flag}")

print("\n" + "=" * 80)
print("SCRIPT 01 COMPLETE  →  next: 02_transform_data.py")
print("=" * 80)
print("""
  Script 02 will:
    1. Load financial_data_master_daily.csv
    2. Restrict to analytical sample: 1997-01-02 → 2024-12-31
    3. Forward-fill on business days (resolve weekend/holiday NaN)
    4. Apply stationarity transformations:
         log-returns : SP500, SP5EFIN, DAX, XLF, DXY, EURUSD
         first diff  : DGS10, DGS2, DTB3, SLOPE, FEDFUNDS, CSPREAD, AAA, BBB, TED
         VIX         : log-levels or first-diff after ADF/KPSS test
    5. ADF / KPSS unit-root tests on all transformed series
    6. Export var_ready_data.csv  (business-day index, stationary, no NaN)
""")
