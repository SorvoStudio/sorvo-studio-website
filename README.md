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

Push changes to `main`. [GitHub Actions](https://github.com/SorvoStudio/sorvo-studio-website/actions/workflows/deploy.yml) runs **Deploy website**, connects to the server over SSH, publishes the triggering commit, and checks the live version and website pages. Use the standard green/red job status and step logs to see success or errors. The workflow also supports **Run workflow** on `main`.

The old `sorvo-deploy.timer` polling timer is disabled. GitHub Actions is the automatic deployment entry point. The server only accepts `deploy <full commit SHA>`, and rejects a SHA that is no longer the current `main` tip. If an older queued run reports an outdated commit, check the newest run instead. Revert changes on `main` to deploy an older site's content as a new commit.

Repository secrets:
- `SORVO_DEPLOY_KEY`: dedicated SSH private key for the restricted `sorvo-deploy` account.
- `SORVO_KNOWN_HOSTS`: server host public key verified through the VPS console.

The account has no administrator privileges, interactive shell, file-transfer access, or forwarding. It fetches the fixed public repository, validates required files, rejects symlinks/special files, and atomically switches the live release. Repository scripts are never executed. Validation failures preserve the previous release; a failure in the later public HTTP check must be investigated using the workflow logs and live site.

The live commit is available at https://www.sorvostudio.com/deployment-version.txt.

Server administration:

```sh
# Verify the old timer stays disabled
systemctl is-enabled sorvo-deploy.timer
# Emergency manual publish of current main
sudo systemctl start sorvo-deploy.service
# Logs for emergency manual runs (normal deploy logs are in Actions)
journalctl -u sorvo-deploy.service -n 30
```

Installed scripts: `/usr/local/lib/sorvo-deploy.py` and `/usr/local/lib/sorvo-ssh-deploy.py`. SSH restrictions: `/etc/ssh/sshd_config.d/90-sorvo-deploy.conf`; authorized public key: `/etc/ssh/sorvo-deploy.keys`. Source copies are in `deploy/`; the active workflow is `.github/workflows/deploy.yml`. Changes to server scripts/configuration require manual installation by a server administrator.

Git state is in `/var/lib/sorvo-deploy`; releases are retained under `/var/www/sorvo-auto/releases/<commit>/public`. Monitor disk space and remove unneeded old releases during maintenance.

For emergency rollback, disable the GitHub workflow and wait for any running deployment to finish, then atomically switch `/var/www/sorvo-auto/current` to a previously validated release. Keep the workflow disabled until the problematic GitHub change is reverted. Normal rollback is a revert commit on `main`.

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
