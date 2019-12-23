"""icingagen package configuration."""
from setuptools import setup

setup(
    name="backup",
    version="0.1",
    description="SOWN backup",
    url="https://github.com/sown/backup",
    author="SOWN",
    packages=["backup"],
    zip_safe=False,
    install_requires=[
        "pynetbox",
        "pyzfs",
    ],
    extras_require={
        "dev": [
            "flake8",
            "flake8-commas",
            "flake8-comprehensions",
            "flake8-debugger",
            "flake8-mutable",
            "flake8-todo",
            "flake8-docstrings",
            "flake8-isort",
        ],
    },
    entry_points={
        "console_scripts": [
            "backup=backup.__main__:main",
        ],
    },
)
