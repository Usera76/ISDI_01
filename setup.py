from setuptools import setup, find_packages

setup(
    name="financegpt2",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'python-dotenv>=1.0.0',
        'pandas>=2.0.0',
        'numpy>=1.0.0',
        'scikit-learn>=1.0.0',
        'pytest>=7.0.0',
        'fpdf>=1.7.2'
    ]
)