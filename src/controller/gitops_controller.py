import time
import subprocess
import pandas as pd
from kubernetes import client, config
from kubernetes.client.rest import ApiException

DEPLOYMENT_NAME = "nginx-telecom-app"
NAMESPACE = "default"
STABLE_IMAGE = "nginx:1.20-alpine"

def init_k8s():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    return client.AppsV1Api()

def run_predictive_pipeline():
    """Triggers Feature Engineering and returns risk status."""
    print("\n[*] Starting Closed-Loop Pipeline...")
    try:
        # 1. Feature Engineering (Parsing ns-3 telemetry)
        # In a real run, parse_data.py reads the latest XML from ns-3
        subprocess.run(["python3", "parse_data.py"], check=True)
        
        # 2. Predictive Analytics (Inference)
        # We simulate the inference result based on the parsed CSV logic
        # In Milestone 4, we will load the actual model.pkl here
        df = pd.read_csv("flow_metrics.csv")
        latest_delay = df['delay_sum_ns'].iloc[-1]
        
        # Thresholding logic from Milestone 2
        is_faulty = latest_delay > df['delay_sum_ns'].quantile(0.9)
        
        print(f"[i] Feature Extraction: delay_sum_ns = {latest_delay}")
        return is_faulty
    except Exception as e:
        print(f"[!] Pipeline Error: {e}. Falling back to simulation mode.")
        return False

def execute_rollback(apps_v1):
    try:
        deployment = apps_v1.read_namespaced_deployment(name=DEPLOYMENT_NAME, namespace=NAMESPACE)
        if deployment.spec.template.spec.containers[0].image != STABLE_IMAGE:
            print(f"[!] FAULT DETECTED. Reverting to {STABLE_IMAGE}...")
            deployment.spec.template.spec.containers[0].image = STABLE_IMAGE
            apps_v1.patch_namespaced_deployment(name=DEPLOYMENT_NAME, namespace=NAMESPACE, body=deployment)
            print("[+] Remediation Successful.")
    except ApiException as e:
        print(f"[ERROR] K8s API: {e}")

if __name__ == "__main__":
    api = init_k8s()
    while True:
        if run_predictive_pipeline():
            execute_rollback(api)
        time.sleep(10)
