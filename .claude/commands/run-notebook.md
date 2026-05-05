# Run Notebook

Execute the worldbankproj.ipynb notebook using the correct venv kernel and verify outputs.

## Rules
- ALWAYS use the `PowerShell` tool on this machine. NEVER use the `Bash` tool — it runs in a Unix shell and cannot resolve Windows paths like `.\venv\Scripts\`.
- The registered Jupyter kernel name for this project is `worldbank`. Always pass `--ExecutePreprocessor.kernel_name=worldbank`.
- Timeout should be at least 300 seconds.

## Command
```powershell
cd "C:\Users\oreva\Documents\world bank proj"
.\venv\Scripts\jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.kernel_name=worldbank --ExecutePreprocessor.timeout=300 worldbankproj.ipynb
```

## After running
Verify outputs were written by checking the file size increased and key cells have outputs:
```powershell
(Get-Item worldbankproj.ipynb).Length
```

## If kernel is missing
Re-register it:
```powershell
.\venv\Scripts\pip install ipykernel
.\venv\Scripts\python -m ipykernel install --user --name worldbank --display-name "World Bank (venv)"
```
