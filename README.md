## About md_katex

![Build Status](https://github.com/dbzhang800/md_katex/actions/workflows/python-package.yml/badge.svg)

**md_katex** is a KaTeX plugin initially developed for use in personal blogs with **Pelican**. It focuses on rendering mathematical formulas directly in the browser using the KaTeX JavaScript library, rather than performing offline conversions.

### Features

- **Client-Side Rendering**: Unlike other plugins, **md_katex** does not convert formulas offline. Instead, the KaTeX JavaScript file in the browser handles the rendering, making the publishing process simpler and more efficient.
- **Supports Multiple Formula Delimiter Styles**:
  - **GitLab Style**: Use `` $` `` and `` `$ `` for inline formulas, and `~~~math` code blocks for block-level formulas.
  - **Brackets Style**: Use `\(` and `\)` for inline formulas, and `\[` and `\]` for block-level formulas.
  - **GitHub Style**: Use `$$` as both the opening and closing delimiters for block-level formulas.

- **Unified Output Format**: After Markdown is converted to HTML, all formulas are standardized to use the Brackets style delimiters and are rendered via JavaScript.

### Installation

First, ensure that you have the `python-markdown` library installed. Then, you can install this plugin using the following command:

```bash
pip install md_katex
```

The generated HTML will include KaTeX formulas, and you will need to load KaTeX JavaScript on the frontend to complete the rendering.

To ensure proper rendering, include the KaTeX script via a `<script>` tag in your HTML page. For example, using a CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous"
onload="renderMathInElement(document.body);"></script>
```

## References

* https://github.com/mbarkhau/markdown-katex
* https://github.com/martenlienen/pelican-katex
* https://github.com/oruelle/md_mermaid
* https://github.com/goessner/markdown-it-texmath
* https://docs.gitlab.com/ee/user/markdown.html#math
* https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions
* https://katex.org/docs/autorender

