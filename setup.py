from setuptools import setup, find_packages

setup(
    name="modern-business-software",
    version="1.0.0",
    description="Modern Business Management System for Vegetable Wholesale Operations",
    author="Devin AI",
    packages=find_packages(),
    install_requires=[
        'dbf==0.99.3',
        'Pillow==10.0.0',
        'reportlab==4.0.4',
    ],
    entry_points={
        'console_scripts': [
            'business-app=main:main',
        ],
    },
    python_requires='>=3.8',
)
