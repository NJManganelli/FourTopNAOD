from root_numpy import root2array, array2root
import json
import numpy as np
import argparse
import pandas as pd
import sys
# sys.path.append("/uscms_data/d3/mquinnan/Nano4top2/CMSSW_10_2_10/src/PhysicsTools/NanoTrees/python/macros/plotting/")
# import RootStuff as rs
import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True
print("We can work this out!")
parser = argparse.ArgumentParser(description='adds eventBDT discriminants to premade trees.')
parser.add_argument("-f", "--filenames", dest="filenames", nargs="*", default=[])
parser.add_argument("-c", "--compfile", dest="compfile", default='')
#if filenames is not specified, will not recreate json file
#if compfile is not specified, will not compare files

parser.add_argument("-v", "--vars", dest="vars", nargs="*", default=['event', 'run', 'lumi'])
parser.add_argument("-s", "--samp", dest="samp", default='TTTT')
parser.add_argument("-t", "--treename", dest="treename", default='Events')
parser.add_argument("-e", "--eventname", dest="eventname", default='event')
parser.add_argument("-l", "--luminame", dest="luminame", default='lumi')
parser.add_argument("-b", "--baseline", dest="base", default='nleptons==0 & ht>700 & njets>=9 & nbjets>=3')
parser.add_argument("-o", "--outfile", dest="outfile", default='output.json')
args = parser.parse_args()
print("filenames: {}".format(args.filenames))
print("comparison file: {}".format(args.compfile))
print("sample: {}".format(args.samp))
print("treename: {}".format(args.treename))
print("eventname: {}".format(args.eventname))
print("luminame: {}".format(args.luminame))
print("variables: {}".format(args.vars))
print("outfile: {}".format(args.outfile))


#function to wrtie json file
def write_json(args, jsonFile):
#clear file if not empty
    full_json = {}

#loop over rootfiles and apply baseline
    totevts = 0
    for f in args.filenames: #get proper outname:
        outf=f
        if "/eos/uscms/" in f:
            f=f.replace("/eos/uscms/","root://cmseos.fnal.gov/")
        print 'prepping input file', f, '...'

        data = pd.DataFrame(root2array(f, args.treename, selection=args.base))
        print '# input events in file:', len(data)
        totevts+=len(data)
        if len(data)==0:
            continue

        #extract information and fill json file    
        for i,d in enumerate(data[args.eventname]):
            json_data = {}
            for obj in args.vars:
                json_data[obj]=int(data[obj][i])
            # print d
            dictname = str(d)+'_'+str(data[args.luminame][i])
            # print dictname
            full_json[dictname] = json_data

        #print # keys in full dictionary for each file 
        print 'total events in json file:', len(full_json.keys())

    jsonFile.write(json.dumps(full_json, sort_keys=True))
    print '# files scanned:', len(args.filenames)
    print 'Total # input events:', totevts

#function to compare two dictionaries/json files
def compare_dict(a,b):   
    ngood_a = 0; ngood_b = 0;nbad = 0; nbad_val = 0; nvgood = 0
    for k,v in a.iteritems():         
        # event check
        if k in b:            
            nbad+=1
            print 'event',k, 'also in', args.compfile
        else:
            goodval=True
            ngood_a+=1
            # for subk, subv in v.iteritems():
            #     if subv != b[k][subk]:               
            #         goodval=False
            #         print 'for event', k, 'variable', v,':', subv, 'does not match', b[k][subk], 'in', args.compfile
            # if goodval:
            #     nvgood+=1

    for k,v in b.iteritems():         
        # event check
        if k in a:
            pass
            # nbad_b+=1
            # print 'event',k, 'also in', outjson
        else:
            ngood_b+=1

    print '---------------------------------------------------------------'
    print '# non-overlapping events:', ngood_a, 'in', outjson, ngood_b, 'in', args.compfile
    print '# events in', args.compfile, 'also in', outjson,':', nbad
    # print '# events in',outjson, 'also in', args.compfile,':', nbad_b
    # print '# events with mismatched values:', nbad_val 
    print 'fractional overlap:', outjson, (float(nbad)/float(ngood_a+nbad)), args.compfile, (float(nbad)/float(ngood_b+nbad))
    # print '% events with matched values:', (float(nvgood)/float(ngood))




########################################################################
outjson = args.samp + '_' + args.outfile

if len(args.filenames)>0:
    print 'will create and write to ', outjson
    with open(outjson, 'w') as jsonFile:
        write_json(args, jsonFile)
    jsonFile.close()

elif len(args.filenames)==0:
    print 'no files provided. will read json file', outjson

if args.compfile != '':
#compare two text files, outputting % overlap
    with open(args.compfile, 'r') as compFile:
        with open(outjson, 'r') as myFile:
            compfile = json.load(compFile)    
            myfile   = json.load(myFile)
            compare_dict(myfile, compfile)

else:
    print 'no compfile provided'
