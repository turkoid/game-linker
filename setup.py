import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="game-linker",
    version="0.1.0",
    author="John Ross",
    author_email="jlross42@gmail.com",
    description="My Game Linker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/turkoid/game-linker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
)
