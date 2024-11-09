# -----------------------------------------------------------------------------
# MIT License
# 
# Copyright (c) 2024 hello@debao.me
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

import re
import typing
import logging

from xml.etree import ElementTree as etree

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.blockprocessors import BlockProcessor
from markdown.postprocessors import Postprocessor
from markdown.util import AtomicString

logger = logging.getLogger(__name__)

# Regular expressions to capture inline formulas wrapped by $` and `$ or $`` and ``$
INLINE_GITLAB_MATH_PATTERN = r'(?:(?<!\\)(?P<s1>(?:\\{2})+)(?=\$+)|(?<!\$)(?P<s2>`+)(?:.+?)(?<!`)(?P=s2)(?!`)|(?<!\\)\$(?P<s3>`+)(?P<formula>.+?)(?<!`)(?P=s3)(?!`)\$)'
# Regular expression to capture inline formulas wrapped by \( and \)
INLINE_BRACKETS_MATH_PATTERN = r'\\\((.+?)\\\)'

class InlineGitlabMathProcessor(InlineProcessor):
    r'''
    $` formula `$
    $`` formula ``$
    \$` not formula`$
    \$`` not formula ``$
    `` $`not a formula`$ ``
    '''
    def handleMatch(self, m, data):
        math_content = m.group("formula")  # Get the inline formula content
        if math_content is not None:
            el = etree.Element('span')
            el.set('class', 'math inline')
            el.text = AtomicString(f'{math_content}')  # Wrap content with KaTeX inline formula delimiters
            return el, m.start(0), m.end(0)
        else:
            return None, None, None
        
class InlineBracketsMathProcessor(InlineProcessor):
    r'''
    \( formula \)
    '''
    def handleMatch(self, m, data):
        math_content = m.group(1)  # Get the inline formula content
        el = etree.Element('span')
        el.set('class', 'math inline')
        el.text = AtomicString(f'{math_content}')  # Wrap content with KaTeX inline formula delimiters
        return el, m.start(0), m.end(0)

class BlockGitlabMathProcessor(Preprocessor):
    r'''
    GitLab-style math blocks with matching backticks or tildes
    
    ```math
    ```
    or

    ~~~math
    ~~~

    but not in other fenced blocks such as:

    ~~~
    ```math
    ```
    ~~~

    '''
    BLOCK_CODE_FENCE_RE       = re.compile(r"^(\s*)(`{3,}|~{3,})")
    BLOCK_CODE_FENCE_MATH_START_RE = re.compile(r"^(\s*)(`{3,}|~{3,})math")

    def __init__(self, md) -> None:
        super().__init__(md)

    def _enclose_fence_block_math(self, block_math_lines: list[str]) -> str:
        indent_len  = len(block_math_lines[0]) - len(block_math_lines[0].lstrip())
        indent_text = block_math_lines[0][:indent_len]
        block_math = "\n".join(line[indent_len:] for line in block_math_lines[1:-1]).rstrip()

        return '<div class="math display">\n' + block_math + '\n</div>'

    def _enclose_non_fence_block_math(self, block_math_lines: list[str]) -> str:
        block_math = "\n".join(line for line in block_math_lines[1:-1]).rstrip()
        return '<div class="math display">\n' + block_math + '\n</div>'

    def _iter_lines(self, lines: list[str]) -> typing.Iterable[str]:
        is_in_code_fence_math     = False
        is_in_code_fence          = False
        expected_code_fence_close = "```"

        # Try to find display formula
        block_math_lines: list[str] = []

        for line in lines:
            if is_in_code_fence:
                # We should deal with any lines in normal fence
                yield line
                if line.rstrip() == expected_code_fence_close:
                    is_in_code_fence = False
            elif is_in_code_fence_math:
                block_math_lines.append(line)
                if line.rstrip() == expected_code_fence_close:
                    is_in_code_fence_math = False
                    ## Ok now, display formula found
                    enclosed_block_math       = self._enclose_fence_block_math(block_math_lines)
                    del block_math_lines[:]
                    yield enclosed_block_math
            else:
                # Try to find the fence code or math block start flag
                code_fence_math_match = self.BLOCK_CODE_FENCE_MATH_START_RE.match(line)
                if code_fence_math_match:
                    is_in_code_fence_math     = True
                    prefix               = code_fence_math_match.group(1)
                    expected_code_fence_close = prefix + code_fence_math_match.group(2)
                    block_math_lines.append(line)
                    continue

                code_fence_match      = self.BLOCK_CODE_FENCE_RE.match(line)
                if code_fence_match:
                    is_in_code_fence          = True
                    prefix               = code_fence_match.group(1)
                    expected_code_fence_close = prefix + code_fence_match.group(2)
                    yield line
                    continue

                ## Ok now, we don't live in any block now
                yield line

        # Unclosed block
        if block_math_lines:
            for line in block_math_lines:
                yield line

    def run(self, lines: list[str]) -> list[str]:
        return list(self._iter_lines(lines))

