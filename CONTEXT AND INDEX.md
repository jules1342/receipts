# CONTEXT AND INDEX: Receipts
> _Location: Projects / Personal / App Development / Receipts_

## Context
Receipts is a phone app Julian built to replace paper receipts. He photographs a receipt (several pages if needed), the app finds the edges, straightens and cleans the image, Claude reads merchant, date, total, GST and category, and the receipt files under one category plus any tags (sections such as Warranty or Reimbursable). Data lives in IndexedDB on the phone. Backup is a zip export, or Google Drive sync once he creates the OAuth client. It is built the same way as Macro: one JSX source file, a local build that inlines React, a deploy folder for Netlify. Read `README.md` before touching anything.

## Index
- **DECISIONS.md**: between-session memory. Task state lives in the root `CURRENT STATUS.md`.
- **README.md**: primary source. Build, local test, Netlify deploy with a fixed URL, phone install, the Google Drive setup steps, export and import.
- **receipts.html**: primary source. The whole app, and the only file to edit.
- **_build/**: primary source. `build.js` compiles the source into `app/index.html`. `icons.js` draws the icons. `serve.js` is a local test server. `deploy.cmd` builds then deploys. `vendor/` holds React, `node_modules/` holds Babel, both copied from Macro so the build runs offline.
- **app/**: deliverable. The built app ready to deploy. Never edit by hand.
