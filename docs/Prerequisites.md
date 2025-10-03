Install terraform 1.13.3 (I personally like using [tfenv](https://github.com/tfutils/tfenv) for terraform version management)

https://developer.hashicorp.com/terraform/install

Install python 3.13.7 (I personally like using [pyenv](https://github.com/pyenv/pyenv) for python version management)

Create venv and install required packages

```sh
python3 -m venv .venv
```

```sh
source ./.venv/bin/activate
```

```sh
pip3 install requirements.txt
```

This will install Ansible 12.0.0 [core 2.19.2]

---

Install kubectl 1.34.1 https://kubernetes.io/docs/tasks/tools/

(optional) Install helm v.3.19.0 https://helm.sh/docs/intro/install/
