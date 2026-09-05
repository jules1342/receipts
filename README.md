# Receipts: build, deploy, set up

## What it is
A phone web app (PWA) that photographs receipts, straightens and cleans the image so the paper can be thrown away, reads merchant, date, total, GST and category with Claude, and files each receipt under a category plus any number of tags (sections). Data lives on the phone in IndexedDB. Backup is a zip export, or Google Drive sync once the OAuth client is set up.

## Files
- `receipts.html` is the only source file. Edit this.
- `_build/build.js` compiles it into `app/index.html` with React inlined. Never edit `app/index.html` by hand.
- `_build/icons.js` regenerates the two icons. `_build/serve.js` is a local test server.
- `app/` is the folder that deploys. It holds `index.html`, `manifest.webmanifest`, `sw.js`, `netlify.toml`, two icons.

## Build
```bash
node "C:\Users\julia\⚡Claude Cowork\Projects\Personal\App Development\Receipts\_build\build.js"
```
Bump `BUILD_VERSION` in `receipts.html` before every ship. Settings, Diagnostics shows the running build string on the phone, so you can tell what is live. The build refuses to write if the compiled code fails to parse, if a CDN reference survives, or if an em dash is in the source.

## Test locally
```bash
node "C:\Users\julia\⚡Claude Cowork\Projects\Personal\App Development\Receipts\_build\serve.js" 5178
```
Then open http://localhost:5178. The camera only works on https or localhost, so on the phone you need the deployed site.

## Deploy to Netlify with a fixed URL
Netlify Drop mints a new URL on every drop, which breaks the installed icon and would break Google sign-in. Use the CLI once so the site keeps one address.

1. Install the CLI once: `npm install -g netlify-cli`
2. In a terminal, from the `app/` folder: `netlify login` (opens the browser once).
3. First deploy: `netlify deploy --prod --dir .` and choose "Create & configure a new site". Pick a site name, for example `julian-receipts`. The URL is then `https://julian-receipts.netlify.app` forever.
4. Every later deploy, from `app/`: `netlify deploy --prod --dir .`

Or use `_build/deploy.cmd`, which runs the build and then that deploy command.

If you would rather deploy from a Git repo, push this folder to GitHub, connect the repo in the Netlify dashboard with publish directory `app`, and every push deploys. Same fixed URL. Either path works.

## Install on the phone
Open the site in Chrome on Android, tap the menu, Add to Home screen, Install. It opens full screen and works offline. Allow the camera when asked.

## Claude API key
Settings, paste the key from console.anthropic.com. It stays in the browser storage on the phone and calls go straight to Anthropic. Extraction uses `claude-opus-5` at low effort with a JSON schema, roughly one to three cents a receipt.

## Google Drive sync (optional, one-time setup, about 10 minutes)
The app needs an OAuth client ID that is allowed to run from your site's address.

1. Go to https://console.cloud.google.com and sign in with the Google account whose Drive you want to use.
2. Create a project. Name it anything, for example "Receipts app".
3. Left menu, APIs & Services, Library. Search "Google Drive API" and click Enable.
4. APIs & Services, OAuth consent screen. Choose External, fill in the app name "Receipts", your email as support email and developer contact, save. Under Audience add your own Gmail address as a test user. You do not need to publish the app; test users can sign in indefinitely.
5. APIs & Services, Credentials, Create credentials, OAuth client ID. Application type Web application. Under Authorised JavaScript origins add your Netlify URL exactly, for example `https://julian-receipts.netlify.app`. No path, no trailing slash. Leave redirect URIs empty. Create.
6. Copy the Client ID (ends in `.apps.googleusercontent.com`). In the app, Settings, Google Drive sync, paste it and Save.
7. Tap Sync to Drive. Google asks you to sign in and allow "See, edit, create and delete only the specific Google Drive files that you use with this app". That scope means the app can only touch files it created.

The app creates a folder called "Receipts App" in your Drive with every receipt image and a `receipts.json`. Sync uploads what is new. Restore from Drive pulls anything missing on this device, so a new phone can be set up from Drive. Sync is manual: tap it after a batch of receipts.

Note: the Drive code has been written but could not be exercised from the build machine, because it needs your Google account and the live site URL. Expect to report back on the first try.

## Export and import
Settings, Export everything (zip). On the phone the share sheet opens, so you can send the zip straight to Google Drive, email, or Files. The zip holds `receipts.json`, `receipts.csv`, and `images/`. Import accepts that zip or a bare `receipts.json` and merges by receipt id, keeping the newer copy.
