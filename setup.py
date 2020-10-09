import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hpcconfig",
    version="2.0.4",
    author="ccnhpc",
    author_email="dsp-cspito-ccn-hpc@edf.fr",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://forge.hpc.edf.fr/cgit/github/edf-hpc/hpc-config.git/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts = [ "hpcconfig/hpc-config-push", "hpcconfig/hpc-config-apply" ],
    install_requires=[
    'boto',
    'urllib3',
    'pyyaml',
    'paramiko',
    ],
    python_requires='>=3.4',
)
