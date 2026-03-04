"""
SCRIPT 02: DATA TRANSFORMATION  →  VAR-READY DATASET
=====================================================
Loads financial_data_master_daily.csv (output of script 01) and produces
a clean, stationary, NYSE-trading-day dataset ready for MATLAB VAR estimation.

─────────────────────────────────────────────────────────────────────────────
OPERATIONS (in order)
─────────────────────────────────────────────────────────────────────────────
  1. Load master daily CSV
  2. Restrict to analytical sample: 1997-01-02 → 2024-12-31
  3. Forward-fill on full calendar, then keep NYSE trading days only
     (eliminates weekends AND market holidays: Christmas, Thanksgiving, etc.)
  4. Stationarity transformations (log-returns or first differences)
  5. ADF + KPSS unit-root tests on raw AND transformed series
  6. Export baseline (12 vars) and full (16 vars) datasets
  7. Save outputs

─────────────────────────────────────────────────────────────────────────────
TRANSFORMATION RULES
─────────────────────────────────────────────────────────────────────────────
  Log-returns  [× 100, in pct]  :  SP500, SP5EFIN, DAX, XLF, DXY, EURUSD
  First diff                    :  DGS10, SLOPE, DTB3, FEDFUNDS,
                                   CSPREAD, AAA, BBB, TED, DGS2
  VIX                           :  log-level tested first; if non-stationary
                                   → log first-difference

─────────────────────────────────────────────────────────────────────────────
OUTPUTS
─────────────────────────────────────────────────────────────────────────────
  var_ready_baseline.csv    12 baseline vars, stationary, NYSE trading days
                            → import directly into MATLAB for VAR estimation
  var_ready_full.csv        all 16 vars (baseline + robustness), same format
  unit_root_tests.csv       ADF and KPSS results for all series (raw + transf.)
  transformation_log.csv    which transformation was applied to each variable

─────────────────────────────────────────────────────────────────────────────
MATLAB IMPORT
─────────────────────────────────────────────────────────────────────────────
  T     = readtable('var_ready_baseline.csv');
  dates = datetime(T.Date, 'InputFormat', 'yyyy-MM-dd');
  Y     = T{:, 2:end};   % T×12 matrix of stationary series
  vars  = T.Properties.VariableNames(2:end);
─────────────────────────────────────────────────────────────────────────────
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss
import pandas_market_calendars as mcal
import warnings
warnings.filterwarnings("ignore")

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE   = "financial_data_master_daily.csv"
SAMPLE_START = "1997-01-02"
SAMPLE_END   = "2024-12-31"

# Baseline variables (12) — VAR ordering: fastest-adjusting first
# Follows Diebold & Yilmaz (2009): equity → volatility → credit → rates → FX → money
BASELINE_VARS = [
    "SP500",     # Equity — broad market
    "SP5EFIN",   # Equity — financial sector
    "VIX",       # Volatility / uncertainty
    "CSPREAD",   # Credit risk
    "AAA",       # AAA yield
    "BBB",       # BBB yield
    "DGS10",     # Long-term interest rate
    "SLOPE",     # Term spread
    "DXY",       # US Dollar Index
    "EURUSD",    # EUR/USD
    "DTB3",      # Short-term rate
    "FEDFUNDS",  # Policy rate
]

# Robustness variables (5) — in var_ready_full.csv only
ROBUSTNESS_VARS = ["DAX", "XLF", "DGS2", "TED"]

ALL_VARS = BASELINE_VARS + ROBUSTNESS_VARS

# Transformation map
# "logret"   → log(Pt/Pt-1) × 100   percentage log-return
# "diff"     → Xt - Xt-1             first difference
# "loglevel" → log(Xt)               log-level (tested first for VIX)
# "logdiff"  → log(Xt/Xt-1) × 100   log first-difference (VIX override if needed)
TRANSFORM_MAP = {
    "SP500":    "logret",
    "SP5EFIN":  "logret",
    "DAX":      "logret",
    "XLF":      "logret",
    "DXY":      "logret",
    "EURUSD":   "logret",
    "DGS10":    "diff",
    "DGS2":     "diff",
    "SLOPE":    "diff",
    "DTB3":     "diff",
    "FEDFUNDS": "diff",
    "CSPREAD":  "diff",
    "AAA":      "diff",
    "BBB":      "diff",
    "TED":      "diff",
    "VIX":      "loglevel",   # tested; overridden to logdiff if non-stationary
}

ADF_MAXLAGS = 10
KPSS_LAGS   = "auto"
ALPHA       = 0.05

# ============================================================================
# HELPERS
# ============================================================================

def apply_transform(series: pd.Series, method: str) -> pd.Series:
    """Apply stationarity transformation. Clips to 1e-10 before log to avoid -inf."""
    s = series.copy()
    if method in ("logret", "logdiff"):
        s_clipped = s.clip(lower=1e-10)
        if (s <= 0).any():
            print(f"    [!] WARNING: {s.name} has non-positive values — clipped before log")
        return (np.log(s_clipped) - np.log(s_clipped.shift(1))) * 100
    elif method == "diff":
        return s.diff()
    elif method == "loglevel":
        s_clipped = s.clip(lower=1e-10)
        return np.log(s_clipped)
    else:
        raise ValueError(f"Unknown transform: {method}")


def run_adf(series: pd.Series) -> dict:
    """ADF test. H0: unit root. Reject → stationary."""
    s = series.dropna()
    try:
        stat, pval, lags, _, crit, _ = adfuller(s, maxlag=ADF_MAXLAGS, autolag="BIC")
        return {
            "ADF_stat":   round(stat, 4),
            "ADF_pval":   round(pval, 4),
            "ADF_lags":   lags,
            "ADF_crit5":  round(crit["5%"], 4),
            "ADF_reject": pval < ALPHA,
        }
    except Exception:
        return {"ADF_stat": np.nan, "ADF_pval": np.nan, "ADF_lags": np.nan,
                "ADF_crit5": np.nan, "ADF_reject": np.nan}


def run_kpss(series: pd.Series) -> dict:
    """KPSS test. H0: stationary. Reject → non-stationary."""
    s = series.dropna()
    try:
        stat, pval, lags, crit = kpss(s, regression="c", nlags=KPSS_LAGS)
        return {
            "KPSS_stat":   round(stat, 4),
            "KPSS_pval":   round(pval, 4),
            "KPSS_lags":   lags,
            "KPSS_crit5":  round(crit["5%"], 4),
            "KPSS_reject": pval < ALPHA,
        }
    except Exception:
        return {"KPSS_stat": np.nan, "KPSS_pval": np.nan, "KPSS_lags": np.nan,
                "KPSS_crit5": np.nan, "KPSS_reject": np.nan}


def stationarity_verdict(adf: dict, kpss_r: dict) -> str:
    """
    STATIONARY    : ADF rejects unit root  AND  KPSS does NOT reject stationarity
    NON-STATIONARY: ADF does not reject    AND  KPSS rejects stationarity
    AMBIGUOUS     : tests disagree
    """
    adf_ok  = adf.get("ADF_reject", False)
    kpss_ok = not kpss_r.get("KPSS_reject", True)
    if adf_ok and kpss_ok:
        return "STATIONARY"
    elif not adf_ok and not kpss_ok:
        return "NON-STATIONARY"
    else:
        return "AMBIGUOUS"


# ============================================================================
# STEP 1 — LOAD
# ============================================================================

print("=" * 80)
print("SCRIPT 02 — DATA TRANSFORMATION  →  VAR-READY DATASET")
print("=" * 80)
print(f"Input:             {INPUT_FILE}")
print(f"Analytical sample: {SAMPLE_START} → {SAMPLE_END}\n")

print("=" * 80)
print("STEP 1 — LOAD MASTER DAILY")
print("=" * 80)

data = pd.read_csv(INPUT_FILE, index_col=0, parse_dates=True)
print(f"  Loaded: {data.shape[0]:,} rows × {data.shape[1]} variables")
print(f"  Index:  {data.index.min().date()} → {data.index.max().date()}")

available = [v for v in ALL_VARS if v in data.columns]
missing_v = [v for v in ALL_VARS if v not in data.columns]
if missing_v:
    print(f"\n  [!] Variables not found in master (check script 01): {missing_v}")
data = data[available].copy()

# ============================================================================
# STEP 2 — RESTRICT TO ANALYTICAL SAMPLE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 2 — RESTRICT TO ANALYTICAL SAMPLE")
print("=" * 80)

data = data.loc[SAMPLE_START:SAMPLE_END]
print(f"  Sample: {data.index.min().date()} → {data.index.max().date()}")
print(f"  Shape:  {data.shape[0]:,} calendar days × {data.shape[1]} variables")

# ============================================================================
# STEP 3 — FORWARD-FILL → NYSE TRADING DAYS ONLY
# ============================================================================

print("\n" + "=" * 80)
print("STEP 3 — FORWARD-FILL AND RESTRICT TO NYSE TRADING DAYS")
print("=" * 80)

# Build NYSE trading day calendar for the sample period
# This removes weekends AND all NYSE market holidays

nyse = mcal.get_calendar("NYSE")
schedule = nyse.schedule(start_date=SAMPLE_START, end_date=SAMPLE_END)
trading_days = schedule.index.tz_localize(None)

print(f"  NYSE trading days in sample: {len(trading_days):,}")

data.index = pd.to_datetime(data.index).tz_localize(None).normalize()

data_ffill = data.ffill()
data_bday  = data_ffill.loc[data_ffill.index.isin(trading_days)].copy()

print(f"  After ffill + NYSE filter:   {data_bday.shape[0]:,} days × {data_bday.shape[1]} vars")

monfri = data_ffill.loc[data_ffill.index.dayofweek < 5]
extra_removed = len(monfri) - len(data_bday)

print(f"  Removed vs Mon-Fri filter: {extra_removed:,} holiday rows")

# Report remaining NaN (series not yet available at sample start)
nan_report = data_bday.isna().sum()
nan_vars   = nan_report[nan_report > 0]
if len(nan_vars) > 0:
    print("\n  Remaining NaN after ffill:")
    for v, n in nan_vars.items():
        print(f"    {v:<12s}: {n:,} NaN  ({n/len(data_bday)*100:.1f}%)")
else:
    print("  No remaining NaN. ✓")

# ============================================================================
# STEP 4a — UNIT ROOT TESTS ON RAW (LEVEL) SERIES
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4a — UNIT ROOT TESTS ON RAW (LEVEL) SERIES")
print("=" * 80)
print(f"\n  {'Variable':<12} {'ADF stat':>10} {'ADF p':>8} {'KPSS stat':>10} {'KPSS p':>8}  Verdict")
print("  " + "─" * 65)

raw_results = []
for var in available:
    adf = run_adf(data_bday[var])
    kps = run_kpss(data_bday[var])
    vrd = stationarity_verdict(adf, kps)
    flag = "✓" if vrd == "STATIONARY" else ("?" if vrd == "AMBIGUOUS" else "✗")
    print(f"  {var:<12} {adf['ADF_stat']:>10.4f} {adf['ADF_pval']:>8.4f} "
          f"{kps['KPSS_stat']:>10.4f} {kps['KPSS_pval']:>8.4f}  {flag} {vrd}")
    raw_results.append({"Variable": var, "Stage": "RAW", "Transform": "level",
                        "Verdict": vrd, **adf, **kps})

# ============================================================================
# STEP 4b — APPLY TRANSFORMATIONS
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4b — APPLY STATIONARITY TRANSFORMATIONS")
print("=" * 80)

data_transf = pd.DataFrame(index=data_bday.index)
transf_log  = []

desc_map = {
    "logret":   "log-return × 100  (pct)",
    "diff":     "first difference",
    "logdiff":  "log first-difference × 100",
    "loglevel": "log-level (tested for stationarity)",
}

for var in available:
    method = TRANSFORM_MAP.get(var, "diff")
    s_tr   = apply_transform(data_bday[var], method)
    data_transf[var] = s_tr
    print(f"  {var:<12s} → {desc_map.get(method, method)}")
    transf_log.append({"Variable": var, "Transformation": method,
                        "Description": desc_map.get(method, method)})

# Drop first row (NaN from differencing/returns)
data_transf = data_transf.iloc[1:].copy()

# ============================================================================
# STEP 4c — UNIT ROOT TESTS ON TRANSFORMED SERIES + VIX OVERRIDE
# ============================================================================

print("\n" + "=" * 80)
print("STEP 4c — UNIT ROOT TESTS ON TRANSFORMED SERIES")
print("=" * 80)
print(f"\n  {'Variable':<12} {'Transform':<12} {'ADF stat':>10} {'ADF p':>8} "
      f"{'KPSS stat':>10} {'KPSS p':>8}  Verdict")
print("  " + "─" * 78)

transf_results = []

for var in available:
    method = TRANSFORM_MAP.get(var, "diff")
    adf    = run_adf(data_transf[var])
    kps    = run_kpss(data_transf[var])
    vrd    = stationarity_verdict(adf, kps)

    # VIX override: if log-level is non-stationary → switch to log first-difference
    if var == "VIX" and vrd != "STATIONARY":
        print(f"  {var:<12} loglevel     → NOT stationary, switching to logdiff ...")
        new_s = apply_transform(data_bday[var], "logdiff").iloc[1:]
        data_transf[var]   = new_s
        TRANSFORM_MAP[var] = "logdiff"
        method = "logdiff"
        adf    = run_adf(data_transf[var])
        kps    = run_kpss(data_transf[var])
        vrd    = stationarity_verdict(adf, kps)
        for entry in transf_log:
            if entry["Variable"] == var:
                entry["Transformation"] = "logdiff"
                entry["Description"]    = "log first-difference × 100 (overridden after ADF)"

    flag = "✓" if vrd == "STATIONARY" else ("?" if vrd == "AMBIGUOUS" else "✗")
    print(f"  {var:<12} {method:<12} {adf['ADF_stat']:>10.4f} {adf['ADF_pval']:>8.4f} "
          f"{kps['KPSS_stat']:>10.4f} {kps['KPSS_pval']:>8.4f}  {flag} {vrd}")
    transf_results.append({"Variable": var, "Stage": "TRANSFORMED",
                            "Transform": method, "Verdict": vrd, **adf, **kps})

non_stat = [r["Variable"] for r in transf_results if r["Verdict"] == "NON-STATIONARY"]
if non_stat:
    print(f"\n  [!] Still non-stationary after transformation: {non_stat}")
    print(f"      Consider second differences or further inspection.")
else:
    print(f"\n  All transformed series are stationary (or ambiguous). ✓")

# ============================================================================
# STEP 5 — FINAL EXPORT
# ============================================================================

print("\n" + "=" * 80)
print("STEP 5 — FINAL EXPORT")
print("=" * 80)

data_transf = data_transf.dropna(how="all")
data_transf.index.name = "Date"

# Baseline (12 vars) — drop rows with any NaN in baseline columns
baseline_cols = [v for v in BASELINE_VARS if v in data_transf.columns]
data_baseline = data_transf[baseline_cols].dropna()
data_baseline.to_csv("var_ready_baseline.csv")
print(f"✓ var_ready_baseline.csv  →  {data_baseline.shape[0]:,} obs × {data_baseline.shape[1]} vars")
print(f"  Sample: {data_baseline.index.min().date()} → {data_baseline.index.max().date()}")

# Full (all 16 vars) — drop only if any baseline column is NaN
all_cols  = [v for v in ALL_VARS if v in data_transf.columns]
data_full = data_transf[all_cols].dropna(subset=baseline_cols)
data_full.to_csv("var_ready_full.csv")
print(f"✓ var_ready_full.csv      →  {data_full.shape[0]:,} obs × {data_full.shape[1]} vars")

# Unit root test table
ur_df = pd.DataFrame(raw_results + transf_results)
ur_df.to_csv("unit_root_tests.csv", index=False)
print(f"✓ unit_root_tests.csv     →  {len(ur_df)} rows (raw + transformed tests)")

# Transformation log
tl_df = pd.DataFrame(transf_log)
tl_df.to_csv("transformation_log.csv", index=False)
print(f"✓ transformation_log.csv  →  {len(tl_df)} variables documented")

# ============================================================================
# STEP 6 — SUMMARY REPORT
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
  Analytical sample : {data_baseline.index.min().date()} → {data_baseline.index.max().date()}
  NYSE trading days : {data_baseline.shape[0]:,}
  Baseline vars     : {data_baseline.shape[1]}
  Full vars         : {data_full.shape[1]}

  Transformations applied (baseline):""")
for entry in transf_log:
    if entry["Variable"] in BASELINE_VARS:
        print(f"    {entry['Variable']:<12s}  {entry['Description']}")

print(f"""
  Files ready for MATLAB:
    → var_ready_baseline.csv   (baseline VAR)
    → var_ready_full.csv       (robustness checks)

  MATLAB import:
    T     = readtable('var_ready_baseline.csv');
    dates = datetime(T.Date, 'InputFormat', 'yyyy-MM-dd');
    Y     = T{{:, 2:end}};        % {data_baseline.shape[0]} × {data_baseline.shape[1]} matrix
    vars  = T.Properties.VariableNames(2:end);
""")
print("=" * 80)
print("SCRIPT 02 COMPLETE  →  next: MATLAB  03_estimate_var.m")
print("=" * 80)
