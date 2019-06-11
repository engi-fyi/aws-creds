import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-creds",
    version="0.9.0",
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
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: System :: Systems Administration"
    ],
    entry_points = {
        'console_scripts': [
            'aws-creds=creds.main:main'
        ]
    },
    install_requires = [
        "boto3",
        "click"
    ],
    py_modules = [
        "creds.cli",
        "creds.cred"
    ]
)
