# Run load tests

**NOTE:** `--insecure-skip-tls-verify` is required because of self-signed TLS certificate for Ingress

## 1. Run stress test
```sh
k6 run tests/k6_stress.js --env BASE_URL=<application_url> --insecure-skip-tls-verify
```

## 2. Run soak test
```sh
k6 run tests/k6_soak.js --env BASE_URL=<application_url> --insecure-skip-tls-verify
```
