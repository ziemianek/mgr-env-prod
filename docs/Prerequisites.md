# Prerequisites

Make sure the following tools are installed:

- [Terraform 1.13.3](https://developer.hashicorp.com/terraform/install)  
  👉 Recommended: use [tfenv](https://github.com/tfutils/tfenv) for version management

- [Python 3.13.7](https://www.python.org/downloads/)  
  👉 Recommended: use [pyenv](https://github.com/pyenv/pyenv) for version management

- [kubectl 1.34.1](https://kubernetes.io/docs/tasks/tools/)

- [Helm 3.19.0](https://helm.sh/docs/intro/install/)

- [k6 v1.3.0](https://grafana.com/docs/k6/latest/set-up/install-k6/)

Create and activate a virtual environment (This will install Ansible 12.0.0 [core 2.19.2]):
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
