# Istio Ingress Gateway Helm Chart

This Helm chart configures the Istio ingress gateway and its virtual service for routing traffic to your application services.

## Components

- **Gateway**: Configures the Istio ingress gateway with HTTP and HTTPS ports
- **VirtualService**: Routes traffic from the gateway to internal services

## Installation

```bash
# From the repo root
helm install istio-ingress-gateway ./helm/istio-ingress-gateway-chart --namespace istio-ingress --values ./helm/istio-ingress-gateway-chart/values.yaml
```

## Configuration

Edit the `values.yaml` file to customize:

- Domain name
- Gateway configuration
- Virtual service routing destinations

### Example values.yaml override

```yaml
domain:
  name: "your-domain.com"

virtualService:
  routes:
    - destination:
        host: "your-service.namespace.svc.cluster.local"
        port: 8080
```

## Updating

```bash
helm upgrade istio-ingress-gateway ./helm/istio-ingress-gateway-chart --namespace istio-ingress --values ./helm/istio-ingress-gateway-chart/values.yaml
```

## Uninstalling

```bash
helm uninstall istio-ingress-gateway --namespace istio-ingress
```