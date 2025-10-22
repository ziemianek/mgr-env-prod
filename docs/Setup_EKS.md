# Deploy Boutique Application on EKS

## 0. Prerequisites

Start with [Prerequisites](./Prerequisites.md)

## 1. Log in to [AWS Management Console](https://aws.amazon.com/console/)

## 2. Setup Terraform IAM User
In AWS, the security model is different. We **NEVER** use the `root` account for work. Instead, we create an IAM administrator account and generate access keys for it.

In the search bar at the top, type `IAM` and go to the IAM service.

In the menu on the left, click `Users`, then `Create user`. Enter a username, for example `terraform-admin`.
On the next page ("Set permissions"), select Attach policies directly.

Above the list of policies, click the Create policy button. This will open a new browser tab.

In the new tab, select the JSON editor.

Delete all the existing content and paste the following JSON policy. This policy gives Terraform permissions to manage EKS, VPC, EC2, IAM roles, and S3, and is much safer than AdministratorAccess.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "TerraformEKSPermissions",
            "Effect": "Allow",
            "Action": [
                "ec2:*",
                "s3:*",
                "eks:*",
                "autoscaling:*",
                "cloudformation:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMForEKSRoles",
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "iam:PassRole",
                "iam:CreateInstanceProfile",
                "iam:AddRoleToInstanceProfile",
                "iam:ListInstanceProfiles",
                "iam:ListRoles",
                "iam:TagRole",
                "iam:GetRole",
                "iam:GetPolicy",
                "iam:GetPolicyVersion",
                "iam:ListAttachedRolePolicies"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AllowTerraformToVerify",
            "Effect": "Allow",
            "Action": [
                "iam:ListAccountAliases",
                "iam:GetUser"
            ],
            "Resource": "*"
        }
    ]
}
```

Click Next.

Give the policy a name, for example, TerraformEKSFullPolicy.

Click Create policy.

Now, return to the original browser tab where you were creating the user.

Click the Refresh button (the circular arrow icon) above the list of policies.

In the search bar, type the name of your new policy (e.g., TerraformEKSFullPolicy).

Check the box next to your new policy.

Click Next until the user is created.






Now generate access keys (your Service Principal):

Click on the name of the user you just created (terraform-admin).

Go to the "Security credentials" tab.

Scroll down to the "Access keys" section and click "Create access key".

Choose the "Command Line Interface (CLI)" option.

Confirm that you understand the recommendations and click "Create access key".

IMPORTANT: Two values will be displayed — the Access key ID and the Secret access key. Save them immediately in a secure place. Once you close this window, you will never be able to see the secret key again.


## 3. Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## 4. Verify the installation

If successful, you should now be able to use the aws CLI:
```sh
aws --version
```

## 4. Configure your AWS credentials

Run:
```sh
aws configure
```

Enter your:

AWS Access Key ID

AWS Secret Access Key

Default region name (e.g., us-east-1 or eu-central-1)

Default output format (json)

To verify:

aws sts get-caller-identity

6. Enable Required Services

EKS uses multiple underlying services, which must be available in your account:

EC2 (compute and networking)

IAM (authentication)

VPC (networking)

CloudFormation (resource orchestration)

S3 (Terraform backend)

EKS (managed Kubernetes)

These are automatically available in most regions, but you can confirm with:

aws eks describe-addon-versions --region eu-central-1

7. Configure Ansible and Terraform

Create a vault file for AWS credentials:
ansible/inventories/group_vars/aws/template.vault.yaml

Add:

aws_access_key: "<your-access-key-id>"
aws_secret_key: "<your-secret-access-key>"
aws_region: "eu-central-1"


Encrypt it:

ansible-vault encrypt ansible/inventories/group_vars/aws/template.vault.yaml


Rename template.vault.yaml → vault.yaml.

8. Run Ansible Automation

Navigate to the ansible/ directory and execute the playbooks below in order.

8.1. Create Terraform State S3 Bucket

This creates an S3 bucket for storing Terraform state files.

ansible-playbook -i inventories/prod.ini playbooks/aws/tfstate_bucket/create.yaml -v --ask-vault-pass

8.2. Create VPC

Creates a dedicated VPC with subnets and security groups for the cluster.

ansible-playbook -i inventories/prod.ini playbooks/aws/vpc/create.yaml -v --ask-vault-pass

8.3. Set up Application (EKS + Boutique)

Creates the EKS cluster, worker nodes, and deploys the Boutique app via Helm.

ansible-playbook -i inventories/prod.ini playbooks/aws/create_boutique.yaml -v --ask-vault-pass


At the end, you will receive a public endpoint to access the application, for example:
https://a1b2c3d4e5f6g7h8.elb.us-east-1.amazonaws.com/

Connect to EKS Cluster using local kubectl

Ensure you have kubectl and aws-iam-authenticator installed (the latter is included in AWS CLI v2).

Retrieve credentials:

aws eks update-kubeconfig --name boutique-k8s-cluster --region eu-central-1


Verify access:

kubectl get ns


If the output lists Kubernetes namespaces, your connection is active.

Grafana

Ansible automation automatically forwards Grafana to localhost:3000.

Use the credentials stored in
ansible/inventories/group_vars/aws/vault.yaml.