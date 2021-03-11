#!/bin/zsh
print 2018 ElMu DYJets_DL
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL/ElMu/
print 2018 ElMu DYJets_DL-HT100
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-100to200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT100/ElMu/
print 2018 ElMu DYJets_DL-HT200
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-200to400_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT200/ElMu/
print 2018 ElMu DYJets_DL-HT400
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT400/ElMu/
print 2018 ElMu DYJets_DL-HT600
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-600to800_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT600/ElMu/
print 2018 ElMu DYJets_DL-HT800
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-800to1200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT800/ElMu/
print 2018 ElMu DYJets_DL-HT1200
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT1200/ElMu/
print 2018 ElMu DYJets_DL-HT2500
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/DYJetsToLL_M-50_HT-2500toInf_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/DYJets_DL-HT2500/ElMu/
print 2018 ElMu ST_tW
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_tW/ElMu/
print 2018 ElMu ST_tbarW
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_tbarW/ElMu/
print 2018 ElMu ST_tW-NoFHad
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_tW-NoFHad/ElMu/
print 2018 ElMu ST_tbarW-NoFHad
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_tbarW-NoFHad/ElMu/
print 2018 ElMu ST_s-channel
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_s-channel/ElMu/
print 2018 ElMu ST_t_t-channel
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_t_t-channel/ElMu/
print 2018 ElMu ST_tbar_t-channel
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ST_tbar_t-channel/ElMu/
print 2018 ElMu ttH
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttH/ElMu/
print 2018 ElMu ttH_DL-bb
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ttHTobb_ttTo2L2Nu_M125_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttH_DL-bb/ElMu/
print 2018 ElMu ttH_SL-bb
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ttHTobb_ttToSemiLep_M125_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttH_SL-bb/ElMu/
print 2018 ElMu ttHH
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTHH_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttHH/ElMu/
print 2018 ElMu ttWH
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTWH_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttWH/ElMu/
print 2018 ElMu ttWJets
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttWJets/ElMu/
print 2018 ElMu ttWJets_QQ
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttWJets_QQ/ElMu/
print 2018 ElMu ttWJets_LNu
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttWJets_LNu/ElMu/
print 2018 ElMu ttWW
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTWW_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttWW/ElMu/
print 2018 ElMu ttWZ
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTWZ_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttWZ/ElMu/
print 2018 ElMu ttZH
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTZH_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttZH/ElMu/
print 2018 ElMu ttZJets
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttZJets/ElMu/
print 2018 ElMu ttZZ
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTZZ_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttZZ/ElMu/
print 2018 ElMu ttZ_DL-M10
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttZ_DL-M10/ElMu/
print 2018 ElMu ttZ_DL-M1to10
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTZToLL_M-1to10_TuneCP5_13TeV-amcatnlo-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttZ_DL-M1to10/ElMu/
print 2018 ElMu ttZ_QQ
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ttZ_QQ/ElMu/
print 2018 ElMu tt_AH
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH/ElMu/
print 2018 ElMu tt_AH-CR1-QCD
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_TuneCP5CR1_QCDbased_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH-CR1-QCD/ElMu/
print 2018 ElMu tt_AH-CR2-GluonMove
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_TuneCP5CR2_GluonMove_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH-CR2-GluonMove/ElMu/
print 2018 ElMu tt_AH-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH-HDAMPdown/ElMu/
print 2018 ElMu tt_AH-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH-HDAMPup/ElMu/
print 2018 ElMu tt_AH-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_TuneCP5down_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH-TuneCP5down/ElMu/
print 2018 ElMu tt_AH-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToHadronic_TuneCP5up_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_AH-TuneCP5up/ElMu/
print 2018 ElMu tt_DL
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL/ElMu/
print 2018 ElMu tt_DL-CR1-QCD
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_TuneCP5CR1_QCDbased_13TeV-powheg-pythia8/nmangane-NoveCampaign-1cea6da0d07fd8de4a53b465a6714af5/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-CR1-QCD/ElMu/
print 2018 ElMu tt_DL-CR2-GluonMove
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_TuneCP5CR2_GluonMove_13TeV-powheg-pythia8/nmangane-NoveCampaign-1cea6da0d07fd8de4a53b465a6714af5/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-CR2-GluonMove/ElMu/
print 2018 ElMu tt_DL-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-1cea6da0d07fd8de4a53b465a6714af5/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-HDAMPdown/ElMu/
print 2018 ElMu tt_DL-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-HDAMPup/ElMu/
print 2018 ElMu tt_DL-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-TuneCP5down/ElMu/
print 2018 ElMu tt_DL-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-TuneCP5up/ElMu/
print 2018 ElMu tt_DL-GF
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-GF/ElMu/
print 2018 ElMu tt_DL-GF-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_HT500Njet7_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-GF-HDAMPdown/ElMu/
print 2018 ElMu tt_DL-GF-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_HT500Njet7_hdampUP_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-GF-HDAMPup/ElMu/
print 2018 ElMu tt_DL-GF-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5down_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-GF-TuneCP5down/ElMu/
print 2018 ElMu tt_DL-GF-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5up_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_DL-GF-TuneCP5up/ElMu/
print 2018 ElMu tt_SL
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL/ElMu/
print 2018 ElMu tt_SL-CR1-QCD
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_TuneCP5CR1_QCDbased_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-CR1-QCD/ElMu/
print 2018 ElMu tt_SL-CR2-GluonMove
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_TuneCP5CR2_GluonMove_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-CR2-GluonMove/ElMu/
print 2018 ElMu tt_SL-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-HDAMPdown/ElMu/
print 2018 ElMu tt_SL-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-HDAMPup/ElMu/
print 2018 ElMu tt_SL-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-TuneCP5down/ElMu/
print 2018 ElMu tt_SL-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-TuneCP5up/ElMu/
print 2018 ElMu tt_SL-GF
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-GF/ElMu/
print 2018 ElMu tt_SL-GF-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLepton_HT500Njet9_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-GF-HDAMPdown/ElMu/
print 2018 ElMu tt_SL-GF-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLepton_HT500Njet9_hdampUP_TuneCP5_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-GF-HDAMPup/ElMu/
print 2018 ElMu tt_SL-GF-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLepton_HT500Njet9_TuneCP5down_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-GF-TuneCP5down/ElMu/
print 2018 ElMu tt_SL-GF-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTToSemiLepton_HT500Njet9_TuneCP5up_13TeV-powheg-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tt_SL-GF-TuneCP5up/ElMu/
print 2018 ElMu tttJ
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTJ_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tttJ/ElMu/
print 2018 ElMu tttW
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTW_TuneCP5_13TeV-madgraph-pythia8/nmangane-NoveCampaign-b007c9995322e232a5f950905968126e/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tttW/ElMu/
print 2018 ElMu tttt
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/nmangane-NoveCampaign-1cea6da0d07fd8de4a53b465a6714af5/USER  instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/tttt/ElMu/
print 2018 ElMu ElMu_A
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__ElMu_A.txt_corrected' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir  --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ElMu_A/ElMu/
print 2018 ElMu ElMu_B
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__ElMu_B.txt_corrected' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir  --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ElMu_B/ElMu/
print 2018 ElMu ElMu_C
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__ElMu_C.txt_corrected' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir  --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ElMu_C/ElMu/
print 2018 ElMu ElMu_D
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__ElMu_D.txt_corrected' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir  --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ElMu_D/ElMu/