# miha software

Source for [www.mihasoftware.com](https://www.mihasoftware.com/), built with Hugo and deployed by GitHub Actions to GitHub Pages.

## Local development

Run `./scripts/hugo server --disableFastRender` and open the local URL it prints. The wrapper downloads the exact official Hugo version in `.hugo-version`, verifies its release checksum, and caches the executable under `.cache/`. It supports macOS and Linux and does not install anything globally. No Node, npm, Go, or Sass installation is needed.

Edit Markdown in `content/`, public files in `static/`, and the custom theme in `themes/m1h4/`. Keep existing filenames and download paths stable. Add descriptive `alt`, `width`, and `height` arguments to figure shortcodes, separated by blank lines. Use `loading="lazy"` for below-the-fold images.

## Portfolio content

The homepage is the current app catalogue, generated from `content/apps/`. Set `collection: current` for current apps and `collection: archive` for older apps, with `weight` controlling order within each group. The archive lives at `/apps/archive/`; individual app URLs and original downloads stay stable. `/apps/` redirects to the homepage and `/apps/events/` redirects to `/events/`.

Each app supplies `description`, `platform`, and `availability`. Archive apps, which render their own page with `apps/single.html`, also supply `compatibility`, `version`, `download`, and `downloadlabel`, plus an optional `screenshot`. Current apps use `icon`, `screenshot`, and `screenshotdark` for their home-page card, where `screenshotdark` is left out for an app with a single capture, such as Beam; `producturl` optionally links the card directly to a product landing page. Home cards and archive rows are block links with the class `app-link`, which the validator counts. Do not label historical compatibility as newly tested or offer store downloads before publication.

Use matched, actual app captures for light and dark mode. `theme-picture` generates responsive WebP variants, follows the system theme without JavaScript, and follows a manual appearance choice when JavaScript is available. Given one capture only, it renders that image in both themes. Product landing pages use `product: true`, `intro`, `releasestatus`, and `screenshotcaption` to place their screenshot beside the opening copy on desktop and before the detailed features on phones. English and Croatian capture pairs are in `static/events/` and `static/photo-resize/`, and Beam's single captures in `static/beam/`; all sample calendar/photo content is fictional. Keep text and framing consistent across each pair.

The site has Apps and About & Contact navigation. Posts and photography are retired; the old Analyzed release post redirects to its app page. Other retired pages use the normal 404. RSS is disabled. Appearance follows the device preference until the visitor chooses Light or Dark in the footer. No JavaScript is required to navigate or download apps.

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

`./scripts/build preview` and `./scripts/build production` do the same in one step: each empties `public/`, builds into it, and validates the result.

The checks parse HTML, validate metadata, internal links, redirects, the sitemap, current/archive app membership, and paired screenshot sources. They verify analytics inclusion, removal of retired content, and unchanged original app downloads/screenshots/icons. Update `tests/legacy-contract.json` for deliberate content changes; preserve app support, privacy, translation, and download URLs.

## Publishing

Open a pull request against `master`. CI builds both test and production output and validates them; PRs do not deploy. Merging to `master` builds and uploads the `public/` artifact, then deploys it to the `github-pages` environment. A manual workflow run on `master` can redeploy the current source. Never commit `public/` or edit generated HTML.

Pages must use **GitHub Actions**, with custom domain **www.mihasoftware.com** and **Enforce HTTPS** enabled. DNS remains at its existing provider. With Actions publishing, the domain is managed in Pages settings; a CNAME file is unnecessary. The apex and GitHub hostname redirect to the canonical `www` URL.

The build job has read-only repository permissions. Only the production deployment job receives `pages: write` and `id-token: write`; production deployments are serialized. No personal access token or cross-repository push is used. Monthly Dependabot PRs update the pinned Actions revisions. To update Hugo, change `.hugo-version`, run both validations, and review the browser preview before merging.

## Cloudflare builds and previews

Cloudflare Workers Builds also builds this repository, as the Worker `mihasoftware` described by `wrangler.jsonc`: static assets from `public/`, no Worker script, and `404.html` for unknown paths. GitHub Pages remains the production host until `www.mihasoftware.com` is moved to the Worker.

The Worker must use these settings under **Settings → Build**: build command `./scripts/build`, deploy command `npx wrangler deploy`, preview command `npx wrangler preview`, production branch `master`, and **Enable Preview Builds** on. Its name must match `name` in `wrangler.jsonc`, or builds fail. No build variables are needed; `scripts/build` reads the branch from `WORKERS_CI_BRANCH`.

Pushes to `master` get the production build and deploy it. Every other branch gets a Preview: a `test` build without analytics at its own `workers.dev` address, which Cloudflare posts on the pull request. Both builds run the validator, and a failure stops the deployment. Keep the `workers.dev` and Preview URLs behind Cloudflare Access (**Settings → Domains & Routes**) so previews stay private; they also send `X-Robots-Tag: noindex`.

Cloudflare redirects `.html` pages such as `/events/privacy.html` to the same path without the extension, where GitHub Pages serves both forms.

## Analytics

Cloudflare Web Analytics uses the public beacon identifier in `config.toml`. Events, Photo Resize and Beam landing, privacy, and support pages, and the Radio privacy and support pages, opt out with `noAnalytics: true`; their routes are recorded in `tests/legacy-contract.json`. Elsewhere it is included only in production builds and is always excluded by `hugo server`, including when the server uses the production environment. Use the test environment for static previews. Cloudflare automatic injection is disabled.

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

`content/events/` contains the English and Croatian landing, privacy and support pages. Keep `/events/`, `/events/index-hr.html`, `/events/privacy.html`, `/events/privacy-hr.html`, `/events/support.html` and `/events/support-hr.html` stable: the Android app uses these URLs. `themes/m1h4/layouts/events.html` is a short wrapper that passes the app's name, icon, contact address and URLs to the shared `partials/product-page.html`; screenshots and the icon are in `static/events/` and contain only fictional calendar data. Update the existing page when editing either translation, and preserve the same-page language links.

`content/apps/events.md` only feeds the home-page card (`build.render: never`); it no longer renders a page, and `/apps/events/` redirects to `/events/` through an alias on `content/events/_index.md`. The app is still preparing for release; add its verified Google Play link only when published. Support uses `support@mihasoftware.com`. Changes deploy through the normal pull-request and Actions workflow.

## Photo Resize release pages

The catalogue/English landing page is `content/apps/photo-resize.md`. Its Croatian translation, bilingual privacy policy, and support pages are in `content/photo-resize/`, with a non-rendered section index. Preserve `/apps/photo-resize/`, `/apps/photo-resize/hr/`, `/apps/photo-resize/privacy/`, `/apps/photo-resize/privacy/hr/`, `/apps/photo-resize/support/` and `/apps/photo-resize/support/hr/`; the Android app already links to the privacy URLs. These pages opt out of analytics. `themes/m1h4/layouts/photo-resize.html` is the matching wrapper around `partials/product-page.html`; actual paired app captures and the icon are in `static/photo-resize/`. The photograph is synthetic demo content.

The rebuilt app is in internal testing; add its public Google Play link only after availability is verified. Support remains `mihovilic@gmail.com`, matching the app. Original archived screenshots and their URLs remain intact.

## Beam release pages

The catalogue/English landing page is `content/apps/beam.md`. Its Croatian translation, bilingual privacy policy, and support pages are in `content/beam/`, with a non-rendered section index. Preserve `/apps/beam/`, `/apps/beam/hr/`, `/apps/beam/privacy/`, `/apps/beam/privacy/hr/`, `/apps/beam/support/` and `/apps/beam/support/hr/`; the App Store listing links to the privacy and support URLs. `themes/m1h4/layouts/beam.html` is the matching wrapper around `partials/product-page.html`; the icon and screenshots are in `static/beam/` and show only generated sample photos. Beam has one capture per language and no dark variant, so its pages and home-page card show the same image in both themes.

Beam 1.0 is being prepared for the App Store; add its App Store link only after the app is released. Support uses `support@mihasoftware.com`. These pages opt out of analytics with `noAnalytics: true`, and their routes are recorded in `tests/legacy-contract.json`.

## Radio release pages

`content/radio/` contains the English and Croatian privacy and support pages for the iOS app Radio: Croatian Stations, with a non-rendered section index. Preserve `/apps/radio/privacy/`, `/apps/radio/privacy/hr/`, `/apps/radio/support/` and `/apps/radio/support/hr/`: the iOS app and its App Store listing link to these URLs, which follow the Beam layout. `themes/m1h4/layouts/radio.html` wraps `partials/product-page.html` without a home URL or icon, so the pages link only to each other and their translations: there is no `/apps/radio/` landing page yet. Update the existing page when editing either translation, and preserve the same-page language links.

The app is not on the App Store yet, so there is no catalogue entry in `content/apps/`; add it, a landing page and the verified App Store link only after the app is released. Support uses `support@mihasoftware.com`. These pages opt out of analytics with `noAnalytics: true`, and their routes are recorded in `tests/legacy-contract.json`. Changes deploy through the normal pull-request and Actions workflow.
