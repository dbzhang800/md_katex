from setuptools import setup, find_packages

setup(
    name="md-katex",
    version="0.2",
    description="A Markdown extension for rendering LaTeX math using Katex",
    author="Debao Zhang",
    author_email="hello@debao.me",
    packages=find_packages(),
    install_requires=[
        "markdown>=3.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
