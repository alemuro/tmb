import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tmb",
    version="0.0.4",
    author="alemuro",
    author_email="hola@aleixmurtra.com",
    description="Library that interacts with TMB API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alemuro/tmb",
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['requests'],
    keywords='tmb transports metropolitans barcelona tren metro bus',
)