# About
Infrastructure-as-Code project for automated provisioning and benchmarking of managed Kubernetes clusters — **Amazon EKS**, **Azure AKS**, and **Google GKE** — as part of the master's thesis *“Analysis of Managed Kubernetes Services: Comparison of EKS, AKS, and GKE”*.

## 🎯 Project Overview

This repository contains the complete infrastructure automation setup used to:
- Deploy identical microservice-based applications on AWS, Azure, and GCP
- Automate provisioning with **Terraform** and **Ansible**
- Deploy workloads with **Helm**
- Enable observability with **Prometheus** and **Grafana**
- Conduct performance tests using **K6**.

The goal of this project is to **compare managed Kubernetes services** in terms of:
- Performance
- Cost-efficiency
- Security
- Networking
- Ease of management

# How to
[How to setup GKE Cluster](./docs/Setup_GKE.md)

[How to setup AKS Cluster](./docs/Setup_AKS.md)

[How to setup EKS Cluster](./docs/Setup_EKS.md)

[How to perform testing](./docs/Testing.md)

[Access monitoring dashboards](./docs/Monitoring.md)
