import sys
from typing import List

# 动态导入处理
try:
    from setuptools import setup, find_packages
except ImportError:
    # 回退方案
    sys.stderr.write("Warning: setuptools not found, using minimal setup\n")
    from distutils.core import setup  # type: ignore


    def find_packages():  # type: ignore
        return []


# 读取项目版本
def get_version() -> str:
    with open("analyzer.py", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'')
    return "0.1.0"


# 读取依赖项
def get_requirements() -> List[str]:
    try:
        with open("requirements.txt", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


setup(
    # 基础元数据
    name="simple_analyzer",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight static code analyzer for Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simple-analyzer",

    # 包配置
    packages=find_packages(),
    py_modules=["analyzer"],
    python_requires=">=3.8",
    install_requires=get_requirements(),

    # 分类信息
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Quality Assurance",
    ],

    # 入口点
    entry_points={
        "console_scripts": [
            "analyzer=analyzer:main",
        ],
    },

    # 额外文件
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md"],
    },

    # 项目标签
    keywords="static-analysis python code-quality",
    license="MIT",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/simple-analyzer/issues",
        "Source": "https://github.com/yourusername/simple-analyzer",
    },
)