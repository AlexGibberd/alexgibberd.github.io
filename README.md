# 28 Cromwell Road, Lancaster — property site

A single-page static site for the sale of 28 Cromwell Road, Lancaster, LA1 5BD.
No build step, no dependencies — plain HTML, CSS and JavaScript.

Live at <https://alexgibberd.github.io/>

## Files

```
index.html          the whole page
css/style.css       all styling (colour tokens are at the top, in :root)
js/main.js          sticky nav, mobile menu, photo lightbox, scroll reveals
images/             web-optimised photos (-800 for the grid, -1600 for the lightbox)
                    plus floorplan.svg
tools/              make_floorplan.py — regenerates images/floorplan.svg
favicon.svg
.nojekyll           tells GitHub Pages to serve the files as-is
```

## Publishing to GitHub Pages

The site is served from the root of a repository named exactly
`alexgibberd.github.io` (that name is what puts it at `alexgibberd.github.io`
rather than a sub-path).

1. Create a **public** repo on GitHub called `alexgibberd.github.io`. Do not add
   a README, .gitignore or licence — start it empty.
2. From this folder:

   ```bash
   git init
   git add -A
   git commit -m "28 Cromwell Road property site"
   git branch -M main
   git remote add origin https://github.com/alexgibberd/alexgibberd.github.io.git
   git push -u origin main
   ```

3. On GitHub go to **Settings → Pages**, and under *Build and deployment* set
   **Source: Deploy from a branch**, **Branch: `main`**, **Folder: `/ (root)`**.
4. Wait a minute or two, then open <https://alexgibberd.github.io/>.

To update anything later, edit the files, then:

```bash
git add -A && git commit -m "Update details" && git push
```

## Previewing locally

```bash
python -m http.server 8000
```

Then open <http://localhost:8000>. (Opening `index.html` directly by
double-clicking works too, but a local server matches how Pages will serve it.)

## Editing the content

Everything the seller is likely to change is marked with an `<!-- EDIT ... -->`
comment in `index.html`:

- **Price** — in the hero (`.hero__price`) and in the page `<title>` / meta description.
- **Overview text** — the `#overview` section.
- **Property details table** — `#accommodation`. Two rows still say
  *To be confirmed* (tenure and council tax band). Fill these in or delete the
  rows before sharing the link.
- **Energy panel** — `#improvements`. Every figure comes from the EPC issued on
  4 September 2025 (certificate `0330-2594-9110-2105-6555`), which the page
  links to twice. If a newer certificate is issued, update the panel, the
  *EPC rating* row, the facts strip and the meta description together.
- **Improvements list** — `#improvements`. Confirm each item is accurate.
- **Email address** — appears in the `#contact` section and the footer.

### Adding photographs

Put a wide version (about 1600px) and a grid version (about 800px) in
`images/`, then copy an existing `figure` block in the `#gallery` section and
point `src` at the small file and `data-full` at the large one. The lightbox
picks up any element with a `data-full` attribute automatically, so no
JavaScript changes are needed.

To regenerate the whole image set from the originals, see the resize script
noted in the commit history, or use any image tool — the site only expects the
`-800` / `-1600` filename convention.

## Notes

- The map is an OpenStreetMap embed centred on 54.042369, -2.806996. To move
  the pin, edit the `bbox` and `marker` values in the `<iframe>` in the
  `#location` section.
- The floorplan is a redrawn SVG (`images/floorplan.svg`), not the original
  agent image — so it stays sharp at any zoom, carries no watermark and is 16 KB.
  Layout, fixtures and room labels follow the original plan, but the geometry is
  rebuilt at one consistent scale (the original is not drawn to scale). Edit
  `tools/make_floorplan.py` and re-run it to change anything:

  ```bash
  python tools/make_floorplan.py
  ```
- The footer carries a short non-contractual disclaimer, which is worth keeping
  on a private sale listing.
