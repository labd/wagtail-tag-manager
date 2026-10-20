from setuptools import find_packages, setup


install_requires = [
    "wagtail>=7.0",
    "wagtail_modeladmin>=2.3.0",
]

scanner_require = [
    "selenium>=3.141.0,<3.142.0",
]

tests_require = [
    "factory_boy",
    "pytest-cov",
    "pytest-django",
    "pytest-randomly",
    "pytest",
    "wagtail_factories",
]

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name="wagtail-tag-manager",
    version="1.6.0",
    description="A Wagtail add-on for managing tags.",
    author="Jasper Berghoef",
    author_email="j.berghoef@me.com",
    maintainer="Lab Digital",
    url="https://github.com/labd/wagtail-tag-manager",
    project_urls={
        "Source": "https://github.com/labd/wagtail-tag-manager",
        "Upstream": "https://github.com/jberghoef/wagtail-tag-manager",
    },
    python_requires=">=3.10",
    install_requires=install_requires,
    extras_require={"scanner": scanner_require, "test": tests_require},
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="BSD 3-Clause",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Framework :: Django",
        "Framework :: Django :: 5.2",
        "Framework :: Django :: 6.0",
        "Framework :: Django :: 6.1",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 7",
        "Framework :: Wagtail :: 8",
    ],
)
