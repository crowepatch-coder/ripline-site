# Ripline support site

The two pages Apple requires on the App Store listing: a privacy policy URL
and a support URL. Hosted free on GitHub Pages.

## How it's built

`Docs/PRIVACY_POLICY.md` and `Docs/SUPPORT.md` in the app repo stay the
source of truth. `build.py` converts them into `privacy.html` and
`support.html` using the template and `style.css` here, so the published
pages can't drift from what the repo says.

After editing either Markdown file:

```sh
python3 Site/build.py
```

`site.json` holds the support address and the "last updated" date. The build
refuses to run if the address is still a placeholder — publishing a support
page with no working contact fails App Review.

`index.html` is written by hand; it's the only page not generated.

To check the pages before publishing, serve the folder (opening the files
directly works, but the stylesheet won't load):

```sh
python3 -m http.server 8765 --directory Site
```

## Publishing

This folder is pushed to its own **public** repository, separate from the app
source, which stays private. One command, from the app repo root:

```sh
git subtree push --prefix=Site site main
```

`site` is a git remote pointing at the public site repository. Set it once:

```sh
git remote add site git@github.com:<user>/ripline-site.git
```

Then in that repository: **Settings → Pages → Build and deployment → Deploy
from a branch → main / (root)**. The pages appear at
`https://<user>.github.io/ripline-site/` within a minute or two.

## What goes in the App Store listing

| Field | URL |
|---|---|
| Privacy Policy URL | `https://<user>.github.io/ripline-site/privacy.html` |
| Support URL | `https://<user>.github.io/ripline-site/support.html` |
| Marketing URL (optional) | `https://<user>.github.io/ripline-site/` |

## Before submission

- The support address in `site.json` must be a mailbox someone actually
  reads. Apple checks that the support URL works; buyers use the address.
- The privacy policy describes the app as it ships. When photo capture lands
  (spec §8), the camera and photo sections have to come back into
  `Docs/PRIVACY_POLICY.md` before that build goes out.
