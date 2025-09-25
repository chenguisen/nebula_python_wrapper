from setuptools import setup, find_packages

setup(
    name='nebula_python_wrapper',
    version='1.0.0',
    description='Python wrapper for Nebula simulation analysis',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
    ],
    entry_points={
        'console_scripts': [
            'nebula-sem-analysis=nebula_python_wrapper.sem_analysis:main',
        ],
    },
)