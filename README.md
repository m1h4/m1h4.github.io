# miha software

Source for [www.mihasoftware.com](https://www.mihasoftware.com/), built with Hugo and deployed by GitHub Actions to GitHub Pages.

## Local development

Run `./scripts/hugo server --disableFastRender` and open the local URL it prints. The wrapper downloads the exact official Hugo version in `.hugo-version`, verifies its release checksum, and caches the executable under `.cache/`. It supports macOS and Linux and does not install anything globally. No Node, npm, Go, or Sass installation is needed.

Edit Markdown in `content/`, public files in `static/`, and the custom theme in `themes/m1h4/`. Keep existing filenames and download paths stable. Add descriptive `alt`, `width`, and `height` arguments to figure shortcodes, separated by blank lines. Use `loading="lazy"` for below-the-fold images.

## Validation

Python 3.9 or newer is needed only for validation:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r tests/requirements.txt
./scripts/hugo --environment test --destination .cache/test-site --minify --panicOnWarning
.venv/bin/python scripts/check-site.py .cache/test-site --analytics off
./scripts/hugo --environment production --minify --panicOnWarning
.venv/bin/python scripts/check-site.py public --analytics on
```

The checks parse HTML, validate metadata, internal links, sitemap and feeds, verify analytics inclusion, and compare original images/downloads/icons against the pre-migration SHA-256 manifest. When intentionally adding a content page, add its route to `tests/legacy-contract.json`; preserve existing routes and asset checksums unless a deliberate replacement is approved.

## Publishing

Open a pull request against `master`. CI builds both test and production output and validates them; PRs do not deploy. Merging to `master` builds and uploads the `public/` artifact, then deploys it to the `github-pages` environment. A manual workflow run on `master` can redeploy the current source. Never commit `public/` or edit generated HTML.

Pages must use **GitHub Actions**, with custom domain **www.mihasoftware.com** and **Enforce HTTPS** enabled. DNS remains at its existing provider. With Actions publishing, the domain is managed in Pages settings; a CNAME file is unnecessary. The apex and GitHub hostname redirect to the canonical `www` URL.

The build job has read-only repository permissions. Only the production deployment job receives `pages: write` and `id-token: write`; production deployments are serialized. No personal access token or cross-repository push is used. Monthly Dependabot PRs update the pinned Actions revisions. To update Hugo, change `.hugo-version`, run both validations, and review the browser preview before merging.

## Analytics

Cloudflare Web Analytics uses the public beacon identifier in `config.toml`. It is included only in production builds and is always excluded by `hugo server`, including when the server uses the production environment. Use the test environment for static previews. Cloudflare automatic injection is disabled; DNS and hosting remain on the existing setup.

[Open Web Analytics](https://dash.cloudflare.com/e2ea5e5904a6618a6f0363269c888fdf/web-analytics) to view the `www.mihasoftware.com` site. The service reports visits and pageviews, has six months of accessible history, and does not count custom download events. Browser blockers may suppress measurements. The previous GA4 account and historical data are retained, but this site no longer sends GA4 events.

## Migration and rollback

The source snapshot was imported from private `m1h4/website` commit `8629dfbbcd3a35c3450d53cd93841a897d575a28`; its private history was not imported. That repository is retained as an archived reference after successful cutover.

The tag `pre-hugo-migration-2026-11-06` points to the last generated-site commit, `1e7398276ade5259ad9598794c8cfc485a2f494c`. For emergency rollback:

1. Disable this repository's publishing workflow to prevent a concurrent deployment.
2. Create a branch such as `rollback/generated-site` from the saved tag without rewriting `master`.
3. In Settings → Pages, select **Deploy from a branch**, the rollback branch, and `/ (root)`. Retain the custom domain and HTTPS setting. The saved commit includes its original CNAME and `.nojekyll` files.
4. Verify the website. To restore the source deployment later, select **GitHub Actions**, re-enable the workflow, and dispatch it on `master`.

Normal rollback after subsequent changes is a revert PR followed by the standard deployment workflow.
