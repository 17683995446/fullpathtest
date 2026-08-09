#!/usr/bin/env python3
"""
FullPathTest V4.0 Setup

极致轻量化全路径代码测试系统
"""

from setuptools import setup, find_packages

setup(
    name="fullpathtest",
    version="4.0.0",
    description="极致轻量化全路径代码测试系统",
    author="FullPathTest Team",
    packages=find_packages(include=['fullpathtest', 'fullpathtest.*']),
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=6.0.0',
        'fastapi>=0.100.0',
        'uvicorn>=0.23.0',
        'pydantic>=2.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'ruff>=0.0.280',
        ],
        'llm': [
            'openai>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'fullpathtest=fullpathtest.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.11',
)
