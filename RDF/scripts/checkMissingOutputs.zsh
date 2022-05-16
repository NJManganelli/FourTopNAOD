#!/bin/zsh
tagnoera=${1}
varset=${2}
catset=${3}



if [[ (-z ${varset} ) && (-z ${catset} ) ]]; then
    print Checking BTaggingYields
    for era in 2017 2018; for c in ElMu ElEl MuMu; for s in $(less standardmc.txt | grep -v '\tt_DL\|tt_SL') ttbb_SL-GF_fr ttbb_SL_fr ttbb_SL_nr ttbb_DL-GF_fr ttbb_DL_fr ttbb_DL_nr ttother_SL-GF_fr ttother_SL_fr ttother_SL_nr ttother_DL-GF_fr ttother_DL_fr ttother_DL_nr; do if [[ $(ls /eos/user/n/nmangane/analysis/${tagnoera}_${era}/BTaggingYields/${c}/${era}*.root | grep -c ${s}) -lt 1 ]]; then print ${c} ${era} ${s}; fi; done;
fi

if [[ (-n ${varset} ) && (-n ${catset} ) ]]; then
    print Checking Combine Outputs
    for era in 2017 2018; for c in ElMu ElEl MuMu; for s in $(less standardmc.txt | grep -v '\tt_DL\|tt_SL') ttbb_SL-GF_fr ttbb_SL_fr ttbb_SL_nr ttbb_DL-GF_fr ttbb_DL_fr ttbb_DL_nr ttother_SL-GF_fr ttother_SL_fr ttother_SL_nr ttother_DL-GF_fr ttother_DL_fr ttother_DL_nr; do if [[ $(ls /eos/user/n/nmangane/analysis/${tagnoera}_${era}/Combine/${c}/${era}___*___${varset}___${catset}___all.root | grep -c ${s}) -lt 1 ]]; then print ${c} ${era} ${s}; fi; done;
fi


