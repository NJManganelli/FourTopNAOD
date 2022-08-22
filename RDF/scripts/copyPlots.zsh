#!/bin/zsh
analysis_dir_base_notag=$1
analysis_base_tag=$2
varSet=$3
categorySet=$4
print ${analysis_dir_base_notag}
print ${analysis_base_tag}
print ${varSet}
print ${categorySet}
for e in 2017 2018; 
  for t in ${analysis_base_tag}_${e}; 
    for c in ElMu MuMu ElEl;
      for x in $(ls ${analysis_dir_base_notag}/${t}/Plots/${e}/${c}/${varSet}_${categorySet}_${e}_${c}_DeepJet/nominal | grep .pdf | grep -v ${varSet}_${categorySet}); 
        do mkdir -p ~/FourTopAN/AN-20-085/figures_control/${t}/ &&
        cp ${analysis_dir_base_notag}/${t}/Plots/${e}/${c}/${varSet}_${categorySet}_${e}_${c}_DeepJet/nominal/${x} ~/FourTopAN/AN-20-085/figures_control/${t}/${varSet}_${categorySet}_${e}_${c}${x:s/nMediumDeepJetB2p//:s/nMediumDeepJetB3p//:s/nMediumDeepJetB4p//:s/nMediumDeepJetB2//:s/nMediumDeepJetB3//:s/nMediumDeepJetB4//};
      done
