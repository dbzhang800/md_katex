import re
import unittest

PATTERN = re.compile(
    r'(?:(?<!\\)(?P<s1>(?:\\{2})+)(?=\$+)|(?<!\$)(?P<s2>`+)(?:.+?)(?<!`)(?P=s2)(?!`)|(?<!\\)\$(?P<s3>`+)(?P<formula>.+?)(?<!`)(?P=s3)(?!`)\$)'
)


class TestBacktickMathPattern(unittest.TestCase):
    r'''
    $` formula `$
    $`` formula ``$
    \$` not formula`$
    \$`` not formula ``$
    `` $`not a formula`$ ``
    '''

    def test_gitlab_math(self):
        text = "This is a math formula: $`E=mc^2`$ and this is $``a^2+b^2=c^2``$."
        matches = [m for m in PATTERN.finditer(text) if m.group("formula") is not None]
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0].group("formula"), "E=mc^2")  # Match $`...`$
        self.assertEqual(matches[1].group("formula"), "a^2+b^2=c^2")  # Match $``...``$

    def test_ignore_codeblock(self):
        text = "No formula in code block: `` $`E=mc^2`$ `` and `` $``a^2+b^2=c^2``$ ``."
        matches = [m for m in PATTERN.finditer(text) if m.group("formula") is not None]
        self.assertEqual(len(matches), 0)  # Formulas inside code blocks should be ignored

    def test_mixed_content(self):
        text = "Here is a formula $`E=mc^2`$ and no formula in code block `` $``a^2+b^2=c^2``$ ``."
        matches = [m for m in PATTERN.finditer(text) if m.group("formula") is not None]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group("formula"), "E=mc^2")  # Only match the formula, ignore the one inside the code block

    def test_escaped_dollar(self):
        text = r"This is not math: \$`E=mc^2`$ and \$``a^2+b^2=c^2``$."
        matches = [m for m in PATTERN.finditer(text) if m.group("formula") is not None]
        self.assertEqual(len(matches), 0)  # Escaped $ should not be matched

    def test_no_match(self):
        text = "This should not match: no dollar signs or backticks."
        matches = [m for m in PATTERN.finditer(text) if m.group("formula") is not None]
        self.assertEqual(len(matches), 0)

if __name__ == '__main__':
    unittest.main()