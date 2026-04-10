# AI-Powered Automated Network Software Deployment

This repository contains an autonomic GitOps controller designed to monitor telecom network simulations and autonomously patch Kubernetes deployments using ML inference.

## Project Structure
* `src/controller/`: Python logic for the K8s Operator and Data Parsing.
* `src/ml/`: Model training and evaluation scripts.
* `k8s/`: Kubernetes manifests (RBAC, Deployments).
* `docker/`: Containerization files.

## Prerequisites
* Minikube / K3s
* Python 3.12+
* Docker

## Quick Start
1. Apply RBAC: `kubectl apply -f k8s/setup/`
2. Apply Apps: `kubectl apply -f k8s/apps/`
3. Build Controller: `cd docker && docker build -t ai-gitops-controller:v1 .`

*Note: This is a milestone prototype for Samsung PRISM.*
