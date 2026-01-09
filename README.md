# LSF Automation
Small automation script to log into the LSF portal, fetch the "Notenspiegel" table and summarize grades/points.

## Features
- Logs into LSF using Selenium
- Navigates to the Notenspiegel page and extracts table rows
- Calculates average grade and total points
- Outputs on the console the course name, grade and points received
- Writes runtime logs to `logs/`

## How to use

1. Clone the repository:

```bash
git clone https://github.com./tiagomorato/lsf-automation.git
cd lsf-automation
```

2. Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install project dependencies declared in `pyproject.toml`.

If you use `pip` (will build and install the project and its dependencies):

```bash
pip install .
```

4. Create a `.env` file in the project root and add your credentials:

```
LOGIN=your_username
PASSWORD=your_password
```

5. Run the automation script:

```bash
python lsf_automation.py
```

## Logs
Logs are written into the directory specified by `LOG_DIR` (default: `logs`). Log filename includes a timestamp.