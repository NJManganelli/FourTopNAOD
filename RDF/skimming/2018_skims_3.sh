# print tt_AH
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext2-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH/
# print tt_AH-CR1-QCD
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_TuneCP5CR1_QCDbased_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH-CR1-QCD/
# print tt_AH-CR2-GluonMove
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_TuneCP5CR2_GluonMove_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH-CR2-GluonMove/
print tt_AH-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH-HDAMPdown/
print tt_AH-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH-HDAMPup/
print tt_AH-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_TuneCP5down_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH-TuneCP5down/
print tt_AH-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToHadronic_TuneCP5up_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_AH-TuneCP5up/
# print tt_DL
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL/
print tt_DL-CR1-QCD
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_TuneCP5CR1_QCDbased_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-CR1-QCD/
print tt_DL-CR2-GluonMove
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_TuneCP5CR2_GluonMove_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-CR2-GluonMove/
print tt_DL-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext2-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-HDAMPdown/
print tt_DL-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-HDAMPup/
print tt_DL-TuneCP5down
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_TuneCP5down_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-TuneCP5down/
print tt_DL-TuneCP5up
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_TuneCP5up_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-TuneCP5up/
# print tt_DL-GF
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-GF/
print tt_DL-GF-HDAMPdown
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_HT500Njet7_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-GF-HDAMPdown/
print tt_DL-GF-HDAMPup
python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_HT500Njet7_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-GF-HDAMPup/
# print tt_DL-GF-TuneCP5down
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5down_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-GF-TuneCP5down/
# print tt_DL-GF-TuneCP5up
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTTo2L2Nu_HT500Njet7_TuneCP5up_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_DL-GF-TuneCP5up/
# print tt_SL
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext3-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL/
# print tt_SL-CR1-QCD
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_TuneCP5CR1_QCDbased_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-CR1-QCD/
# print tt_SL-CR2-GluonMove
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_TuneCP5CR2_GluonMove_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-CR2-GluonMove/
# print tt_SL-HDAMPdown
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-HDAMPdown/
# print tt_SL-HDAMPup
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-HDAMPup/
# print tt_SL-TuneCP5down
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_TuneCP5down_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-TuneCP5down/
# print tt_SL-TuneCP5up
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLeptonic_TuneCP5up_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-TuneCP5up/
# print tt_SL-GF
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLepton_HT500Njet9_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-GF/
# print tt_SL-GF-HDAMPdown
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLepton_HT500Njet9_hdampDOWN_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-GF-HDAMPdown/
# print tt_SL-GF-HDAMPup
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLepton_HT500Njet9_hdampUP_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-GF-HDAMPup/
# print tt_SL-GF-TuneCP5down
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLepton_HT500Njet9_TuneCP5down_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v1/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-GF-TuneCP5down/
# print tt_SL-GF-TuneCP5up
# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input dbs:/TTToSemiLepton_HT500Njet9_TuneCP5up_13TeV-powheg-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21-v2/NANOAODSIM --write --nThreads 12 --simultaneous 3 --keep run event genTtbarId genWeight nLHEPart LHEPart_pdgId nGenJet GenJet_pt GenJet_eta nElectron Electron_pt Electron_eta Electron_ip3d Electron_dz Electron_cutBased Electron_jetIdx nMuon Muon_pt Muon_eta Muon_ip3d Muon_dz Muon_looseId Muon_pfIsoId Muon_jetIdx nJet Jet_pt Jet_eta Jet_jetId --redir --outdir /eos/cms/store/user/nmangane/NANOv7_bookkeeping/skims/2018/tt_SL-GF-TuneCP5up/
