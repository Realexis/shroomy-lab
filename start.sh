#!/bin/bash
# Start the Shroomy LAB copy on this Mac: http://localhost:5190/
# Lab label in the header, visit counter off. Stop it with Ctrl+C.
set -e
cd "$(dirname "$0")/site/web"
[ -d node_modules ] || npm ci
VITE_PREVIEW_LABEL=Lab VITE_COUNTER=off npx vite --port 5190 --strictPort --host 127.0.0.1 --open
