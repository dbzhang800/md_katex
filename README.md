## About md_katex

> **md_katex** is a KaTeX plugin designed for personal use with debaoblog. It aims to render formulas using the KaTeX JavaScript file in the browser, instead of performing offline conversion.

### Features

- **Browser-side Rendering**: Unlike other plugins, this one does not perform offline conversion. Formula rendering is handled by the KaTeX JavaScript file in the browser, simplifying the publishing process.
- **Supports Multiple Formula Delimiter Styles**:
  - **GitLab Style**: Uses `` $` `` and `` `$ `` as inline formula delimiters, and `~~~math` code blocks for block-level formulas.
  - **Brackets Style**: Uses `\(` and `\)` as inline formula delimiters, and `\[ ... \]` as block-level formula delimiters.
  
- **Unified Output Format**: After Markdown is converted to HTML, all formulas will use the Brackets style delimiters and will be rendered via JavaScript.

### Installation

First, ensure that you have the `python-markdown` library installed. Then, you can install this plugin using the following command:

```bash
pip install md_katex
```

The generated HTML will include KaTeX formulas, and you will need to load KaTeX JavaScript on the frontend to complete the rendering.

## References

* https://github.com/mbarkhau/markdown-katex
* https://github.com/martenlienen/pelican-katex
* https://github.com/oruelle/md_mermaid
* https://github.com/goessner/markdown-it-texmath
* https://docs.gitlab.com/ee/user/markdown.html#math
* https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions
* https://katex.org/docs/autorender

