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

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor

logger = logging.getLogger(__name__)

# gitlab style math block:  ```math, ~~~math, etc.
CODE_FENCE_RE       = re.compile(r"^(\s*)(`{3,}|~{3,})")
CODE_FENCE_MATH_START_RE = re.compile(r"^(\s*)(`{3,}|~{3,})math")

# code span starts with "`" or "``", note that the following is valid "`` ` ``"
CODE_SPAN_DELIM_RE = re.compile(r"`{1,2}") 
INLINE_MATH_START_DELIM_RE = re.compile(r"\\\(") 
BLOCK_MATH_START_DELIM_RE = re.compile(r"\\\[") 
DELIM_START_END_MAP = {r"\(": r"\)",
             r"\[": r"\]",
             r"$`": r"`$",
             r"$``": r"``$",
             r"$": r"$",
             r"$$": r"$$",
             r"\f$": r"$\f",
             r"\f[": r"]\f"}


ESCAPE_BACKSLASHES_RE = re.compile(r"(\\)([(){}\[\]\*\!`+\-_#])")

def escape_backslashes(text: str) -> str:
    '''Make sure the backslash in math is not removed by the markdown parser.

    https://daringfireball.net/projects/markdown/syntax#backslash
    '''
    return ESCAPE_BACKSLASHES_RE.sub(r"\\\\\2", text)

class InlineMathItem(typing.NamedTuple):
    ''' Represents an inline math item in the text.

    start: pos of the total math including begining delim
    end: the pos after the ending delim
    inline_math: text without the delims
    '''
    start      : int
    end        : int
    inline_math: str

def iter_inline_katex(line: str) -> typing.Iterable[InlineMathItem]:
    '''Find the position of inline formula, which

    * starts with \\( and ends with \\)
    * starts with $` and ends with `$
    * starts with $`` and ends with ``$
    '''
    
    pos = 0
    while True:
        code_span_delim_match = CODE_SPAN_DELIM_RE.search(line, pos)
        if code_span_delim_match is None:
            # outside/after code span
            math_pos = pos
            while True:
                inline_math_match = INLINE_MATH_START_DELIM_RE.search(line, math_pos)
                if inline_math_match is None:
                    break
                # ok inline math found outside code span
                math_pos = inline_math_match.end()
                math_start = inline_math_match.start()
                math_delim = inline_math_match.group()
                try:
                    math_end = line.index(DELIM_START_END_MAP[math_delim], math_pos)
                except ValueError:
                    math_pos = math_start + len(math_delim)
                    continue
                inline_math = line[math_start + len(math_delim) : math_end]
                math_pos = math_end + len(math_delim)
                yield InlineMathItem(math_start, math_pos, inline_math)
            break

        # outside/before code span
        search_end_pos = code_span_delim_match.start()
        math_pos = pos
        while math_pos <= search_end_pos:
            inline_math_match = INLINE_MATH_START_DELIM_RE.search(line, math_pos)
            if inline_math_match is None:
                break
            # ok inline math found outside code span
            math_pos = inline_math_match.end()
            if math_pos > search_end_pos:
                break
            math_start = inline_math_match.start()
            math_delim = inline_math_match.group()
            try:
                math_end = line.index(DELIM_START_END_MAP[math_delim], math_pos)
            except ValueError:
                math_pos = math_start + len(math_delim)
                continue
            inline_math = line[math_start + len(math_delim) : math_end]
            math_pos = math_end + len(math_delim)
            yield InlineMathItem(math_start, math_pos, inline_math)

        # we are in code span now
        # try to find it's a gitlab formula or not
        pos   = code_span_delim_match.end()
        start = code_span_delim_match.start()
        delim = code_span_delim_match.group()

        try:
            end = line.index(delim, start + len(delim)) + (len(delim) - 1)
        except ValueError:
            # avoid infinite loop
            pos = start + len(delim)
            continue

        pos = end

        if line[start - 1] == "$" and line[end + 1] == "$":
            # if code span wrapped with $ $, which means $` `$ or $`` ``$
            inline_math = line[start + 1 : end - len(delim) + 1]
            pos         = end + len(delim)

            yield InlineMathItem(start - 1, end + 2, inline_math)

