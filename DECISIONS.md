# DECISIONS: Receipts
> _Location: Projects / Personal / App Development / Receipts_

## Broader task
Build and maintain Receipts, Julian's personal receipt tracker that replaces the paper. Modelled loosely on Smart Receipts, but only the parts he uses.

## Decisions
- **Working preferences.** No em dashes, ever (the build refuses them). Australian English. AUD and day-first dates. Concise, with pushback.
- **2026-09-05, phone web app (PWA), not native.** Same pattern as Macro and Movement Tracker: one source file, local build, static hosting.
- **2026-09-05, one category plus any number of tags.** Categories are the main bucket (Electronics, Bills, plus any he adds; Warranty is a tag, not a category). Sections are tags, so a receipt can sit in both Warranty and Reimbursable. Julian chose this over a folder model.
- **2026-09-05, Claude reads the receipt, not on-device OCR.** `claude-opus-5`, effort low, JSON schema output. The model marks each of merchant, date, total and category high or low confidence. Anything low or missing is highlighted in the form and the receipt carries a "Check" chip until he saves it with the field edited.
- **2026-09-05, the crop is auto-detected and then hand-adjustable.** Corners drag. On release, a corner snaps to the strongest detected straight line nearby, so a nudged edge lands on the real paper edge. "Full" resets to the whole frame.
- **2026-09-05, enhanced scans are the default.** Divide-by-local-mean greyscale, so paper goes white and faint ink stays readable. Colour is one tap away per page, and the default is a setting.
- **2026-09-05, camera is in-page getUserMedia, never the system camera.** Carried over from Macro: Android kills the backgrounded tab when the camera app opens. Lens switcher remembers his choice.
- **2026-09-05, Drive sync waits for the OAuth client.** Julian chose to build everything else first. The sync and restore code is in place behind a Settings field and is untested until he creates the client ID and the site has a fixed URL.
- **2026-09-05, GitHub Pages is the host, not Netlify.** Julian's call: a fixed URL (`https://jules1342.github.io/receipts/`) and a deploy Claude can run end to end with a push. Google only allows Drive sign-in from a registered origin, so the URL must never change.
- **Export is a zip with the images and a CSV**, shared through the phone's share sheet so it can go straight to Drive without any Google setup. Import merges by id and keeps the newer copy.
