#!/usr/bin/env python3
"""
Setup script for Universal Intelligent Communicator (UnIC)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="universal-intelligent-communicator",
    version="1.0.0",
    author="UnIC Team",
    author_email="contact@unic-project.com",
    description="A comprehensive AI-powered knowledge management and conversational system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Universal-Intelligent-Communicator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "full": [
            "torch>=1.12.0",
            "transformers>=4.21.0",
            "spacy>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "unic=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.html"],
    },
    keywords=[
        "ai",
        "nlp",
        "chatbot",
        "knowledge-management",
        "conversational-ai",
        "semantic-search",
        "text-to-speech",
        "speech-recognition",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/Universal-Intelligent-Communicator/issues",
        "Source": "https://github.com/yourusername/Universal-Intelligent-Communicator",
        "Documentation": "https://github.com/yourusername/Universal-Intelligent-Communicator#readme",
    },
) 