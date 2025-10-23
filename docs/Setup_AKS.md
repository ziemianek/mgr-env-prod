# Deploy Boutique Application on AKS

## 0. Prerequisites
Start with [Prerequisites](./Prerequisites.md).

## 1. Make sure you have access to [Microsoft Azure Portal](https://portal.azure.com/#home)

## 2. Install [Azure CLI](https://learn.microsoft.com/pl-pl/cli/azure/install-azure-cli?view=azure-cli-latest) for your operating system

## 3. Verify the installation

If successful, you should now be able to use the az CLI:
```sh
az version
```

## 4. Log in to your Azure account

Run:
```sh
az login
```

Then select your subscription and copy its id.
You will need it in the next steps.

## 5. Create and Configure a Service Principal

This account will be used by Ansible and Terraform.
```sh
az ad sp create-for-rbac --name terraform-sp \
  --role="Contributor" \
  --scopes="/subscriptions/<your-subscription-id>"
```

The command outputs credentials similar to:
```json
{
  "appId": "xxxxxxx",
  "displayName": "terraform-sp",
  "password": "yyyyyyy",
  "tenant": "zzzzzzz"
}
```

**Save these values – you’ll need them in the next step.**

## 6. Configure Ansible and Terraform

Go to `ansible/inventories/group_vars/azure/template.vault.yaml` and paste credentials from previous step:

```yaml
vault_azure_client_id: "<appId>"
vault_azure_client_secret: "<password>"
vault_azure_tenant_id: "<tenant>"
vault_azure_subscription_id: "<your-subscription-id>"
```

Rename `template.vault.yaml` → `vault.yaml` and encrypt it with Ansible Vault:
```sh
ansible-vault encrypt ansible/inventories/group_vars/azure/vault.yaml
```

## 7. Run Ansible Automation

Navigate to the `ansible/` directory and run the following playbooks in order:

### 7.1. Create Terraform state storage

Creates an Azure Storage Account and container for storing Terraform state.

```sh
ansible-playbook -i inventories/prod.ini playbooks/azure/tfstate_bucket/create.yaml -v --ask-vault-pass
```

### 7.2. Create Virtual Network

```sh
ansible-playbook -i inventories/prod.ini playbooks/azure/vnet/create.yaml -v --ask-vault-pass
```

### 7.3. Set up application
```sh
ansible-playbook -i inventories/prod.ini playbooks/azure/create_boutique.yaml -v --ask-vault-pass
```

At the end, you will get a URL that you can use to access the application, for example: `https://34.118.2.252/`

# Connect to AKS Cluster using local kubectl

Use the Azure CLI to retrieve credentials:

```sh
az aks get-credentials --resource-group boutique-k8s-rg --name boutique-k8s-cluster
```

Verify that you have access:

```sh
kubectl get ns
```

You should see namespaces from your AKS cluster. The environment is now ready.
