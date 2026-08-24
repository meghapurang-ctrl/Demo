# Agentic Campaign Optimization Engine

A workshop-ready Streamlit application that demonstrates an agent monitoring campaign performance, diagnosing underperformers, generating targeted creative, and reallocating budget.

## Run locally

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

The app reads `synthetic_marketing_campaign_dataset.csv` from the project directory. No API key is required: the creative agent is a deterministic simulation designed for teaching and repeatable demos.

## Structure

- `app.py` - Streamlit pages, layout, charts, and session interaction
- `utils/data.py` - dataset loading, anomaly detection, and budget calculations
- `utils/agent.py` - simulated creative analysis and copy generation
- `requirements.txt` - Python dependencies
