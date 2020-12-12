import copy
from glob import glob #For getFiles
import os, pwd, sys #For getFiles
import tempfile #For getFiles

def getFiles(query, redir="", outFileName=None, globSort=lambda f: int(f.split('_')[-1].replace('.root', '')), doEOSHOME=False, doGLOBAL=False, verbose=False):
    """Use one of several different methods to acquire a list or text file specifying the filenames.

Method is defined by a string passed to the query argument (required, first), with the type of query prepended to a string path.
'dbs:' - Used to signify getFiles should do a DAS query using the following string path
'glob:' - Used to signify getFiles should do a glob of the following string path, which should include a reference to the filetype, i.e. "glob:~/my2017ttbarDir/*/results/myTrees_*.root"
    optional - globSort is a lambda expression to sort the globbed filenames, with a default of lambda f: int(f.split('_')[-1].replace('.root', ''))
'list:' - Used to signify getFiles should open the file in the following path and return a List. 

outFileName can be specified for any option to also write a file with the list (as prepended with any redir string, specified with redir="root://cms-xrd-global.cern.ch" or "root://eoshome-<FIRST_INITIAL>.cern.ch/"
redir will prepend the redirector to the beginning of the paths, such as redir="root://cms-xrd-global.cern.ch/"
doEOSHOME will override the redir string with the one formatted based on your username for the eoshome-<FIRST_INITIAL>, which is your typical workspace on EOS (/eos/user/<FIRST_INITIAL>/<USERNAME>/)
    For example, this xrdcp will work with valid grid proxy or KRB5: "xrdcp root://eoshome-n.cern.ch//eos/user/n/nmangane/PATH/TO/ROOT/FILE.root ."
"""
    #methods to support: "dbs" using dasgoclient query, "glob" using directory path, "file" using text file
    fileList = []
    if doEOSHOME:
        #Set eoshome-<FIRST_INITIAL> as redirector, by getting the username and then the first initial from the username
        redir = "root://eoshome-{0:s}.cern.ch/".format((pwd.getpwuid(os.getuid())[0])[0])
    elif doGLOBAL:
        #Standard redirector
        redir = "root://cms-xrd-global.cern.ch/"
    elif redir != "":
        #accept redirector as-is
        pass
    else:
        redir = ""
    if "dbs:" in query:
        with tempfile.NamedTemporaryFile() as f:
            cmd = 'dasgoclient --query="file dataset={0:s}" > {1:s}'.format(query.replace("dbs:",""),f.name)
            if verbose:
                print("dbs query reformatted to:\n\t" + query)
            os.system(cmd)
            for line in f:
                fileList.append(line.decode("utf-8").rstrip("\s\n\t"))
    elif "glob:" in query:
        query_stripped = query.replace("glob:","")
        fileList = glob(query_stripped)
    elif "list:" in query:
        query_stripped = query.replace("list:","")
        fileList = []
        with open(query_stripped, "r") as in_f:
            for line in in_f:
                fileList.append(line.rstrip("\s\n\t"))
    else:
        print("No query passed to getFiles(), exiting")
        sys.exit(9001)
    if redir != "":
        if verbose: print("prepending redir")
        #Protect against double redirectors, assuming root:// is in the beginning
        if len(fileList) > 0 and "root://" not in fileList[0]:
            if verbose: print("Not prepending redirector, as one is already in place")
            fileList[:] = [redir + file for file in fileList]

    #Write desired output file with the list
    if outFileName:
        if verbose: print("Writing output file {0:s}".format(outFileName))
        with open(outFileName, 'w') as out_f:
            for line in fileList:
                out_f.write(line + "\n")
    #Return the list
    return fileList
