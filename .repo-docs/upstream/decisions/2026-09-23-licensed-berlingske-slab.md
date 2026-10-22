> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Licensed Berlingske Slab: self-hosted, never in git, deployed by Pages artifact

**Date:** 2026-09-23 · **Status:** accepted · **Ticket:** SC-320

> **Amended 2026-09-23 (SC-335): the fonts are now hosted by the ROOT site, not v2.**
> Scott wanted a future v3 to need no setup. So `SteelCompendium.github.io` runs the
> private-repo checkout, the Pages artifact deploy and the artifact deletion described
> below, and serves the files at `/fonts/licensed/berlingske-slab/`. v2 references that
> path; its CI has no secret and no fonts. v2 keeps `just fonts` only to fill a
> gitignored local-preview copy, which is the second `src` URL in each `@font-face`.
> Where this record says "v2 CI" for fetching or hosting, read "root site CI". The
> current rules live in the workspace `ARCHITECTURE.md` → "Licensed fonts".

## Context

The body face was Berlingske Slab (Playtype) until 2026-09-06, loaded from
`db.onlinewebfonts.com` — an unlicensed copy. It was swapped for Zilla Slab (OFL) for
legal reasons. On 2026-09-16 Scott bought a **Playtype Web-font Self-hosting license**
(certificate FLC-20260916-781E84-4CC1, order 20260916-03657) for six cuts:
Demibold, Bold, Extrabold and their italics, **Web: < 250,000 pageviews/month**. No
Regular/Book cut is licensed.

The EULA (playtype.com/eula, revised May 2025) sets the constraints. Verbatim:

- *"the fonts must be hosted by the Licensee, and the Font Software should be stored and
  served securely from the same devices and location as the other software and assets
  associated with the domain names … The use of third party font hosting services is
  strictly prohibited."*
- *"The Licensee must take necessary precautions to prevent downloads of the font by
  unlicensed third parties."* / *"use reasonable measures to prevent the access to
  unlicensed parties … by protecting and securing the font from download, extraction or
  editing."*
- Prohibited: *"making public or sharing the Font Software … in any way that makes it
  possible for others to download, extract or redistribute the Font Software … as a
  standalone file"*, and *"changing or modifying the fonts in any way."*
- *"PDF, EPUB, iOS and/or Android native applications are not permitted under the
  Web-font License"*.

The EULA has **no attribution requirement and no requirement to post the license.** The
certificate must NOT be published: it carries Scott's home address and email. It is kept
in the private fonts repo as proof of license.

The problem: `SteelCompendium/v2` is a **public** repo, and CI deployed with
`mkdocs gh-deploy`, which commits the built site to the public `gh-pages` branch. Either
path would put the font files in a public git repo, downloadable as standalone files —
exactly what the EULA forbids.

## Options considered

**Where the font files live**

- *Commit them to v2* — rejected: public repo, standalone download, plain violation.
- *Third-party CDN (jsDelivr etc.)* — rejected: "third party font hosting … strictly
  prohibited".
- *GPG-encrypted blob committed to v2, passphrase in a secret* — workable, but ships an
  opaque binary in a public repo and makes updates awkward.
- **Private repo `SteelCompendium/licensed-fonts`, read by CI through a read-only deploy
  key** — chosen. Nothing licensed is ever public in git; the certificate lives beside the
  fonts; local dev clones it with normal GitHub access.

**How the site deploys**

- *Keep `gh-deploy`* — rejected: publishes the fonts to the public `gh-pages` branch.
- **GitHub Pages artifact deploy (`upload-pages-artifact` + `deploy-pages`)** — chosen.
  The fonts are served by the site and exist nowhere else public. Requires the repo's
  Pages source set to "GitHub Actions".

## Decision

- **Files:** the six `.woff2` files, byte-for-byte as delivered (no subsetting — that is a
  modification). WOFF/EOT are not deployed; every supported browser takes WOFF2, and fewer
  copies means less exposure.
