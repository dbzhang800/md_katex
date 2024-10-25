## About md_katex

![Build Status](https://github.com/dbzhang800/md_katex/actions/workflows/python-package.yml/badge.svg)

> **md_katex** is a KaTeX plugin originally designed for personal blog use with pelican. It aims to render formulas using the KaTeX JavaScript file in the browser, instead of performing offline conversion.

### Features

- **Browser-side Rendering**: Unlike other plugins, this one does not perform offline conversion. Formula rendering is handled by the KaTeX JavaScript file in the browser, simplifying the publishing process.
- **Supports Multiple Formula Delimiter Styles**:
  - **GitLab Style**: Uses `` $` `` and `` `$ `` as inline formula delimiters, and `~~~math` code blocks for block-level formulas.
  - **Brackets Style**: Uses `\(` and `\)` as inline formula delimiters, and `\[ ... \]` as block-level formula delimiters.
  
- **Unified Output Format**: After Markdown is converted to HTML, all formulas will use the Brackets style delimiters and will be rendered via JavaScript.

### Usage

In your python script :

~~~python
# Function to generate the HTML
def generate_html_with_katex(markdown_content: str) -> str:
    # Register the custom extension
    md = Markdown(extensions=[MdKatexExtension()])

    # Convert the Markdown content to HTML
    html_body = md.convert(markdown_content)

    # Define the full HTML structure, including KaTeX CSS and JS
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>KaTeX Math Example</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous"
    onload="renderMathInElement(document.body);"></script>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    return full_html

if __name__ == '__main__':
    # Example Markdown content with KaTeX formulas

    from markdown import Markdown

    markdown_content = r"""
# Md_KaTeX Math Example

Gitlab style inline formula: $`E=mc^2`$

Brackets style inline formula: \(E=mc^2\)

Gitlab style block formula:

```math
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
```

Brackets style block formula:

\[
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\]

"""

    # Generate the HTML content
    html_content = generate_html_with_katex(markdown_content)

    # Write the HTML to a file
    with open("katex_example.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML file 'katex_example.html' has been generated.")
~~~

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

