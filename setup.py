"""Setup script for the Advanced Search Agent."""

from setuptools import setup, find_packages

setup(
    name="advanced-search-agent",
    version="1.0.0",
    description="Professional candidate search and evaluation system for Mercor",
    author="Bhaumik Tandan",
    author_email="bhaumik.tandan@gmail.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "turbopuffer>=1.0.0",
        "openai>=1.0.0",
        "requests>=2.28.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "openpyxl>=3.0.10",
        "python-dotenv>=1.0.0",
        "tqdm>=4.64.0",
        "pymongo>=4.0.0",
        "certifi>=2022.0.0",
    ],
    extras_require={
        "dev": [
            "mypy>=1.0.0",
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "search-agent=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 