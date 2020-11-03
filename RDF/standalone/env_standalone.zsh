#!/bin/zsh

# Please setup python 2.7 and ROOT into your environment first

CWD=$PWD
THIS_SCRIPT=${(%):-%N}
if [[ ${THIS_SCRIPT[0,1]} == "/" ]]; then #Double [[ ]] to change equality testing rule
    FULLPATH=${THIS_SCRIPT}
else
    FULLPATH=$PWD/${THIS_SCRIPT};
fi
cd ${FULLPATH/%env_standalone.zsh/}/..

if [ -f standalone/env_standalone.sh ]; then
    if [ ! -d build ]; then
	if [ x${1} = 'xbuild' ]; then
            mkdir -p build/lib/python/FourTopNAOD
            ln -s ../../../../python build/lib/python/FourTopNAOD/RDF
	    echo "Build directory created for RDF, please source again standalone/env_standalone.sh without the build argument."
	else
	    echo "Build directory is not yet present for RDF, please source again standalone/env_standalone.sh with the build argument."
	fi
    else
	if [ x${1} = 'xbuild' ]; then
	    echo "Build directory is already present for RDF, please source again standalone/env_standalone.sh without the build argument."
	else
	    find build/lib/python python -type d -execdir touch '{}/__init__.py' \;
	    export FOURTOPNAOD_BASE=${PWD}
	    export PYTHONPATH=${FOURTOPNAOD_BASE}/build/lib/python:${PYTHONPATH}
	    echo "Standalone environment set."
	fi
    fi
    cd $CWD
else
    echo "Error in moving to the FourTopNAOD directory to setup the standalone environment for RDF"
    cd $CWD
fi

