import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tslearn",
    version="0.0.1",
    author="Marcel Zoll",
    author_email="marcel.zoll.physics@gmail.com",
    description="learning and processing features from time-series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mzoll/tslearn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Propretary :: NIPropretary",
        "Operating System :: OS Independent",
    ],
)