- **Location:** private repo `SteelCompendium/licensed-fonts`, `web/berlingske-slab/*.woff2`
  (+ `licenses/` for the certificate). The build copies those `.woff2` files, by name, into
  `docs/stylesheets/licensed-fonts/berlingske-slab/` — **gitignored** in v2, and inside `stylesheets/` so
  `steel-etl site`'s docs-dir cleanup (which keeps only protected dirs) doesn't delete it.
  `docs/fonts/` would be wiped on every `steel-etl site` run.
- **CI (`.github/workflows/ci.yml`):** refuses to deploy if any licensed font is tracked in
  git; checks out the private repo with `secrets.LICENSED_FONTS_DEPLOY_KEY`; fails (does
  not silently fall back) if the key is missing; copies only the `.woff2` files, by name;
  asserts the DBd file reached `site/`; deploys via Pages artifact; then **deletes the
  artifact** (`if: always()`). The artifact is the whole built site, fonts included, and
  any signed-in GitHub user can download a public repo's artifacts until they expire
  (minimum retention is one day). Deleting it right after `deploy-pages` shrinks that
  window to the minute or two between upload and delete.
- **Repo settings (one-time):** Pages source = "GitHub Actions" (`build_type=workflow`),
  and the `github-pages` environment's deployment-branch policy must allow `main` —
  under `gh-deploy` it only allowed `gh-pages`, so the first artifact deploy from `main`
  is rejected until `main` is added.
- **Local:** `just fonts` (v2 justfile) clones/pulls the private repo into
  `.licensed-fonts/` (gitignored) and installs the same `.woff2` files; `just serve` and
  `just build` run it best-effort.
- **CSS (`custom_font.css`):** one family, `"Berlingske Slab"`, six `@font-face` rules with
  weight *ranges*: Demibold = 100–500 (the site's normal weight, as it was before
  2026-09-06 when DBd was the only face loaded), Bold = 600, Extrabold = 700–900 (so
  `<strong>` reads clearly heavier than body prose). Ranges leave no gap for the browser to
  faux-bold.
- **Fallback:** `--md-text-font: "Berlingske Slab", "Zilla Slab"`. Forks, fresh clones and a
  broken local fetch render in Zilla Slab (identical to the 2026-09-06 → SC-320 look).
  Zilla stays a Settings option.
- **Settings:** the default font entry now stores nothing when chosen (previously it stored
  its own string, which is how readers got stranded on the retired `"BerlingskeSlab-DBd"`
  family and fell back to Georgia). On load, `settings-panel.js` drops any saved font that
  is no longer an option (the old Berlingske string, and retired Beaufort / Test Newzald /
  Forum heading picks); the `overrides/main.html` early-apply skips the old Berlingske
  string so those readers see no Georgia flash. Readers who explicitly saved Zilla Slab
  while it was the default keep Zilla — their saved string is still a valid option.

## Consequences

- The DSE Obsidian plugin can never bundle Berlingske (application use needs a separate
  license); it keeps its own serif stack.
- **Residual risk — hotlinking.** GitHub Pages sends `Access-Control-Allow-Origin: *` on
  every file and allows no header or referrer control, so another site could reference
  the font URLs. Closing that needs a proxy in front of Pages (e.g. Cloudflare with a
  referrer rule). Accepted for now as beyond what the host permits; revisit if Playtype
  asks.
- **Pageview cap.** The license covers < 250,000 pageviews/month. Material's instant
  navigation reports each in-site navigation as a pageview in GA (property
  `G-PMF9SHHXNY`). Exceeding it requires upgrading the license tier with Playtype.
- **Key rotation:** the deploy key is read-only on the fonts repo only. Rotate by
  generating a new pair, replacing the deploy key and the `LICENSED_FONTS_DEPLOY_KEY`
  secret.
- **Every site depends on the root host's path (SC-335).** v2 and the root site load
  the six files from `/fonts/licensed/berlingske-slab/`, served by the root site. That is
  the same domain and host, so it is still self-hosting with one copy. Moving or renaming
  them there breaks every site's body font.
- The old `gh-pages` branch is no longer served once the Pages source is "GitHub Actions";
  it never contained licensed files.

## Outcome

(Fill in after the first deploy.)
