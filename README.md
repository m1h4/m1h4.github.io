# miha software

Source for [www.mihasoftware.com](https://www.mihasoftware.com/), built with Hugo and deployed by GitHub Actions to GitHub Pages.

## Local development

Run `./scripts/hugo server --disableFastRender` and open the local URL it prints. The wrapper downloads the exact official Hugo version in `.hugo-version`, verifies its release checksum, and caches the executable under `.cache/`. It supports macOS and Linux and does not install anything globally. No Node, npm, Go, or Sass installation is needed.

Edit Markdown in `content/`, public files in `static/`, and the custom theme in `themes/m1h4/`. Keep existing filenames and download paths stable. Add descriptive `alt`, `width`, and `height` arguments to figure shortcodes, separated by blank lines. Use `loading="lazy"` for below-the-fold images.

## Portfolio content

The app catalogue is generated from `content/apps/`. Each app supplies `description`, `platform`, `availability`, `compatibility`, and `weight` in its front matter. Downloadable apps also supply `version`, `download`, and `downloadlabel`; omit these when there is no available download. Set `featured: true` to include an app on the homepage. Optional `screenshot` and `screenshotalt` display an existing image; `artmark` and `artcaption` provide a typographic alternative. Set `toc: true` for longer instructions. Do not label historical compatibility as newly tested.

Photos use paired `gallery` and `photo` shortcodes, as demonstrated in `content/photos.md`. Each photo supplies its original `src`, `title`, `caption`, `alt`, and loading priority; its inner Markdown holds the original commentary. Hugo generates 640, 1200, and 1800px WebP variants without changing the originals. The enlarged view loads an original only when opened. The wrapper keeps processing caches under `.cache/` (override with `HUGO_CACHEDIR` if needed).

Writing uses the original `date` as its publication date. Add `lastmod` explicitly only for a substantive content update; changing the theme does not change article dates. Appearance follows the device preference until the visitor chooses Light or Dark in the footer. No JavaScript is required to navigate, download apps, or open original photos.

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

Cloudflare Web Analytics uses the public beacon identifier in `config.toml`. Events and Photo Resize landing, privacy, support, and catalogue pages opt out with `noAnalytics: true`; their routes are recorded in `tests/legacy-contract.json`. Elsewhere it is included only in production builds and is always excluded by `hugo server`, including when the server uses the production environment. Use the test environment for static previews. Cloudflare automatic injection is disabled; DNS and hosting remain on the existing setup.

[Open Web Analytics](https://dash.cloudflare.com/e2ea5e5904a6618a6f0363269c888fdf/web-analytics) to view the `www.mihasoftware.com` site. The service reports visits and pageviews, has six months of accessible history, and does not count custom download events. Browser blockers may suppress measurements. The previous GA4 account and historical data are retained, but this site no longer sends GA4 events.

## Migration and rollback

The source snapshot was imported from private `m1h4/website` commit `8629dfbbcd3a35c3450d53cd93841a897d575a28`; its private history was not imported. That repository is retained as an archived reference after successful cutover.

The tag `pre-hugo-migration-2026-11-06` points to the last generated-site commit, `1e7398276ade5259ad9598794c8cfc485a2f494c`. For emergency rollback:

1. Disable this repository's publishing workflow to prevent a concurrent deployment.
2. Create a branch such as `rollback/generated-site` from the saved tag without rewriting `master`.
3. In Settings → Pages, select **Deploy from a branch**, the rollback branch, and `/ (root)`. Retain the custom domain and HTTPS setting. The saved commit includes its original CNAME and `.nojekyll` files.
4. Verify the website. To restore the source deployment later, select **GitHub Actions**, re-enable the workflow, and dispatch it on `master`.

Normal rollback after subsequent changes is a revert PR followed by the standard deployment workflow.

## Events release pages

`content/events/` contains the English and Croatian landing, privacy and support pages. Keep `/events/`, `/events/index-hr.html`, `/events/privacy.html`, `/events/privacy-hr.html`, `/events/support.html` and `/events/support-hr.html` stable: the Android app uses these URLs. The shared Events layout is `themes/m1h4/layouts/events.html`; screenshots and the icon are in `static/events/` and contain only fictional calendar data. Update the existing page when editing either translation, and preserve the same-page language links.

The catalogue entry is `content/apps/events.md`. The app is still preparing for release; add its verified Google Play link only when published. Support uses `support@mihasoftware.com`. Changes deploy through the normal pull-request and Actions workflow.

## Photo Resize release pages

The catalogue/English landing page is `content/apps/photo-resize.md`. Its Croatian translation, bilingual privacy policy, and support pages are in `content/photo-resize/`, with a non-rendered section index. Preserve `/apps/photo-resize/`, `/apps/photo-resize/hr/`, `/apps/photo-resize/privacy/`, `/apps/photo-resize/privacy/hr/`, `/apps/photo-resize/support/` and `/apps/photo-resize/support/hr/`; the Android app already links to the privacy URLs. These pages opt out of analytics. The shared layout is `themes/m1h4/layouts/photo-resize.html`; actual app captures and the icon are in `static/photo-resize/`. The photograph is synthetic demo content.

The rebuilt app is in internal testing; add its public Google Play link only after availability is verified. Support remains `mihovilic@gmail.com`, matching the app. Original archived screenshots and their URLs remain intact.

## Beam release pages

The catalogue/English landing page is `content/apps/beam.md`. Its Croatian translation, bilingual privacy policy, and support pages are in `content/beam/`, with a non-rendered section index. Preserve `/apps/beam/`, `/apps/beam/hr/`, `/apps/beam/privacy/`, `/apps/beam/privacy/hr/`, `/apps/beam/support/` and `/apps/beam/support/hr/`; the App Store listing links to the privacy and support URLs. The shared layout is `themes/m1h4/layouts/beam.html`, which reuses the Photo Resize page styles; the icon and screenshots are in `static/beam/` and show only generated sample photos.

Beam 1.0 is being prepared for the App Store; add its App Store link only after the app is released. Support uses `support@mihasoftware.com`. These pages opt out of analytics with `noAnalytics: true`, and their routes are recorded in `tests/legacy-contract.json`.
