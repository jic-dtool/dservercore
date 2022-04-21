#!/bin/bash -x
ROOTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

python3 -m venv "${ROOTDIR}/venv"

echo "Activate venv in ${ROOTDIR}/venv"
source "${ROOTDIR}/venv/bin/activate"

pip install --upgrade pip

pip install setuptools_scm

pip install -r "${ROOTDIR}/devel/requirements.txt"

pip install -e "${ROOTDIR}"
