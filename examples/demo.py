from markdown import Markdown

# Example Markdown content with KaTeX formulas
markdown_content = r"""
# Md_KaTeX Math Example

GitLab-style inline formula `` $`E=mc^2`$ `` : $`E=mc^2`$

Brackets-style inline formula `` \(E=mc^2\) ``: \(E=mc^2\)

### GitLab-style Block Formula

Fenced block with GitLab-style math:

~~~
```math
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
```
~~~

**Rendered as:**

```math
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
```

### Brackets-style Block Formula

Formula wrapped with LaTeX-style brackets:

```
\[
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\]
```

**Rendered as:**

\[
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\]

### GitHub-style Block Formula

Formula wrapped with GitHub-style double dollar signs:

```
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

**Rendered as:**

$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
"""

katex_content = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>
    <script>document.addEventListener("DOMContentLoaded", function () {
 var mathElements = document.getElementsByClassName("math");
 var macros = [];
 for (var i = 0; i < mathElements.length; i++) {
  var texText = mathElements[i].firstChild;
  if (mathElements[i].tagName == "SPAN" || mathElements[i].tagName === "DIV") {
   katex.render(texText.data, mathElements[i], {
    displayMode: mathElements[i].classList.contains('display'),
    throwOnError: false,
    macros: macros,
    fleqn: false
   });
}}});
    </script>
"""

# Function to generate the HTML
def generate_html_with_katex(markdown_content: str) -> str:
    # Initialize the Markdown converter with the custom KaTeX extension
    #from md_katex.extension import MdKatexExtension
    #md = Markdown(extensions=[MdKatexExtension(), "extra"])
    md = Markdown(extensions=['md_katex', "extra"])

    # Convert the provided Markdown content into HTML
    html_body = md.convert(markdown_content)

    # Define the full HTML structure, including KaTeX CSS and JavaScript for rendering
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KaTeX Math Example</title>
    {katex_content}
</head>
<body>
    {html_body}
</body>
</html>
 """
    return full_html


# Generate the HTML content with KaTeX formulas rendered
html_content = generate_html_with_katex(markdown_content)

# Write the generated HTML to a file
with open("katex_example.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML file 'katex_example.html' has been generated.")

