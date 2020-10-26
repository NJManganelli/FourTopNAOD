from __future__ import print_function, division
import argparse

def main(analysisDirectory, era, channel, variable, categories, template="TTTT_templateV3.txt"):
    outputLines = []
    with open(template, "r") as inFile:
        for line in inFile:
            outputLines.append(line)
    for category in categories:
        with open("{}/TTTT_{}_{}_{}_{}.txt".format(analysisDirectory, era, channel, category, variable).replace("//", "/"), "w") as outFile:
            for line in outputLines:
                outFile.write(line.replace("$ERA", era).replace("$CHANNEL", channel)\
                              .replace("$CATEGORY", category).replace("$VAR", variable))
            print("Finished writing output for category {}".format(category))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate cards from simple template')
    parser.add_argument('--analysisDirectory', dest='analysisDirectory', action='store', type=str, default="/eos/user/$U/$USER/analysis/$DATE",
                        help='directory for analysis inputs and outputs')
    parser.add_argument('--era', dest='era', type=str, default="2017", choices=['2017', '2018'],
                        help='era for creating templated combine cards')
    parser.add_argument('--variable', dest='variable', action='store', type=str, default="HT", choices=['HT'],
                        help='combine input for opposite-sign dilepton analysis')
    parser.add_argument('--channel', dest='channel', action='store', type=str, default="ElMu", choices=['ElMu', 'ElEl', 'MuMu'],
                        help='Decay channel for opposite-sign dilepton analysis')
    parser.add_argument('--categories', dest='categories', action='store', nargs='*', type=str, default="nMediumDeepJetB2_nJet4",
                        help='categories for the combine cards, i.e. nMediumDeepJetB2_nJet8p')
    parser.add_argument('--template', dest='template', action='store', type=str, default="TTTT_templateV3.txt",
                        help='directory for analysis inputs and outputs')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')

    args = parser.parse_args()

    main(args.analysisDirectory, args.era, args.channel, args.variable, args.categories, template=args.template)
