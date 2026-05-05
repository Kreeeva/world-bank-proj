# Windows Dev Rules

Critical rules for this project to avoid the errors that have occurred in past sessions.

## Tool selection
- ALWAYS use `PowerShell` tool. NEVER use `Bash` — it is a Unix shell and cannot see `.\venv\Scripts\` or Windows paths.
- There is no exception to this rule on this machine.

## Running Python scripts
- Never run Python logic as an inline PowerShell one-liner. PowerShell mangles f-strings and quotes.
- Always write a `.py` file first with the `Write` tool, then execute it:
  ```powershell
  .\venv\Scripts\python script.py
  ```
- Always add this at the top of any Python script that prints to the console:
  ```python
  import sys
  sys.stdout.reconfigure(encoding='utf-8')
  ```
  Windows defaults to cp1252 which cannot print Unicode characters and will throw `UnicodeEncodeError`.

## Venv executables
All executables live at `.\venv\Scripts\`. Use the full relative path every time:
| Tool | Command |
|---|---|
| pip | `.\venv\Scripts\pip` |
| python | `.\venv\Scripts\python` |
| jupyter | `.\venv\Scripts\jupyter` |
| streamlit | `.\venv\Scripts\streamlit` |

## Jupyter kernel
The kernel registered for this project is named `worldbank`.
Always pass `--ExecutePreprocessor.kernel_name=worldbank` to nbconvert.
Never rely on the kernel name stored in the notebook metadata — it may reference a stale Conda environment.

## File-before-run rule
Always use the `Write` tool to create a script file BEFORE calling PowerShell to run it. Never reference a file that has not been written yet in the current session.

## GitHub / git
- `gh` CLI is NOT installed. Do not attempt `gh` commands.
- Use `git` directly for all version control operations.
- To install gh in future: `winget install GitHub.cli`
