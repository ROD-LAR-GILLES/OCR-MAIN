from setuptools import setup, find_packages

setup(
    name="ocr-main",
    version="0.1.0",
    description="Sistema OCR con Clean Architecture",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pytesseract>=0.3.8",
        "pdf2image>=1.16.0",
        "opencv-python>=4.5.3",
        "pdfplumber>=0.7.0",
        "numpy>=1.21.0",
        "Pillow>=8.3.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.1",
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ocr-process=interfaces.cli.menu:main",
        ],
    },
)