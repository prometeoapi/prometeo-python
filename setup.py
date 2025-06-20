import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setuptools.setup(
    name="prometeo",
    version="2.0.5",
    author="Prometeo",
    author_email="dev@prometeoapi.com",
    description="Python client library for Prometeo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prometeoapi/prometeo-python",
    packages=setuptools.find_packages(exclude="tests"),
    package_data={"README": ["README.md"]},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
