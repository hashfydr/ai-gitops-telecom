import os
import sys
import time
import base64
import yaml
from dotenv import load_dotenv  # <-- ADD THIS
from github import Github, Auth
from github.GithubException import GithubException

env_path = os.path.join(os.getcwd(), '.env')
if not os.path.exists(env_path):
    print(f"[CRITICAL ERROR] No .env file found at: {env_path}")
    sys.exit(1)

# Load the hidden .env file automatically
load_dotenv()  # <-- ADD THIS

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("[CRITICAL ERROR] The .env file was found, but GITHUB_TOKEN is empty inside it!")
    print("Make sure the file literally contains: GITHUB_TOKEN=\"ghp_your_token\"")
    sys.exit(1)
# configuration
REPO_NAME = "hashfydr/ai-gitops-telecom" # <-- Ensure your username is here
FILE_PATH = "k8s/apps/dummy-nginx-deployment.yaml"
CHECK_INTERVAL = 30 # seconds
def evaluate_network_state():
    """Simulates the ML Model evaluation."""
    print("[AI] Evaluating network state from simulation data...")
    time.sleep(10) 
    return True 

def remediate_via_gitops():
    """Acts as the GitOps Developer. Commits a YAML fix to GitHub."""
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN environment variable not set.")
        return

    # Fix 1: Use the modern Auth.Token method to eliminate deprecation warnings
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)
    
    try:
        # 1. Fetch the current deployment YAML from GitHub
        file_content = repo.get_contents(FILE_PATH, ref="main")
        yaml_content = base64.b64decode(file_content.content).decode("utf-8")
        
        # Fix 2: Parse Multi-Document YAML files (handling '---')
        docs = list(yaml.safe_load_all(yaml_content))

        # 2. Iterate through documents to find the Deployment
        action_taken = False
        for doc in docs:
            if doc and doc.get('kind') == 'Deployment':
                print(f"[GitOps] Found Deployment: {doc['metadata']['name']}")
                current_replicas = doc['spec'].get('replicas', 1)
                print(f"[GitOps] Current replicas: {current_replicas}")

                new_replicas = 3
                if current_replicas == new_replicas:
                    print("[GitOps] System already remediated. No action needed.")
                    return

                # Update the replicas
                doc['spec']['replicas'] = new_replicas
                action_taken = True
                break # We just update the first deployment we find

        if not action_taken:
            print("[ERROR] No Deployment found in the YAML file to update.")
            return

        # 3. Convert back to a multi-document YAML string safely
        updated_yaml_str = yaml.safe_dump_all(docs, default_flow_style=False)

        # 4. Commit the change to GitHub
        print("[GitOps] Committing remediation to GitHub: Scaling up replicas.")
        repo.update_file(
            path=file_content.path,
            message="Auto-Remediation: AI detected network degradation, scaling up replicas.",
            content=updated_yaml_str,
            sha=file_content.sha,
            branch="main"
        )
        print("[GitOps] Commit successful! ArgoCD will now sync the cluster.")

    except GithubException as e:
        print(f"[ERROR] GitHub API Error: {e}")

if __name__ == "__main__":
    print("Starting AI GitOps Controller in true Declarative Mode...")
    while True:
        is_degraded = evaluate_network_state()
        if is_degraded:
            print("[AI] ALERT: Network degradation predicted!")
            remediate_via_gitops()
            time.sleep(120) 
        else:
            print("[AI] Network healthy.")
            time.sleep(CHECK_INTERVAL)
