# 📁 Experiment Organization (실험 파일 관리)

## 🎯 Purpose
**실험마다 독립된 폴더 + 표준화된 구조 = 재현성 + 추적성**

---

## 📂 Minimal Directory Structure

### 실험 루트 디렉토리
```
~/experiments/
├── 2025-12-18_15-30_experiment_name/
├── 2025-12-18_16-45_another_experiment/
└── REGISTRY.md                        # 실험 추적
```

### 개별 실험 폴더 (최소 구조)
```
experiments/YYYY-MM-DD_HH-MM_experiment_name/
├── README.md                          # 실험 카드 (가설, 결론, 메타데이터)
├── config.yaml                        # 설정 (고정값 기록)
├── code/                              # 실험 코드
├── results/                           # 결과물
│   ├── metrics.json                   # 핵심 지표
│   ├── trades.csv                     # 거래 내역 (trade-by-trade)
│   └── reconciliation.csv             # 포지션/PnL 정합성 체크
└── logs/                              # 실행 로그
```

**Note**: 전략 타입(옵션/MM/롱숏/arbitrage)에 따라 추가 구조는 자유롭게 추가

---

## 📝 README.md Required Sections

Every experiment MUST have a README with:

1. **Hypothesis** (What/Why/Change)
2. **Configuration** (Period/Universe/Costs/Parameters)
3. **Results Summary** (Table with key metrics)
4. **Validation Results** (Checkboxes)
5. **Key Findings**
6. **Risks & Limitations**
7. **Next Steps**
8. **Reconciliation Status** (✅/❌ - see Backtesting Integrity section)

---

## 🤖 Agent Rules for File Organization

### MANDATORY behaviors:

1. **Create experiment folder BEFORE running**
   ```python
   from datetime import datetime
   exp_name = datetime.now().strftime("%Y-%m-%d_%H-%M") + "_fair_iv_ridge"
   exp_dir = Path(f"~/experiments/{exp_name}").expanduser()
   exp_dir.mkdir(parents=True, exist_ok=True)
   (exp_dir / "code").mkdir(exist_ok=True)
   (exp_dir / "results").mkdir(exist_ok=True)
   (exp_dir / "logs").mkdir(exist_ok=True)
   (exp_dir / "validation").mkdir(exist_ok=True)
   ```

2. **Save ALL outputs to experiment folder**
   - Metrics: `results/metrics.json`
   - Logs: `logs/experiment.log`
   - Plots: `results/figures/*.png`
   - Code: `code/*.py` (copy or save)

3. **Generate README.md at the END**
   - After all experiments complete
   - Include actual results (not placeholders)
   - Mark validation checkboxes based on actual tests

4. **Save config.yaml at the START**
   ```yaml
   experiment:
     name: fair_iv_ridge
     date: 2025-12-18 15:30
     hypothesis: "Ridge regression can predict fair IV better than naive model"
   
   data:
     period_start: 2024-10-01
     period_end: 2024-10-07
     symbols: ["BTC-PUT"]
     source: "postgresql://sqr:sqr@localhost/data_integration"
   
   parameters:
     model: Ridge
     alpha: 1.0
     degree: 2
     cv_folds: 5
   
   costs:
     exchange: OKX DMM VIP9
     maker_fee: -0.02%
     taker_fee: 0.03%
   ```

5. **Never scatter files in random locations**
   - ❌ `test.py`, `test2.py`, `final.py`, `final_final.py` in root
   - ✅ All in `experiments/YYYY-MM-DD_HH-MM_name/code/`

---

## 🔍 Searchability & Traceability

### Git Integration
```bash
cd ~/experiments
git init  # if not already
git add YYYY-MM-DD_HH-MM_name/
git commit -m "Experiment: Fair IV Ridge - Sharpe 2.4, Deploy"
git tag exp-fair-iv-ridge-v1
```

### Quick Search
```bash
# Find experiments by metric
grep -r "Sharpe.*2\.[4-9]" ~/experiments/*/README.md

# Find experiments by date range
ls ~/experiments/ | grep "2025-12"

# Find failed experiments
grep -l "Status.*Failed" ~/experiments/*/README.md
```

---

## 📊 Experiment Registry (Optional)

Maintain `~/experiments/REGISTRY.md`:

```markdown
# Experiment Registry

| Date | Name | Status | Sharpe | Decision | Notes |
|------|------|--------|--------|----------|-------|
| 2025-12-18 | fair_iv_ridge | ✅ Success | 2.4 | Deploy | Q4 only, needs validation |
| 2025-12-18 | mispricing_filter | 🟡 Partial | 1.8 | Shelve | Low sample size |
| 2025-12-19 | regime_backtest | 🔴 Failed | 0.3 | Discard | No edge detected |
```

Update automatically or manually after each experiment.

---

**Last Updated**: 2025-12-18  
**Version**: 1.0

