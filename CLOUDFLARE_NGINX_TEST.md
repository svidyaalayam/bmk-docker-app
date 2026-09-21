# Cloudflare and VM Nginx: test environment

This configuration makes the test platform and each school available over
HTTPS, for example `https://uk-telugu-test.balamukundam.com`.

## 1. Cloudflare DNS and TLS

In the `balamukundam.com` Cloudflare zone, create these proxied (orange-cloud)
DNS records pointing to the VM public IP:

| Type | Name | Target |
| --- | --- | --- |
| A | `test` | VM public IP |
| A | `*` | VM public IP |

Create a Cloudflare Origin Certificate whose hostnames include both
`test.balamukundam.com` and `*.balamukundam.com`. Save the certificate and
private key on the VM as:

```
/etc/ssl/cloudflare/balamukundam-origin.pem
/etc/ssl/cloudflare/balamukundam-origin.key
```

Restrict the key file so only root can read it. In Cloudflare, set **SSL/TLS
encryption mode** to **Full (strict)**. Do not use Flexible mode.

## 2. VM Nginx

Copy `deploy/nginx/bmk-test.conf.example` to
`/etc/nginx/sites-available/bmk-test.conf`, enable it, then validate and reload
Nginx:

```sh
sudo ln -s /etc/nginx/sites-available/bmk-test.conf /etc/nginx/sites-enabled/bmk-test.conf
sudo nginx -t
sudo systemctl reload nginx
```

The template proxies to `127.0.0.1:8080`, so keep the Docker test deployment
bound to that port (`WEB_PORT=8080`). The supplied test environment template
sets `WEB_BIND_HOST=127.0.0.1` and `API_BIND_HOST=127.0.0.1`, so VM Nginx is the
only public entry point.

When test, staging, and production share one VM, use
`deploy/nginx/bmk-environments.conf.example` instead. It identifies each
environment from the hostname and routes to separate local ports:

| Hostname | Environment | Docker UI port |
| --- | --- | --- |
| `test.balamukundam.com` or `*-test.balamukundam.com` | Test | 8080 |
| `staging.balamukundam.com` or `*-staging.balamukundam.com` | Staging | 8081 |
| `balamukundam.com` or unsuffixed tenant hostname | Production | 8082 |

## 3. Deploy the application

Use the test environment file and rebuild the UI, then the API startup runs the
school-slug migrations automatically:

```sh
docker compose --env-file .env.test up --build -d
```

Confirm that `APP_DOMAIN` and `VITE_APP_DOMAIN` are both
`balamukundam.com`, and that both tenant-suffix settings are `-test`. The
resulting school URLs are first-level subdomains, such as
`london-telugu-test.balamukundam.com` and
`uk-telugu-test.balamukundam.com`.
