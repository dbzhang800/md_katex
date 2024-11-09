from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
long_description = (HERE / "README.md").read_text()

setup(
    name="md-katex",
    version="0.3.0",
    description="A Markdown extension for rendering LaTeX math using Katex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Debao Zhang",
    author_email="hello@debao.me",
    url="https://github.com/dbzhang800/md_katex",
    packages=find_packages(),
    install_requires=[
        "markdown>=3.0"
    ],
    entry_points={
        'markdown.extensions': [
            'md_katex = md_katex.extension:MdKatexExtension',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
