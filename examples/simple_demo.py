markdown_content = """
Inline Formulas

- GitLab-style inline formula: $`E = mc^2`$
- Brackets-style inline formula: \\( E = mc^2 \\)

GitLab-style block formula:

~~~math
E = mc^2
~~~

Brackets-style block formula:

\\[
E = mc^2
\\]

GitHub-style block formula:

$$
E = mc^2
$$
"""

import markdown

html_content = markdown.markdown(
    markdown_content,
    extensions=['extra', 'md_katex']
)

print(html_content)
