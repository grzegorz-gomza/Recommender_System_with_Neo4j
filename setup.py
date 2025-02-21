from setuptools import find_packages, setup

# Open Readme file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Open requirements.txt file
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

__version__ = "1.0"

REPO_NAME = "Recommender_System_with_Neo4j"
AUTHOR_USER_NAME = "Grzegorz Gomza"
SRC_REPO = ""
AUTHOR_EMAIL = "gomza.datascience@gmail.com"

setup(
    name="recommender_system_for_netflix",
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="Simple Recommender System for Netflix",
    long_description=long_description,
    long_description_content="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements[:-1],
)
