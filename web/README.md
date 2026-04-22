# Web demo

A browser-based frontend that runs the full `satsolver` package client-side
via [Pyodide](https://pyodide.org/) (CPython compiled to WebAssembly). No
backend, no install — users open the page, paste a DIMACS formula or load
one of the preset examples, and the solver runs entirely in their browser.

## Local preview

```
tar --exclude='__pycache__' -cf web/satsolver.tar satsolver
cd web && python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy

`.github/workflows/pages.yml` publishes this directory (plus a tarball of
`satsolver/`) to GitHub Pages on every push to `main`. Enable Pages in the
repository settings with source "GitHub Actions" — no other configuration
is required.

## How it works

1. The page pulls Pyodide (`pyodide.js` + the wasm runtime) from the jsDelivr CDN on load.
2. It fetches `satsolver.tar` (a tarball of the `satsolver/` package produced by the deploy workflow) and extracts it into Pyodide's virtual filesystem.
3. User input is parsed by `satsolver.dimacs.parse`, solved by `satsolver.Solver`, and the model / stats are rendered back to the page.

The solver itself is unchanged — the browser runs the exact same Python
code as the CLI.
