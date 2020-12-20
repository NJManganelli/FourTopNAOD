#!/bin/zsh
export BOOKKEEPING_TAG=NANOv7_CorrNov
for dir in *(/); do print ${dir} && print $(less ${dir}/crab.log | grep 'Output dataset DAS URL:' | sed -e "s/Output dataset DAS URL://g" | sed -e "s/https:\/\/cmsweb.cern.ch\/das\/request?input=/${BOOKKEEPING_TAG}\: dbs\:/g" | sed -e "s/\%2F/\//g" | sed -e "s/\&/ /g") && print ''; done