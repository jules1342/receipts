# Receipts: build, deploy, set up

## What it is
A phone web app (PWA) that photographs receipts, straightens and cleans the image so the paper can be thrown away, reads merchant, date, total, GST and category with Claude, and files each receipt under a category plus any number of tags (sections). Data lives on the phone in IndexedDB. Backup is a zip export, or Google Drive sync once the OAuth client is set up. Hosted on GitHub Pages at https://jules1342.github.io/receipts/.

## Files
- `receipts.html` is the only source file. Edit this.
- `_build/build.js` compiles it into `app/index.html` with React inlined. Never edit `app/index.html` by hand.
- `_build/icons.js` regenerates the two icons. `_build/serve.js` is a local test server.
- `app/` is the folder that deploys. It holds `index.html`, `manifest.webmanifest`, `sw.js`, two icons.

## Build
```bash
node "C:\Users\julia\⚡Claude Cowork\Projects\Personal\App Development\Receipts\_build\build.js"
```
Bump `BUILD_VERSION` in `receipts.html` before every ship. Settings, Diagnostics shows the running build string on the phone, so you can tell what is live. The build refuses to write if the compiled code fails to parse, if a CDN reference survives, or if an em dash is in the source.

## Test locally
```bash
node "C:\Users\julia\⚡Claude Cowork\Projects\Personal\App Development\Receipts\_build\serve.js" 5178
```
Then open http://localhost:5178 on this PC. The camera only works on https or localhost, so on the phone use the live site.

## Deploy: GitHub Pages
The project is a git repo pushed to `github.com/jules1342/receipts`. A GitHub Actions workflow (`.github/workflows/pages.yml`) publishes the `app/` folder on every push to `main`. The fixed address is:

    https://jules1342.github.io/receipts/

To ship a change: edit `receipts.html`, bump `BUILD_VERSION`, build, then commit and push. The design variant at `/receipts/design/` is regenerated with `python _build/make-design.py` then `node _build/build.js receipts-design.html app/design/index.html`. `_build/deploy.cmd` does the build, commit and push in one go. The site updates about a minute after the push; the phone picks it up on the next open (the service worker fetches the page network-first).

## Install on the phone
Open the site in Chrome on Android, tap the menu, Add to Home screen, Install. It opens full screen and works offline. Allow the camera when asked.

## Claude API key
Settings, paste the key from console.anthropic.com. It stays in the browser storage on the phone and calls go straight to Anthropic. Extraction uses `claude-opus-5` at low effort with a JSON schema, roughly one to three cents a receipt.

## Google Drive sync
Settings, **Connect Google Drive**. Google shows its account picker and asks to allow "See, edit, create and delete only the specific Google Drive files that you use with this app". That is the `drive.file` scope: the app can only reach files it created. After that, **Sync to Drive** uploads new images and a `receipts.json` to `My Drive/App Data/Receipts`, creating the folders if needed, and **Restore from Drive** (two taps) pulls anything missing on this phone, so a new phone can be set up from Drive. Sync is manual: tap it after a batch of receipts.

There is nothing to paste. The OAuth client ID is compiled into the app, and it is the same client the Macro app uses, because both apps live on `https://jules1342.github.io` and Google authorises by origin. The client ID is public by design; the origin restriction is what protects it. If the Google Auth Platform setup in the Macro README ever needs redoing, do it once and both apps follow.

Note: the Drive round trip has not been exercised from the build machine. It needs Julian's Google account and the live URL, so the first run on the phone is the real test.

## Export and import
Settings, Export everything (zip). On the phone the share sheet opens, so you can send the zip straight to Google Drive, email, or Files. The zip holds `receipts.json`, `receipts.csv`, and `images/`. Import accepts that zip, a bare `receipts.json`, or the `App Data/Receipts` folder downloaded from Google Drive as a zip, and merges by receipt id, keeping the newer copy. Images are named `date item merchant total pN [pageid].jpg`; the id in brackets is what import and restore match on, so the rest of the name can be anything.

## Migrating from Smart Receipts
`_build/smart-receipts-convert.py` turns a Smart Receipts "report with images" zip into a zip this app imports. Run it on the PC with your API key in the environment so every image is read by Claude, which pins the ambiguous matches (Fuel, Gas, Water) by invoice date and total, fills merchant and a concise item name, and prefers the invoice when the hand-typed row disagrees. Reads are cached in `reads.json`, so a re-run is free. The output folder gets `smart-receipts-import.zip` and a `report.md` listing anything matched by order only or left unmatched. Import the zip on the phone through Settings.

## Demo mode
Add `?demo` to either address (`/receipts/?demo` or `/receipts/design/?demo`) to open the app on a separate, throwaway database seeded with six sample receipts and generated receipt images. It never reads or writes the real data, and the service worker is not registered in demo mode.
