```sh
k6 run tests/k6_stress.js --env BASE_URL=<application_url> --insecure-skip-tls-verify
```

```sh
k6 run tests/k6_soak.js --env BASE_URL=<application_url> --insecure-skip-tls-verify
```

`--insecure-skip-tls-verify` wymagane ze wzgledu na self-signed certyfikat do ingressu
