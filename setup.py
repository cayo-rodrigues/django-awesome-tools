from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="django-utils",
    version="1.0.0.dev",
    description="Useful functions and classes for Django and Django Rest Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cayo-rodrigues/django-utils",
    author="Cayo Rodrigues",
    author_email="cayo.rodrigues1914@gmail.com",
    license="MIT",
    keywords="django utils serializers generic views viewsets mixins email login model manager custom action shortcut error",
    packages=find_packages(include=["django_utils", "django_utils.*"]),
    install_requires=["djangorestframework"],
    python_requires=">=3.8",
)
