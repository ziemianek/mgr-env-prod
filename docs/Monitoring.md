1. Authenticate to the cluster
```sh
gcloud container clusters get-credentials boutique-k8s-cluster --region europe-central2
```

2. Access grafana
```sh
kubectl port-forward --namespace monitoring svc/kube-prometheus-stack-grafana 3000:80
```
