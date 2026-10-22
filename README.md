# Personal website — as2710-rit.github.io

Static portfolio site. HTML + CSS, no build step, no JS framework.

## Structure

```
website/
├── index.html          # all content
├── css/style.css       # all styling
├── assets/
│   └── resume.pdf      # PUT YOUR RESUME HERE (the download button points at it)
└── .nojekyll           # tells GitHub Pages to serve files as-is
```

## Customize (find & replace)

| Placeholder | Replace with |
|---|---|
| `Abdul` | Your full name (nav, hero, footer) |
| `you@example.com` | Real email (2 spots in `#contact`) |
| `linkedin.com/in/your-handle` | Your LinkedIn URL |
| About paragraphs | Your own bio |
| `assets/resume.pdf` | Your actual resume file |

## Deploy to GitHub Pages

```bash
cd website
git init
git add -A
git commit -m "portfolio site"
git branch -M main
git remote add origin https://github.com/as2710-rit/as2710-rit.github.io.git
git push -u origin main
```

Site goes live at **https://as2710-rit.github.io** within about a minute.

## Preview locally

```bash
python -m http.server 8000
# open http://localhost:8000
```