class MdKatexExtension(Extension):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def extendMarkdown(self, md) -> None:
        md.preprocessors.register(DebaoKatexPreprocessor(md, self), name='debao_katex', priority=50)
        md.registerExtension(self)

class DebaoKatexPreprocessor(Preprocessor):
    def __init__(self, md, ext: MdKatexExtension) -> None:
        super().__init__(md)
        self.ext: MdKatexExtension = ext

    def _enclose_fence_block_math(self, block_math_lines: list[str]) -> str:
        indent_len  = len(block_math_lines[0]) - len(block_math_lines[0].lstrip())
        indent_text = block_math_lines[0][:indent_len]
        block_math = "\n".join(line[indent_len:] for line in block_math_lines[1:-1]).rstrip()

        return '<div class="math-block">\\[\n' + block_math + '\n\\]</div>'

    def _enclose_non_fence_block_math(self, block_math_lines: list[str]) -> str:
        block_math = "\n".join(line for line in block_math_lines[1:-1]).rstrip()
        return '<div class="math-block">\\[\n' + block_math + '\n\\]</div>'

    def _enclose_inline_math(self, inline_math: str) -> str:
        return escape_backslashes('<span class="math-inline">\\(' + inline_math + '\\)</span>')

    def _iter_lines(self, lines: list[str]) -> typing.Iterable[str]:
        is_in_code_fence_math     = False
        is_in_code_fence          = False
        is_in_math_block          = False
        expected_code_fence_close = "```"
        expected_math_block_close = "\\]"

        # Try to find display formula
        block_math_lines: list[str] = []

        for line in lines:
            if is_in_code_fence:
                # we should dealwith any lines in normal fence
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
            elif is_in_math_block:
                block_math_lines.append(line)
                if expected_math_block_close in line:
                    is_in_math_block = False
                    ## Ok now, display formula found
                    enclosed_block_math       = self._enclose_non_fence_block_math(block_math_lines)
                    del block_math_lines[:]
                    yield enclosed_block_math
            else:
                # try to find the fence code or math block start flag
                code_fence_math_match = CODE_FENCE_MATH_START_RE.match(line)
                if code_fence_math_match:
                    is_in_code_fence_math     = True
                    prefix               = code_fence_math_match.group(1)
                    expected_code_fence_close = prefix + code_fence_math_match.group(2)
                    block_math_lines.append(line)
                    continue

                code_fence_match      = CODE_FENCE_RE.match(line)
                if code_fence_match:
                    is_in_code_fence          = True
                    prefix               = code_fence_match.group(1)
                    expected_code_fence_close = prefix + code_fence_match.group(2)
                    yield line
                    continue

                # for block math formula not in code fence
                block_math_match = BLOCK_MATH_START_DELIM_RE.match(line)
                if block_math_match:
                    is_in_math_block = True
                    math_start = block_math_match.start()
                    math_delim = block_math_match.group()
                    expected_code_fence_close = DELIM_START_END_MAP[math_delim]
                    block_math_lines.append(line)
                    continue

                ## Ok now, we don't live in any block, try to found inline formula
                inline_codes = list(iter_inline_katex(line))
                for code in reversed(inline_codes):
                    # iterate in reverse, so that start and end indexes remain valid
                    enclosed_inline_math = self._enclose_inline_math(code.inline_math)
                    line       = line[: code.start] + enclosed_inline_math + line[code.end :]

                yield line

        # unclosed block
        if block_math_lines:
            for line in block_math_lines:
                yield line

    def run(self, lines: list[str]) -> list[str]:
        return list(self._iter_lines(lines))

# Register the extension
def makeExtension(**kwargs):
    return MdKatexExtension(**kwargs)

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

$E=mc^2$

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
