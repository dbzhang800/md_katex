import unittest
from markdown import Markdown
from md_katex.extension import MdKatexExtension

class TestMdKatexExtension(unittest.TestCase):
    
    def setUp(self):
        self.md = Markdown(extensions=['extra', MdKatexExtension()])

    def test_inline_math(self):
        """inline formula test"""
        test_cases = [
            {
                "name": "gitlab",
                "input": "This is an inline formula: $`E=mc^2`$.",
                "expected": r'<p>This is an inline formula: <span class="math-inline">\(E=mc^2\)</span>.</p>'
            },
            {
                "name": "brackets",
                "input": "Another formula: \\(a^2 + b^2 = c^2\\).",
                "expected": r'<p>Another formula: <span class="math-inline">\(a^2 + b^2 = c^2\)</span>.</p>'
            },
            {
                "name": "mixed",
                "input": "Mixed: `1` ``2`` $`3`$ \\(4\\) \\(5\\) `6`.",
                "expected": r'<p>Mixed: <code>1</code> <code>2</code> <span class="math-inline">\(3\)</span> <span class="math-inline">\(4\)</span> <span class="math-inline">\(5\)</span> <code>6</code>.</p>'
            }
        ]
        for case in test_cases:
            with self.subTest(case=case["name"]):
                output = self.md.convert(case['input'])
                self.assertEqual(output, case['expected'])

    def test_block_math(self):
        """block math test"""
        test_cases = [
            {
                "name": "gitlab",
                "input": r"""
```math
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
```
""",
                "expected": '<div class="math-block">\\[\n\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}\n\\]</div>'
            },
            {
                "name": "brackets",
                "input": r"""
\[
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\]
""",
                "expected": '<div class="math-block">\\[\n\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}\n\\]</div>'
            },
                        {
                "name": "github",
                "input": r"""
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
""",
                "expected": '<div class="math-block">\\[\n\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}\n\\]</div>'
            }
        ]
        for case in test_cases:
            with self.subTest(case=case["name"]):
                output = self.md.convert(case['input'])
                self.assertEqual(case['expected'].strip(), output.strip())

    def test_normal_backslashescape_text(self):
        """make sure normal text works as expected, markdown supports backslash escapes for some chars"""

        escaped_input_text = r'\\\\ \\{\\}\\*\\!\\`\\+\\-\\_\\#'
        input_text = r'\\ \{\}\*\!\`\+\-\_\#'
        expected_text = r'\ {}*!`+-_#'

        # the following works when this extension disabled
        #escaped_input_text += r'\\(\\)\\[\\]'
        #input_text += r'\(\)\[\]'
        #expected_text += r'()[]'

        test_cases = [
            {
                "name": "normal",
                "input": input_text,
                "expected": '<p>' + expected_text + '</p>', 
            },
            {
                "name": "in-span",
                "input": '<span>' + input_text + '</span>',
                "expected": '<p><span>' + expected_text + '</span></p>'
            },
            {
                "name": "in-div",
                "input": '<div>' + input_text + '</div>',
                "expected": '<div>' + input_text + '</div>' #doesn't changed by markdown
            },
            {
                "name": "normal_escaped",
                "input": escaped_input_text,
                "expected": '<p>' + input_text + '</p>', 
            },
            {
                "name": "in-span_escaped",
                "input": '<span>' + escaped_input_text + '</span>',
                "expected": '<p><span>' + input_text + '</span></p>'
            },
            {
                "name": "in-div_escaped",
                "input": '<div>' + escaped_input_text + '</div>',
                "expected": '<div>' + escaped_input_text + '</div>' #doesn't changed by markdown
            }
        ]
        for case in test_cases:
            with self.subTest(case=case['name']):
                output = self.md.convert(case['input'])
                self.assertEqual(case['expected'], output)

    def test_normal_fenced_code_block(self):
        """make sure that normal fenced code block not be processed"""
        test_cases = [
            {
                "name": "normal ```math in fence code",
                "input": r"""
~~~
```math
```
~~~
""",
                "expected":"<pre><code>```math\n```\n</code></pre>"
            },
            {
                "name": "normal brackets in fence code",
                "input": r"""
```
\[
\]
```
""",
                "expected":"<pre><code>\\[\n\\]\n</code></pre>"
            },
            {
                "name": "normal dolars in fence code",
                "input": r"""
~~~
$$
$$
~~~
""",
                "expected":"<pre><code>$$\n$$\n</code></pre>"
            },
            {
                "name": "python code not affected by our extension",
                "input": r"""
```python
def hello():
    print("Hello, world!")
```
""",
                "expected": (
            '<pre><code class="language-python">def hello():\n'
            '    print(&quot;Hello, world!&quot;)\n'
            '</code></pre>')
            }
        ]
        for case in test_cases:
            with self.subTest(case=case["name"]):
                output = self.md.convert(case['input'])
                self.assertEqual(case['expected'].strip(), output.strip())

if __name__ == '__main__':
    unittest.main()
