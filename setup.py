import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-creds",
    version="0.2.1",
    author="Adam Hammond",
    author_email="adam@hammo.io",
    description="Switch between AWS Credential profiles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HammoTime/aws-creds",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    entry_points = {
        'console_scripts': [
            'aws-creds=bin.run:cli'
        ]
    },
    install_requires = [
        "boto3",
        "click"
    ]
)
