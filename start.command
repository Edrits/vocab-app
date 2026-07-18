#!/bin/bash
# Double-click this file in Finder to open your vocab app.
# It starts a small local server and opens the app in your browser.
cd "$(dirname "$0")"
echo "Starting 网语 · Netizen Vocab …"
open "http://localhost:4173"
echo "App opening in your browser. Keep this window open while studying."
echo "Close this window (or press Ctrl-C) when you're done."
python3 -m http.server 4173
