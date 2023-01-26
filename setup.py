from setuptools import setup

setup(
    name="snippet-generator",
    version="0.0.1",
    install_requires=[],
    extras_require={
    },
    entry_points={
        "console_scripts": [
            "snipgen = snippet_generator.main:main",
        ]
    }
)
