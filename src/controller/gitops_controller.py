import os
import time
import base64
import yaml
from github import Github
from github.GithubException import GithubException

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "hashfydr/ai-gitops-telecom"
FILE_PATH = "k8s/apps/dummy-nginx-deployment.yaml"
CHECK_INTERVAL = 30 # seconds

def evaluate_network_state():
    """
    Simulates the ML Model evaluation.
    In a real scenario, this reads your training_data.csv and runs model.predict()
    Returns True if network is degraded, False if healthy.
    """
    print("[AI] Evaluating network state from simulation data...")
    # For demonstration of the GitOps loop, we will hardcode a failure detection
    # after the script starts. In production, connect this to your ML inference.
    time.sleep(10) 
    return True 

def remediate_via_gitops():
    """
    Acts as the GitOps Developer. Commits a YAML fix to GitHub.
    """
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN environment variable not set.")
        return

    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    
    try:
        # 1. Fetch the current deployment YAML from GitHub
        file_content = repo.get_contents(FILE_PATH, ref="main")
        yaml_content = base64.b64decode(file_content.content).decode("utf-8")
        parsed_yaml = yaml.safe_load(yaml_content)

        print("[GitOps] Current replicas:", parsed_yaml['spec']['replicas'])

        # 2. The AI Decision: Scale up to handle degraded network latency
        new_replicas = 3
        if parsed_yaml['spec']['replicas'] == new_replicas:
            print("[GitOps] System already remediated. No action needed.")
            return

        parsed_yaml['spec']['replicas'] = new_replicas
        
        # 3. Convert back to YAML string
        updated_yaml_str = yaml.dump(parsed_yaml, default_flow_style=False)

        # 4. Commit the change to GitHub
        print(f"[GitOps] Committing remediation to GitHub: Scaling {parsed_yaml['metadata']['name']} to {new_replicas} replicas.")
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
            # Sleep longer after remediation to allow ArgoCD to sync
            time.sleep(120) 
        else:
            print("[AI] Network healthy.")
            time.sleep(CHECK_INTERVAL)
