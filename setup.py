import os.path
import re
import setuptools

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(THIS_DIR, "README.md")) as file:
    README = file.read()
with open(os.path.join(THIS_DIR, "autojinja", "__init__.py")) as file:
    VERSION = re.search(r"__version__ = \"(.*?)\"", file.read()).group(1)

setuptools.setup(
    name="autojinja",
    version=VERSION,
    description="Content generation with Jinja templates in between comments",
    author="Florian Popek",
    author_email="florian.popek@gmail.com",
    url="https://github.com/ldflo/autojinja",
    license="BSD",
    long_description_content_type="text/markdown",
    long_description=README,
    platforms="OS Independent",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
    ],
    packages=["autojinja"],
    install_requires=["jinja2"],
    entry_points={"console_scripts": ["autojinja=autojinja.__main__:entry_point"]},
)
