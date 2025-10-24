1) Ustal nazwę node resource group (MC RG)
MC_RG=$(az aks show -g boutique-aks -n boutique-k8s-cluster --query nodeResourceGroup -o tsv)
echo "$MC_RG"

2) Pobierz tożsamości AKS

Tożsamość control plane (managed identity) – to ona zarządza LB/VMSS:

CONTROL_PLANE_MI_PRINCIPAL_ID=$(az aks show -g boutique-aks -n boutique-k8s-cluster --query identity.principalId -o tsv)
echo "$CONTROL_PLANE_MI_PRINCIPAL_ID"


Kubelet identity (clientId masz już: ec448754-fddc-...) – na wszelki wypadek pobierz principalId:

KUBELET_CLIENT_ID=$(az aks show -g boutique-aks -n boutique-k8s-cluster --query identityProfile.kubeletidentity.clientId -o tsv)
KUBELET_PRINCIPAL_ID=$(az ad sp show --id "$KUBELET_CLIENT_ID" --query id -o tsv)
echo "$KUBELET_PRINCIPAL_ID"

3) Przyznaj właściwe role na MC RG (node resource group)

Najbezpieczniej dać Contributor (obejmuje Compute + Network). Jeśli wolisz minimalne uprawnienia, użyj co najmniej:

Network Contributor (dla LB/PIP) +

Virtual Machine Contributor (dla operacji na VMSS).

Wariant prosty (zalecany):
SUB_ID=$(az account show --query id -o tsv)

# Control plane MI – kluczowe
az role assignment create \
  --assignee-object-id "$CONTROL_PLANE_MI_PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Contributor" \
  --scope "/subscriptions/$SUB_ID/resourceGroups/$MC_RG"

# (opcjonalnie) kubelet MI
az role assignment create \
  --assignee-object-id "$KUBELET_PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Contributor" \
  --scope "/subscriptions/$SUB_ID/resourceGroups/$MC_RG"


Jeśli masz polityki bezpieczeństwa, zamiast „Contributor” możesz dać:

Network Contributor i Virtual Machine Contributor na tym samym scope.

4) Jeśli chcesz używać publicznego IP w innej RG niż MC (np. boutique-network)

nadaj Network Contributor tożsamości control plane na tę RG:

az role assignment create \
  --assignee-object-id "$CONTROL_PLANE_MI_PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Network Contributor" \
  --scope "/subscriptions/$SUB_ID/resourceGroups/boutique-network"


oraz dodaj adnotację w Service:

metadata:
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-resource-group: boutique-network


(jeśli nie dodasz adnotacji, AKS będzie tworzył LB/PIP w MC RG, co też jest OK).

5) Zastosuj zmiany i odśwież Service

Po nadaniu ról odczekaj ~1–3 min, potem:

kubectl annotate svc -n istio-ingress istio-ingress-gateway kubernetes.io/change-cause="$(date)" --overwrite
kubectl get svc -n istio-ingress istio-ingress-gateway -w


-w pozwoli zobaczyć przejście z <pending> na publiczny IP.