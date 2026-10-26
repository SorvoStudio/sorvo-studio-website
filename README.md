# Sorvo Studio Website

Official website for Sorvo Studio, including the studio homepage, privacy policy, and app-ads.txt.

Website: https://www.sorvostudio.com/

## Structure

The site is static HTML, CSS, and JavaScript. All public files are in `public/`; no build step is required.

- `public/index.html`: studio homepage
- `public/privacy.html`: privacy policy
- `public/app-ads.txt`: advertising seller declarations; preserve this filename and URL

## Production hosting

The site is hosted on the studio's BandwagonHost VPS using Nginx and HTTPS. The live web root is `/var/www/sorvo-auto/current`, an atomic symlink to a release's `public/` directory. Only `public/` is served. The original checkout `/var/www/sorvo-studio-website` is retained for maintenance; it is no longer the live web root.

The canonical hostname is `www.sorvostudio.com`. The apex domain redirects ordinary pages to HTTPS on `www`; `/app-ads.txt` remains directly accessible on both hostnames.

DNS is managed in Tencent Cloud DNSPod. Both the apex and `www` A records point to the production VPS.

## Updating the site

Push changes to `main`. The server checks GitHub every 60 seconds and publishes new commits automatically (normally within 1–2 minutes, depending on network availability). This is server-side polling, not a GitHub Actions workflow or webhook. Other branches are not published.

The restricted `sorvo-deploy` service fetches this public repository without SSH keys or GitHub secrets. It checks required files, rejects symlinks/special files, stages a complete release, then atomically switches the live directory. A failed download or validation leaves the previous version live and is retried at the next check. Repository scripts are never executed. Changes to files under `deploy/` require manual installation by a server administrator.

Verify the homepage, privacy policy, and `/app-ads.txt` after updates. The live commit is available at https://www.sorvostudio.com/deployment-version.txt.

Server administration:

```sh
# Status / recent logs
systemctl status sorvo-deploy.timer
journalctl -u sorvo-deploy.service -n 30
# Publish immediately
sudo systemctl start sorvo-deploy.service
# Pause / resume automatic publishing
sudo systemctl stop sorvo-deploy.timer
sudo systemctl start sorvo-deploy.timer
```

Installed files: `/usr/local/lib/sorvo-deploy.py` and `/etc/systemd/system/sorvo-deploy.{service,timer}`. Source copies are in `deploy/`. Git state is in `/var/lib/sorvo-deploy`; releases are retained under `/var/www/sorvo-auto/releases/<commit>/public`. Monitor disk space and remove unneeded old releases during maintenance.

To roll back, stop the timer, wait for any running service to finish, then replace `current` with a symlink to a previously validated release using `ln -s TARGET current.next && mv -Tf current.next current` from `/var/www/sorvo-auto`. Keep the timer stopped until the GitHub change is reverted; resuming it publishes the latest `main` again.

## HTTPS and server configuration

The production Nginx configuration is recorded in `deploy/nginx.conf`. Changes to this file in GitHub do not automatically change the running server configuration.

The Let's Encrypt certificate is named `sorvo-studio-website`. Certbot uses HTTP validation with web root `/var/www/sorvo-acme`; the `snap.certbot.renew.timer` service handles scheduled renewal. Keep port 80 and `/.well-known/acme-challenge/` reachable on both domain names.

To test renewal:

```sh
sudo /snap/bin/certbot renew --cert-name sorvo-studio-website --dry-run
```

## Local preview

```sh
python3 -m http.server 8000 --directory public
```

Open http://localhost:8000/.
