# Access monitoring dashboards

## 1. Authenticate to your cluster

## 2. Forward grafana port from cluster to localhost
```sh
kubectl port-forward --namespace monitoring svc/kube-prometheus-stack-grafana 3000:80
```

## 3. Open `http://localhost:3000` and log in with your credentials (see vaults in ansible/)
