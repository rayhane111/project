import subprocess

# Start Data Visualization Service
subprocess.Popen(["uvicorn", "data-visualisation.app:app", "--host", "0.0.0.0", "--port", "8001"])

# Start Document Translation Service
subprocess.Popen(["uvicorn", "document-translation.app:app", "--host", "0.0.0.0", "--port", "8002"])
