# AI-Driven GitOps for Telecom Networks

This repository contains a closed-loop automation system built for the Samsung PRISM project. It combines machine learning and GitOps to monitor simulated telecom network traffic and automatically scale Kubernetes resources when performance degrades.

Traditionally, network scaling requires manual intervention. This project automates the process by using a machine learning model to detect latency spikes and a Python controller to push declarative infrastructure updates directly to GitHub. ArgoCD then syncs and applies these changes to the live cluster.

---

## Architecture

- **Network Simulation (Mininet):** Generates real-time network traffic and latency metrics.
- **Machine Learning Model (Scikit-Learn):** A Random Forest classifier trained to distinguish between healthy traffic and degraded network states.
- **GitOps Controller (Python):** Monitors the network, queries the ML model, and updates Kubernetes deployment files in GitHub if an issue is detected.
- **ArgoCD & Kubernetes (Minikube):** ArgoCD watches the repository for changes and automatically scales the application pods to handle the degraded network state.

---

## Repository Structure

```text
.
├── k8s/                # Kubernetes manifests and ArgoCD configurations
├── models/             # Trained Machine Learning models (.joblib)
├── simulation/         # Network emulation scripts and ground-truth datasets
└── src/                # Source code
    ├── ai/             # ML training scripts
    └── controller/     # GitOps orchestrator loop
```

##  Prerequisites
Minikube (or similar local Kubernetes cluster)
Python 3.12+
ArgoCD installed in the cluster
A GitHub Personal Access Token (stored in a local .env file)


##  How to Run
1. Start the Infrastructure
```
    Start your Minikube cluster and set up port-forwarding to access the ArgoCD UI:
    minikube start
    kubectl port-forward svc/argocd-server -n argocd 8080:443
```
2. Generate Network Data
Run the Mininet simulation to generate the baseline dataset containing healthy and degraded traffic:
```
sudo python3 simulation/network_sim.py
```
4. Train the Model

Activate your Python virtual environment and train the classifier on the generated data:
```
source venv/bin/activate
python3 src/ai/train_model.py
```
4. Start the Controller

Run the orchestrator script to begin monitoring the network and enabling automated scaling:
```
python3 src/controller/gitops_controller.py
```

##    Workflow Summary:

Once running:
>    The controller continuously monitors simulated network conditions.
>    The ML model detects latency spikes or degraded performance.
>    The controller commits updated Kubernetes configurations to GitHub.
>    ArgoCD detects the change and syncs it to the cluster.
>    Kubernetes scales pods automatically to stabilize the network.

##    Key Highlights
>    Closed-loop automation using AI + GitOps
>    Real-time anomaly detection with machine learning
>    Fully declarative infrastructure updates
>    Zero manual intervention for scaling decisions
