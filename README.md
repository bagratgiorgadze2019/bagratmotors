# bagratmotors

Umbrella marketing site for **Bagrat Motors** — evacuator (towing), mobile vulcanization and mini-excavator services in Tbilisi, 24/7. Source for https://bagratmotors.ge

## Stack
- Static HTML, hosted on GitHub Pages (custom domain via `CNAME`).
- **Tailwind CSS v4** compiled with the CLI: `src/input.css` → `assets/styles.css`.
- Trilingual: Georgian (default, root), English (`/en/`), Russian (`/ru/`).

## Build
```bash
npm install
npm run build     # one-off, minified
npm run watch     # rebuild on change
```

## Structure
- `index.html`, `en/index.html`, `ru/index.html` — homepages
- `services/{evakuatori,vulkanizacia,mini-ekskavatori}/` — Georgian service pages
- `en/services/{towing,vulcanization,mini-excavator}/` — English
- `ru/services/{evakuator,vulkanizaciya,mini-ekskavator}/` — Russian
- `robots.txt`, `sitemap.xml`, `llms.txt` — SEO/AEO
- `assets/` — compiled CSS, images, favicon

## Contact
Phone: 514 90 80 90 · Email: info@bagratmotors.ge
