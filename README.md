# Description

tba

# Usage & Development

Ready to use development environment is provided as DevContainer. Check the guide below to learn how to set it up. 

## VSCode DevContainer – Setup & Use

### What is a DevContainer?
A **DevContainer** is a Docker-based development environment defined in `.devcontainer/`. It ensures consistent tooling/configuration across machines.

---

### Basic Setup

1. Install `Dev Containers (by Microsoft)` VSCode Extension:

2. Build image

3. Open devcontainer

---

## 🚀 Using DevContainer

1. Open the project folder in VSCode.
2. Press `F1` → **Dev Containers: Reopen in Container**
3. VSCode builds & runs the container, mounts your code, installs tools.

---

## 🔁 Add Common Tools

Update Dockerfile or `postCreateCommand`:

Example – Install AWS CLI:
```Dockerfile
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && ./aws/install
```

Other tools to consider:
- Terraform
- kubectl
- Ansible
- Helm

---

## 📁 Typical Files

- `.devcontainer/devcontainer.json`
- `.devcontainer/Dockerfile`
- `.devcontainer/.env` *(should not be committed)*

---

## 💡 Tips

- Use **mounts** for local secrets or config files.
- Use **non-root user** for better security.
- Align with your **CI/CD Dockerfile** for parity.

---

Need a ready-to-use DevContainer for Terraform or FastAPI? Just ask.
