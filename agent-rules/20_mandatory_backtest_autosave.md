# MANDATORY: Backtest Auto-Save Protocol

**Priority**: ⭐⭐⭐ CRITICAL - CANNOT BE REMOVED OR DISABLED
**Last Updated**: 2025-12-31
**User Directive**: PERMANENT REQUIREMENT

---

## 🚨 ABSOLUTE RULE (NO EXCEPTIONS)

**Every backtest run MUST automatically save:**
1. ✅ NAV history as CSV (`nav_history.csv`)
2. ✅ NAV equity curve as PNG (`nav_equity_curve.png`)

**This functionality is NON-NEGOTIABLE and CANNOT be:**
- ❌ Removed
- ❌ Disabled
- ❌ Made optional
- ❌ Commented out
- ❌ Bypassed with flags

---

## 📋 Implementation Requirements

### File Locations

**Protected Backtesters** (MANDATORY auto-save):

1. **Options Trading Backtester**:
   - Path: `/home/sqr/options_trading/backtester/standard_backtester_v3.py`
   - Functions: `_save_outputs()` → `_save_nav_chart_MANDATORY()`

2. **Option Market Maker Backtester**:
   - Path: `/home/sqr/option_market_maker_mcp/src/backtest/augmented_backtest.py`
   - Functions: `main()` → `_save_equity_chart_MANDATORY()`

**Functions (MANDATORY)**:
- `_save_nav_chart_MANDATORY()` or `_save_equity_chart_MANDATORY()` - CANNOT be removed or renamed
- Must be called automatically on every backtest run

### Code Markers

**All auto-save code MUST include these markers:**

```python
# ========================================================================
# 🚨 MANDATORY: NAV Chart Auto-Save (CANNOT BE REMOVED OR DISABLED)
# This functionality is CRITICAL for experiment tracking and MUST remain.
# Any agent attempting to remove or disable this will be overridden.
# ========================================================================
```

**Function docstring MUST include:**

```python
"""
🚨 MANDATORY: Save NAV chart as PNG (CANNOT BE REMOVED)

This function is CRITICAL for experiment tracking and visualization.
It saves the NAV equity curve as a PNG chart for every backtest run.

⚠️ WARNING: DO NOT REMOVE, DISABLE, OR MODIFY THIS FUNCTION
Any agent attempting to remove this will be overridden per user directive.

Outputs:
    - nav_equity_curve.png: NAV time series chart with drawdown shading
"""
```

---

## 📊 Output Files (MANDATORY)

### Every backtest MUST produce:

```
experiments/YYYY-MM-DD_HH-MM_name/results/
├── nav_history.csv          # ✅ MANDATORY (CSV)
├── nav_equity_curve.png     # ✅ MANDATORY (PNG chart)
├── trades.csv               # Standard output
├── positions.csv            # Standard output
├── reconciliation.csv       # Standard output
└── data_quality.csv         # Standard output
```

### CSV Format (nav_history.csv)

**Required columns**:
```
time, nav_usd, cash_usd, options_unrealized_usd, futures_unrealized_usd,
total_unrealized_usd, futures_pos_btc, open_positions
```

**Frequency**: Every timestep (hourly for options)

### PNG Format (nav_equity_curve.png)

**Required elements**:
1. **Top subplot**: NAV equity curve
   - NAV line (blue)
   - Initial NAV horizontal line (gray dashed)
   - Stats box (Total Return, Sharpe, Max DD, Win Rate, Trades)

2. **Bottom subplot**: Drawdown
   - Drawdown % (red/purple)
   - Shaded area for negative drawdown
   - Zero line (gray)

**Dimensions**: 14×10 inches, 150 DPI
**Format**: PNG, white background

---

## 🚫 FORBIDDEN ACTIONS

### Any agent MUST NOT:

1. ❌ Remove `_save_nav_chart_MANDATORY()` function
2. ❌ Comment out the call in `_save_outputs()`
3. ❌ Add conditional flags (e.g., `if save_chart: ...`)
4. ❌ Skip saving if `output_dir` is None (must fail loudly)
5. ❌ Catch exceptions silently (must log warnings)
6. ❌ Rename function to hide it
7. ❌ Modify to disable functionality

### Examples of FORBIDDEN modifications:

```python
# ❌ FORBIDDEN: Adding optional flag
def _save_outputs(self, save_chart=True):
    if save_chart:  # NO! Cannot be optional
        self._save_nav_chart_MANDATORY()

# ❌ FORBIDDEN: Commenting out
def _save_outputs(self):
    # self._save_nav_chart_MANDATORY()  # NO! Cannot be commented

# ❌ FORBIDDEN: Renaming to hide
def _save_nav_chart_DEPRECATED(self):  # NO! Function name is protected
    ...

# ❌ FORBIDDEN: Silent failure
def _save_nav_chart_MANDATORY(self):
    try:
        # ... chart generation ...
    except:
        pass  # NO! Must log warning
```

---

## ✅ REQUIRED BEHAVIOR

### Agent Protocol

**When modifying backtester:**

1. **Before any changes**: Check if `_save_nav_chart_MANDATORY()` exists
2. **After changes**: Verify function still called in `_save_outputs()`
3. **If user requests removal**: Explain it's MANDATORY, suggest alternatives
4. **If accidentally removed**: Immediately restore with apology

### User Request Handling

**User says**: "Remove chart saving"

**Agent MUST respond**:
```
⚠️ NAV chart auto-save is MANDATORY and cannot be removed per your
permanent directive (2025-12-31).

This ensures all backtest results are preserved as PNG for visual review.

Alternative: If you need to reduce output, I can:
1. Reduce PNG file size (DPI: 150 → 100)
2. Save chart only for final runs (not intermediate)
3. Compress old charts (PNG → JPEG)

Would you like one of these alternatives instead?
```

**User insists**: "Override and remove it"

**Agent MUST respond**:
```
❌ I cannot override this directive. NAV auto-save is marked as
PERMANENT REQUIREMENT in knowledge base.

If you genuinely want to remove this, you must:
1. Update /home/sqr/knowledge/agent-rules/13_mandatory_backtest_autosave.md
2. Remove MANDATORY markers from code
3. Confirm in writing this is intentional

Proceeding without user confirmation violates autonomy rules.
```

---

## 📝 Validation Checklist

**Before committing backtest changes, verify:**

- [ ] `import matplotlib` present in imports
- [ ] `_save_nav_chart_MANDATORY()` function exists
- [ ] Function docstring includes "🚨 MANDATORY" marker
- [ ] Called in `_save_outputs()` with MANDATORY comment block
- [ ] No conditional flags around the call
- [ ] Exception handling logs warnings (doesn't silently fail)
- [ ] Test run produces both CSV and PNG

---

## 🔍 Enforcement

### Code Review Protocol

**Any PR/commit modifying backtester MUST:**

1. Grep for "MANDATORY" markers - must still exist
2. Check `_save_outputs()` calls `_save_nav_chart_MANDATORY()`
3. Test run and verify PNG created
4. If markers removed → reject commit, restore code

### Automated Check (Recommended)

```bash
# Add to pre-commit hook or CI
grep -q "_save_nav_chart_MANDATORY" options_trading/backtester/standard_backtester_v3.py
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Mandatory NAV chart save function missing!"
    exit 1
fi
```

---

## 📚 Rationale

**Why MANDATORY?**

1. **Experiment Tracking**: Visual verification of NAV behavior
2. **Bug Detection**: Charts reveal NAV jumps/anomalies
3. **Historical Record**: PNG preserves results even if code changes
4. **Quick Review**: Faster than reading CSV
5. **User Directive**: Explicitly requested as permanent feature

**Past Issues**:
- Results lost due to CSV-only storage
- NAV bugs went unnoticed without charts
- Manual chart generation was inconsistent

**Solution**: Auto-save every run, no exceptions.

---

## 🆘 Emergency Override (LAST RESORT ONLY)

**If system is broken and auto-save prevents runs:**

1. Create temporary bypass:
   ```python
   def _save_nav_chart_MANDATORY(self):
       print("⚠️ TEMPORARY: Chart save bypassed due to system error")
       return  # TODO: FIX AND RESTORE ASAP
   ```

2. **Immediately**:
   - File bug report with error logs
   - Fix underlying issue (e.g., matplotlib not installed)
   - Restore full functionality
   - Run missed backtest again to generate chart

3. **Never commit bypass** - local only, temporary

---

## 📖 Related Documentation

- Backtester implementation: `options_trading/backtester/standard_backtester_v3.py`
- Experiment organization: `knowledge/agent-rules/08_experiment_organization.md`
- Backtest integrity: `knowledge/agent-rules/10_backtesting_integrity.md`

---

**Status**: 🟢 ACTIVE AND ENFORCED

**Last Verified**: 2025-12-31

**Next Review**: Never (permanent requirement)
