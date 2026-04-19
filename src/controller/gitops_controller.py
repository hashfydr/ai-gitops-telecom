import os
import sys
import time
import base64
import yaml
import joblib
import numpy as np
import pandas as pd  # <-- Added to fix the Sklearn warning
from dotenv import load_dotenv
from github import Github, Auth
from github.GithubException import GithubException

# --- Load Environment Variables ---
env_path = os.path.join(os.getcwd(), '.env')
if not os.path.exists(env_path):
    print(f"[CRITICAL ERROR] No .env file found at: {env_path}")
    sys.exit(1)

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("[CRITICAL ERROR] GITHUB_TOKEN is empty inside .env!")
    sys.exit(1)

# --- Configuration ---
REPO_NAME = "hashfydr/ai-gitops-telecom" # <-- Your repo
FILE_PATH = "k8s/apps/dummy-nginx-deployment.yaml"
CHECK_INTERVAL = 30 # seconds

# --- Load AI Model ---
try:
    model = joblib.load('models/network_model.joblib')
except FileNotFoundError:
    print("[CRITICAL ERROR] models/network_model.joblib not found. Run training script first.")
    sys.exit(1)

# --- Functions ---
def check_network_with_ai(current_latency):
    """Uses the trained ML model to predict network state."""
    # FIX: Send a Pandas DataFrame with the column name 'latency' to suppress the Sklearn warning
    input_data = pd.DataFrame([[current_latency]], columns=['latency'])
    prediction = model.predict(input_data)[0]
    
    if prediction == 1:
        print(f"!!! AI PREDICTION: Network is DEGRADED (Latency: {current_latency}ms) !!!")
        return True
    else:
        print(f"[AI] Network healthy ({current_latency}ms).")
        return False

def remediate_via_gitops():
    """Pushes a commit to GitHub to scale up replicas."""
    print(f"[GitOps] Authenticating to GitHub...")
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

    try:
        repo = g.get_repo(REPO_NAME)
        file_content = repo.get_contents(FILE_PATH)
        yaml_content = base64.b64decode(file_content.content).decode("utf-8")
        
        # FIX: Handle multiple YAML documents separated by "---"
        parsed_yamls = list(yaml.safe_load_all(yaml_content))
        updated_yamls = []
        current_replicas = 0
        new_replicas = 0
        
        for doc in parsed_yamls:
            # Only change replicas if the document is a Deployment
            if doc and doc.get("kind") == "Deployment":
                current_replicas = doc["spec"].get("replicas", 1)
                new_replicas = current_replicas + 1
                doc["spec"]["replicas"] = new_replicas
            updated_yamls.append(doc)
        
        # Dump all documents back into a single string with --- separators
        updated_yaml_str = yaml.dump_all(updated_yamls, default_flow_style=False)
        
        print(f"[GitOps] Pushing scale-up ({current_replicas} -> {new_replicas}) to GitHub...")
        repo.update_file(
            path=file_content.path,
            message=f"Auto-Remediation: AI detected degradation, scaled replicas {current_replicas}->{new_replicas}.",
            content=updated_yaml_str,
            sha=file_content.sha,
            branch="main"
        )
        print("[GitOps] Commit successful! ArgoCD will now sync the cluster.")

    except GithubException as e:
        print(f"[ERROR] GitHub API Error: {e}")

# --- Main Execution Loop ---
if __name__ == "__main__":
    print("Starting AI GitOps Controller...")
    print("AI Model loaded and monitoring network...")
    
    while True:
        # Simulate a live feed picking healthy (15ms) or degraded (510ms) latency
        current_latency = np.random.choice([15.0, 510.0]) 
        
        print(f"\n[Monitor] Current Network Latency: {current_latency}ms")
        
        # Ask the AI
        is_degraded = check_network_with_ai(current_latency)
        
        if is_degraded:
            print("[Decision] AI confirms degradation. Initiating GitOps scaling...")
            remediate_via_gitops()
            
            print("[Cooldown] Waiting 2 minutes for ArgoCD to sync and cluster to stabilize...")
            time.sleep(120) 
        else:
            time.sleep(CHECK_INTERVAL)
