# Sorvo Studio Website

Official website for Sorvo Studio, including the studio homepage, privacy policy, and app-ads.txt.

Website: https://www.sorvostudio.com/

## Structure

The site is static HTML, CSS, and JavaScript. All public files are in `public/`; no build step is required.

- `public/index.html`: studio homepage
- `public/privacy.html`: privacy policy
- `public/app-ads.txt`: advertising seller declarations; preserve this filename and URL

## Production hosting

The site is hosted on the studio's BandwagonHost VPS using Nginx and HTTPS. The repository checkout is `/var/www/sorvo-studio-website`, and the web root is its `public/` directory. Only `public/` is served.

The canonical hostname is `www.sorvostudio.com`. The apex domain redirects ordinary pages to HTTPS on `www`; `/app-ads.txt` remains directly accessible on both hostnames.

DNS is managed in Tencent Cloud DNSPod. Both the apex and `www` A records point to the production VPS.

## Updating the site

After committing changes to GitHub, sign in to the production server and run:

```sh
cd /var/www/sorvo-studio-website
git pull --ff-only origin main
```

Static file updates do not require restarting Nginx. Verify the homepage, privacy policy, and `/app-ads.txt` after updates. GitHub pushes alone do not deploy to this server.

## Local preview

```sh
python3 -m http.server 8000 --directory public
```

Open http://localhost:8000/.
