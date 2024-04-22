# Backend

## User Installation

```bash
pip install -e .
```

## Dev Installation

Conda is mainly use to isolate the environment and dictate the python version. For the dependencies, use pip.

```bash
conda env create -f environment.yml
conda activate yourapp-backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
# make sure you're in backend/
pip install -e .
```

## Run scripts in `yourapp/scripts/`

```bash
python -m yourapp.scripts.<script_name>
```

### Optional steps (if not using PyCharm)

Make sure the current directory is the same as this file's.

Unix-like system:

```bash
echo "PYTHONPATH=\$PYTHONPATH:$(pwd)" >> .env
```

*vscode tip:* Make sure to always open vscode with this directory as root in order to work on this codebase. Otherwise you will experience import issues. In settings, `git.openRepositoryInParentFolders` set to `always`.

## How to install more dependencies

```bash
pip install <package>
```

If your dependency is required by the code in `yourapp/`: 

```bash
# update requirements.txt
echo "<package>" >> requirements.txt
```

Otherwise:

```bash
# update requirements-dev.txt
echo "<package>" >> requirements-dev.txt
```