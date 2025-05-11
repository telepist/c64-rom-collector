from setuptools import setup, find_packages

setup(
    name="c64collector",
    version="1.0.0",    packages=find_packages(where="src"),
    package_dir={"": "src"},
    description="Commodore 64 ROM Collection Manager",
    author="Original Author",
    python_requires=">=3.6",
    install_requires=[
        "tqdm",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "unittest-xml-reporting>=3.2.0",
            "coverage>=7.0.0",
        ]
    },    entry_points={
        "console_scripts": [
            "c64collector=c64collector.cli:main",
        ],
    },
)
