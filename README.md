<<<<<<< HEAD
# nebula_python_wrapper
=======
# Nebula Python Wrapper

A Python wrapper for analyzing Nebula simulation results.

## Project Structure
```
nebula_python_wrapper/
├── data/               # Data files (e.g., output.det, pmma.mat)
├── docs/               # Documentation files
├── nebula_python_wrapper/  # Python wrapper source code
│   ├── __init__.py
│   ├── nebula_wrapper.py
│   ├── sem-analysis.py
│   └── sem-pri.py
├── scripts/            # Utility scripts
│   └── nebula_gui.py
├── README.md
├── requirements.txt
└── setup.py
```

## Features
- Reels analysis
- SEM analysis

## Usage
To run the SEM analysis script:
```bash
python nebula_python_wrapper/sem-analysis.py
```

## Installation
```bash
pip install -e .
```

## Usage
```bash
nebula-analysis <input_file>
nebula-sem-analysis <input_file>
```
>>>>>>> 025c552 (添加项目文档：包括CHANGELOG.md、PROJECT_DOCUMENTATION.md、README.md、TECHNICAL_DOCUMENTATION.md和USER_GUIDE.md)