# The map that defines the delimiter pairs

class BlockBracketsMathProcessor(BlockProcessor):
    """
    BlockProcessor to capture LaTeX math blocks with various start and end delimiters.
    """
    RE_MATH_START = re.compile(r'^\s*(\\\[|\$\$)\s*')  # Matches the start of \[ or $$
    RE_MATH_END1 = re.compile(r"\s*\\\]\s*")  # Corrected: matches \]
    RE_MATH_END2 = re.compile(r"\s*\$\$\s*")  # Matches $$

    # Match start delimiters to their corresponding end delimiters
    FORMULA_DELIM_PAIR_MAP = {
        r"\[": RE_MATH_END1,  # The key now matches the captured start delimiter
        r"$$": RE_MATH_END2,
    }

    def __init__(self, parser):
        super().__init__(parser)
        self.start_delim = r'\[' 

    def test(self, parent, block):
        """
        Test if the block starts with a known formula delimiter.
        """
        m = self.RE_MATH_START.match(block)
        if m:
            self.start_delim = m.group(1)
            return True
        return False

    def run(self, parent, blocks):
        r"""
        Process the block and convert it to a unified \[...\] format.
        """
        original_block = blocks[0]

        blocks[0] =  re.sub(self.RE_MATH_START, '', blocks[0])
        math_content = []
        for block_num, block in enumerate(blocks):
            if re.search(self.FORMULA_DELIM_PAIR_MAP[self.start_delim], block):
                blocks[block_num] = re.sub(self.FORMULA_DELIM_PAIR_MAP[self.start_delim], '', block)
                math_content.append(blocks[block_num])
                # Create a <div> element to wrap the math content
                div = etree.SubElement(parent, 'div')
                div.set('class', 'math display')
                div.text = AtomicString('\n' + '\n'.join(math_content) + '\n')

                # Remove used blocks
                for i in range(0, block_num + 1):
                    blocks.pop(0)
                return True  # or could have had no return statement
            else:
                math_content.append(block)

        blocks[0] = original_block
        return False

class MdKatexExtension(Extension):
    def extendMarkdown(self, md):
        # Note: markdown.inlinepatterns.BacktickInlineProcessor priority is 190
        md.inlinePatterns.register(InlineGitlabMathProcessor(INLINE_GITLAB_MATH_PATTERN, md), 'inline_gitlab_math', 195)
        md.inlinePatterns.register(InlineBracketsMathProcessor(INLINE_BRACKETS_MATH_PATTERN, md), 'inline_brackets_math', 185)
        md.preprocessors.register(BlockGitlabMathProcessor(md), "block_gitlab_math", 100)
        md.parser.blockprocessors.register(BlockBracketsMathProcessor(md.parser), "block_brackets_math", 30)

# Register the extension
def makeExtension(**kwargs):
    return MdKatexExtension(**kwargs)

# Function to generate the HTML
def generate_html_with_katex(markdown_content: str) -> str:
    # Initialize the Markdown converter with the custom KaTeX extension
    md = Markdown(extensions=[MdKatexExtension(), "extra"])

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

    # Generate the HTML content with KaTeX formulas rendered
    html_content = generate_html_with_katex(markdown_content)

    # Write the generated HTML to a file
    with open("katex_example.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML file 'katex_example.html' has been generated.")
