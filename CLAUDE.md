# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project goal

**Infrastructure Credit Risk Model** — a probability-of-default model for infrastructure projects (toll roads, bridges, power plants) using the World Bank PPI database. The model predicts project distress using logistic regression and/or survival analysis, mirroring what risk analysts do at project finance desks. Final deliverable includes a Streamlit dashboard.

Stack: Python, pandas, scikit-learn, Streamlit.

## Environment

- Python 3.14 via a local `venv` — activate with `venv\Scripts\Activate.ps1` (PowerShell) before running anything
- Data lives in `data\CustomQuery.xlsx` (6,636 rows × 45 columns, World Bank PPI database export)

## Windows rules — read before running any tool

**Always use the `PowerShell` tool. Never use the `Bash` tool.** Bash runs in a Unix shell and cannot resolve `.\venv\Scripts\` or any Windows paths.

| Operation | Correct command |
|---|---|
| pip | `.\venv\Scripts\pip <args>` |
| python | `.\venv\Scripts\python <script>.py` |
| jupyter | `.\venv\Scripts\jupyter <args>` |
| streamlit | `.\venv\Scripts\streamlit run app.py` |

**Python scripts, not one-liners.** PowerShell mangles f-strings and quotes in inline `-c` calls. Always `Write` a `.py` file first, then run it. Every script that prints must include:
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')  # Windows cp1252 can't print Unicode
```

**Jupyter kernel.** The notebook's kernel metadata references a stale Conda environment. Always override it:
```powershell
.\venv\Scripts\jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=worldbank --ExecutePreprocessor.timeout=300 worldbankproj.ipynb
```
To re-register the kernel if missing: `.\venv\Scripts\python -m ipykernel install --user --name worldbank`

**GitHub CLI is not installed.** Do not use `gh` commands. Use `git` directly. To install: `winget install GitHub.cli`

## Commands

Run the Streamlit dashboard:
```powershell
.\venv\Scripts\streamlit run app.py
```

Install dependencies:
```powershell
.\venv\Scripts\pip install pandas numpy openpyxl jupyter scikit-learn matplotlib seaborn streamlit lifelines imbalanced-learn ipykernel
```

`lifelines` is the survival analysis library. `imbalanced-learn` provides SMOTE/class-weight tools needed for the severe class imbalance.

## Modeling approach

**Target variable:** `distressed` — binary flag where 1 = `Project status` ∈ {Cancelled, Distressed}, 0 = all others.

**Class imbalance:** 129 distressed vs. 6,507 healthy (~1.9% positive rate). Use `class_weight='balanced'` in sklearn or SMOTE. Evaluate with AUC-ROC and precision-recall, not accuracy.

**Two modeling paths:**
1. **Logistic regression** — probability of distress at financial close; interpretable coefficients map directly to credit risk factors (leverage, sector, region)
2. **Survival analysis** (Cox proportional hazards via `lifelines`) — models *time to distress*, treating active projects as right-censored; `ContractPeriod` and `InvestmentYear` serve as the time axis

## Data and feature engineering

The raw 45-column dataset covers project geography, contract structure, financing, and sponsor details. Engineered features in the notebook:

| Feature | Description |
|---|---|
| `distressed` | Binary target: `Project status` ∈ {Cancelled, Distressed} |
| `has_direct_support` | Govt direct support present (not "Not Available/Applicable") |
| `has_indirect_support` | Govt indirect support present |
| `is_subsaharan` | Region contains "Sub-Saharan" |
| `is_brownfield_div` | `Type of PPI` ∈ {Brownfield, Divestiture} |
| `is_high_risk_sector` | `Primary sector` ∈ {ICT, Transport} |

Numeric columns cast with `pd.to_numeric(..., errors='coerce')`: `TotalInvestment`, `PhysicalAssets`, `Total Equity`, `TotalDebtFunding`, `ContractPeriod`, `PercentPrivate`.

## Key data quirks

- `MultiLateralSupport` / `BiLateralSupport` are free-text strings like `"IFC (Loan / $10 Million / 2004)"`, not booleans — extract binary presence flags before modeling
- `DebtEquityGrantRatio` is a string like `"80:20"` — split on `:` and convert to a numeric leverage ratio
- Sponsor country strings use `\n\n` as a multi-value separator
- `TotalDebtFunding` is only ~35% complete — imputation strategy significantly affects leverage-based features
- `Financial closure year` and `InvestmentYear` are separate fields that are often identical; use `Financial closure year` as the primary time reference
