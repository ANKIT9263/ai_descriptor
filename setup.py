from setuptools import setup, find_packages

# Load requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ai_image_descriptor",  # change this to your project name
    version="0.1.0",
    author="Ankit Singh",
    author_email="aksingh9263@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # or your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
