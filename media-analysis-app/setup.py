from setuptools import setup, find_packages

setup(
    name="media-analysis-app",
    version="0.1.0",
    author="Vicky Kosambiya",
    author_email="Vicky.Kosambiya@course5i.com",
    description="A media analysis application for processing videos and news articles.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit>=1.24.0",
        "requests>=2.31.0",
        "lxml>=4.9.0",
        "deep-translator>=1.11.0",
        "pydub>=0.25.1",
        "python-dotenv>=1.0.0",
        "langdetect>=1.0.9",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pytube>=15.0.0",
        "moviepy>=1.0.3",
    ],
    entry_points={
        "console_scripts": [
            "media-analysis=core.app:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
)