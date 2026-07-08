# Deploy: The Decision Loop → jonathangu.com/coframebrain

One folder, one file, zero build steps.

1. In your `jonathangu.github.io` repo (the GitHub Pages repo behind jonathangu.com),
   copy the `coframebrain/` folder to the repo root:

       cp -r coframebrain /path/to/jonathangu.github.io/
       cd /path/to/jonathangu.github.io
       git add coframebrain && git commit -m "Add coframebrain" && git push

2. Wait ~1 minute for Pages to redeploy. Done:

       https://jonathangu.com/coframebrain/

Password: joncoframebook

Notes
- The page is fully self-contained (fonts, figures, CSS, JS all inline) — no other
  assets to upload, nothing to configure.
- Content is AES-256-GCM encrypted (PBKDF2, 600k iterations) and decrypted in the
  reader's browser. The plaintext never sits on GitHub; without the password the
  file is ciphertext. Fine for a public Pages repo.
- Works great on phones — send the URL + password straight to the CEO/CTO.
- To rotate the password later, just ask me to rebuild with a new one.

Tip for next time: add `jonathangu/jonathangu.github.io` to the Claude GitHub app's
allowed repos and I can push updates like this directly.
