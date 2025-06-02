import streamlit as st
import os
import yaml
import pandas as pd

# Path to MLflow experiment runs
eid = '946821819132995098'
mlruns_dir = os.path.join('mlruns', eid)

# Helper to read a file if it exists
def read_file(path):
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except Exception:
        return None

# Helper to read YAML
def read_yaml(path):
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

# Gather all runs
def get_runs():
    runs = []
    for run_id in os.listdir(mlruns_dir):
        run_path = os.path.join(mlruns_dir, run_id)
        meta = read_yaml(os.path.join(run_path, 'meta.yaml'))
        if not meta:
            continue
        params_dir = os.path.join(run_path, 'params')
        metrics_dir = os.path.join(run_path, 'metrics')
        patient_id = read_file(os.path.join(params_dir, 'patient_id'))
        alert_level = read_file(os.path.join(params_dir, 'alert_level'))
        risk_score = read_file(os.path.join(metrics_dir, 'risk_score'))
        # Parse risk_score (take last value if multiple)
        if risk_score:
            risk_score = risk_score.strip().split()[-2] if len(risk_score.strip().split()) >= 2 else risk_score.strip()
        runs.append({
            'run_id': run_id,
            'run_name': meta.get('run_name'),
            'user_id': meta.get('user_id'),
            'start_time': meta.get('start_time'),
            'end_time': meta.get('end_time'),
            'status': meta.get('status'),
            'patient_id': patient_id,
            'alert_level': alert_level,
            'risk_score': risk_score
        })
    return runs

st.title('MLflow Model Runs Monitor')
runs = get_runs()
if not runs:
    st.warning('No runs found.')
else:
    df = pd.DataFrame(runs)
    st.dataframe(df)
    st.caption('Showing all MLflow runs for the health_monitoring experiment.')
