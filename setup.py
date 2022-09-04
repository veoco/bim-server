import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bim-server",
    version="0.1.0",
    author="Veoco",
    author_email="one@nomox.cn",
    description="Server for bench.im",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/veoco/bim-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)