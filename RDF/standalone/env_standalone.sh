#!/bin/bash

# Please setup python 2.7 and ROOT into your environment first

CWD=$PWD
if [ ${BASH_SOURCE[0]:0:1} == "/" ]; then
    FULLPATH=${BASH_SOURCE[0]}
else
    FULLPATH=$PWD/${BASH_SOURCE[0]}
fi
cd ${FULLPATH/%env_standalone.sh/}/..

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

