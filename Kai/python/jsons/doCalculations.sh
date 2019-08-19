#!/bin/zsh
####2018 Calculation for SF split at run 316361####
print 'Doing lumi calculation for 2018 around the split in run 316361, for the muon SL HLT SF weighting'
print 'Run2018 < 316361'
brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 315252 --end 316360 -u /fb -i Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt --hltpath "HLT_IsoMu24_v*"
print 'Run2018 >= 316361'
brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 316361 --end 325175 -u /fb -i Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt --hltpath "HLT_IsoMu24_v*"



####2018 nominal eras####
# print '\n\nDoing lumi calculation for 2018 nominal, with normtag and golden json'
# print 'Run 2018A'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 315252 --end 316995 -u /fb -i Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt
# print 'Run 2018B'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 317080 --end 319310 -u /fb -i Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt
# print 'Run 2018C'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 319337 --end 320065 -u /fb -i Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt
# print 'Run 2018D'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 320673 --end 325175 -u /fb -i Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt


####2017 nominal eras####
# print '\n\nDoing lumi calculation for 2017 nominal, with normtag and golden json'
# print 'Run 2017B'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 297046 --end 299329 -u /fb -i Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt
# print 'Run 2017C'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 299368 --end 302029 -u /fb -i Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt
# print 'Run 2017D'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 302030 --end 303434 -u /fb -i Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt
# print 'Run 2017E'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 303824 --end 304797 -u /fb -i Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt
# print 'Run 2017F'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 305040 --end 306462 -u /fb -i Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt


####2016 nominal eras####
# print '\n\nDoing lumi calculation for 2016 nominal, with normtag and golden json'
# print 'Run 2016A'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 271036 --end 271658 -u /fb -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
# print 'Run 2016B'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 272007 --end 275376 -u /fb -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
# print 'Run 2016C'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 275657 --end 276283 -u /fb -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
# print 'Run 2016D'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 276315 --end 276811 -u /fb -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
# print 'Run 2016E'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 276831 --end 277420 -u /fb -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
# print 'Run 2016F'
# brilcalc lumi --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --begin 277772 --end 278808 -u /fb -i Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt
