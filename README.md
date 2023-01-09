
# Packaging code on Azure DevOps

**How do you package code in a private pypi repository**

Large projects especially those with high collaborative teams often have code that is reusable across teams. Packaging this code makes the code’s functionality easily available, version-controlled and maintainable. Instead of the different teams reinventing the wheel, they can utilise the standardised implementation of the reusable functionality. 

Public package index repositories like PyPI and [conda-forge](https://conda-forge.org/) exist to host the popular packages like pandas, numpy etc but for certain projects, code has to be private. This blog explores how we package and publish reusable code in a private pypi repository.  We shall use Azure DevOps and Python package for this demonstration. *Similar foundational concepts apply to other git hosts and programming languages*

## Prerequisites

1. Azure DevOps Repository - see how to create one

## Steps
### 1. Configure Artifact Feed
Azure Artifacts feed enables you to store, manage and control how your packages are shared. The feed can be project or organizational wide accessible. 

1. Create a new feed in Azure Artifacts -in our case, the name is `reusabilityLab-packages`. Multiple settings exist including setting the visibility and scope of access.  See image below:

    ![](images/artifact-feed.jpeg)

For more information about Azure artifact feeds, follow this [link](https://learn.microsoft.com/en-us/azure/devops/artifacts/concepts/feeds?view=azure-devops)


### 2. Setup Folder structure

For easy maintainability, we structure our files and folders as below:

```
├── azure-pipelines.yml
├── pyproject.toml
├── src
│   ├── package
│   │   └── sub_package
│   │       ├── __init__.py 
│   │       └── module_1.py
```

Each of these files has a crucial purpose in successfully building and publishing your package:

- `azure-pipelines.yml` - cicd pipeline to incrementally build and deploy our pipeline
- `pyproject.toml` - configuration file with package building settings
- `__init__.py` - constructor that initializes a python package object
- `src/package/sub_package/module_1.py` - code to be packaged

### 3. Configure pyproject.toml
`pyproject.toml` provides a build tool agnostic package configuration that defines the build system requirements and settings utilised by pip to build our package.
Two main definitions are made in the `pyproject.toml` - `[build-system]` and `[project]`

- `build-system` specifies what backend build tools to use to build the package. For python, a couple of build systems are possible i.e. Hatchling, setuptools, Flit and PDM. For this use case, we use `setuptools` which is also the most commmonly used.

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools-git-versioning"]
build-backend = "setuptools.build_meta"
```

- `project` specifies the project metadata e.g. name of the package, versioning techniques, authors, python version required, url link to documentation and most importantly dependencies required for your package build

```toml
[build-system]
requires = ["setuptools>=61.0", "setuptools-git-versioning"]
build-backend = "setuptools.build_meta"

[tool.setuptools-git-versioning]
enabled = true

[project]
name = "my_custom_package"
dynamic = ["version"]
authors = [
  { name="Author_name", email="youremail@email.com" },
]
description = "Reusable code for our project"
readme = "README.md"
requires-python = ">=3.7"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies =[
    "numpy==1.24.1"
]

[project.urls]
"Wiki" = "https://your-documentation.com"
```
To cater for the incremental versions of your published package, we define the versioning to be dynamic and tied to git versioning - to be defined in `azure-pipeline.yaml`. This is defined by `dynamic = ["version"]` in the project metadata and `"setuptools-git-versioning"` in build-system configuration. An appropriate versioning strategy can be adopted - see semantic versioning [here](https://semver.org/)

More information about `pyproject.toml` can be found [here](https://pip.pypa.io/en/stable/reference/build-system/pyproject-toml/#)

### 4. Add your reusable python code
In `src/my_custom_package` we can add our logic that is reusable and eligible for packaging. Having quality code is advisable. In our case, a sub package called `simple_calculations` is defined with an `algebra.py` module. 

```python
import numpy as np


def addition(a, b):
    return np.sum([a, b])


def subtraction(a, b):
    return np.subtract([a, b])


def division(a, b):
    return np.divide(a, b)


def multiplication(a, b):
    return np.prod([a * b])

```

### 5. Set up CICD
To facilitate continuous integration of new functionality into our package and deployment into the artifact feed, we define an [Azure DevOps CI/CD pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/get-started/what-is-azure-pipelines?view=azure-devops) as below:

```yaml
trigger:
  tags:
    include:
      - v*.*

stages:
  - stage: onPush
    condition: startsWith(variables['Build.SourceBranch'], 'refs/tags/v')
    jobs:
      - job: onPushJob
        pool:
          vmImage: "ubuntu-20.04"

        steps:
          - task: UsePythonVersion@0
            displayName: "Use Python 3.9"
            inputs:
              versionSpec: "3.9"

          - script: |
              python3 -m pip install --upgrade pip
              pip install -r unit-requirements.txt
            displayName: "Install dependencies"

          - script: |
              python3 -m build --wheel
            displayName: "Build Package"

          - task: TwineAuthenticate@1
            displayName: Twine Authenticate
            inputs:
              artifactFeed: reusabilityLab/reusabilityLab-packages

          - script: |
              python -m twine upload -r reusabilityLab-packages --config-file $(PYPIRC_PATH) dist/*.whl
            displayName: "Upload to Azure Artifacts"

```

- This pipeline is triggerd by a git tag with naming convention - `v.*`. This tag is picked by the build system - `setuptools` defined in `pyproject.toml` and used as the version of the package i.e `package_namev.0.0.1`
- [Twine](https://twine.readthedocs.io/en/latest/) is a utility to securely authenticate the package and upload it to our private PyPI repository- Azure Artifacts over HTTPS via a verified connection


### 6. Build and Publish Package
With all the above steps ready, we can now build and publish our code as a reusable package. 

Assuming this code is already on your `main` branch in your git repository, we create and push a git tag to trigger our CI/CD pipeline which picks our reusable code, builds a package based on the configuration in `pyproject.toml`, authenticates and publishes it to our artifact feed using Twine.

```bash
git tag -a v0.0.1 -m "etl feature release"
git push origin --tags
```

The above will trigger the pipeline and you should have a new version of your package in your artifact feed.

Successful pipeline:

![](images/pipeline.png)

Published package:

![](images/package.png)

## How to access the published package
Our package is now available in Azure artifacts, we can install it anywhere via pip:
`pip install my_custom_package --upgrade --extra-index-url <insert-package-reader-token>@pkgs.dev.azure.com/<azure-devops-organisation>/PaceMak<azure-devops-project>/_packaging/<azure-artifacts-feed-name>/pypi/simple/`


Then we can import our package as 

```python
import my_custom_package.data_transformation.etl import cast_datatype, join_dataframes
```

## Resources

1. https://packaging.python.org/en/latest/tutorials/packaging-projects/
1. [https://towardsdatascience.com/install-custom-python-libraries-from-private-pypi-on-databricks-6a7669f6e6fd](https://towardsdatascience.com/install-custom-python-libraries-from-private-pypi-on-databricks-6a7669f6e6fd)
1. https://peps.python.org/pep-0621/