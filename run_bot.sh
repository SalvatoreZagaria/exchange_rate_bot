#!/usr/bin/env bash

setup_venv()
{
    ${PYTHON_INTERPRETER} -m venv $BOT_WORKSPACE/venv --without-pip
    source $BOT_WORKSPACE/venv/${PIP_PATH}/activate
    curl https://bootstrap.pypa.io/get-pip.py | $PYTHON_INTERPRETER
    pip install -r $BOT_WORKSPACE/requirements.txt
}

setup_folders()
{
if [[ ! -d $BOT_WORKSPACE/venv ]]; then
    echo "Virtual environment not found. Setting up a new venv."
    setup_venv
else
    source $BOT_WORKSPACE/venv/${PIP_PATH}/activate
fi
}

main()
{
export BOT_WORKSPACE=$PWD

setup_folders

python bot.py
}

os_check()
{
case "$(uname -s)" in

	Linux)
		PYTHON_INTERPRETER=python3
		PIP_PATH=bin
		;;
	CYGWIN*|MINGW32*|MSYS*)
		PYTHON_INTERPRETER=python
		PIP_PATH=Scripts
		;;
esac
}

os_check
main
#EOF