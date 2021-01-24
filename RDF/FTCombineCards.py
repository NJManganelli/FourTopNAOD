from __future__ import print_function, division
import argparse
from FourTopNAOD.RDF.combine.templating import write_combine_cards

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
    parser.add_argument('--categories', dest='categories', action='store', nargs='*', type=str, default=["HT500_nMediumDeepJetB2_nJet4", "HT500_nMediumDeepJetB2_nJet5", "HT500_nMediumDeepJetB2_nJet6", "HT500_nMediumDeepJetB2_nJet7", "HT500_nMediumDeepJetB2_nJet8p",
                                                                                                         "HT500_nMediumDeepJetB3_nJet4", "HT500_nMediumDeepJetB3_nJet5", "HT500_nMediumDeepJetB3_nJet6", "HT500_nMediumDeepJetB3_nJet7", "HT500_nMediumDeepJetB3_nJet8p",
                                                                                                         "HT500_nMediumDeepJetB4p_nJet4", "HT500_nMediumDeepJetB4p_nJet5", "HT500_nMediumDeepJetB4p_nJet6", "HT500_nMediumDeepJetB4p_nJet7", "HT500_nMediumDeepJetB4p_nJet8p"],
                        help='categories for the combine cards, i.e. HT500_nMediumDeepJetB2_nJet8p')
    parser.add_argument('--template', dest='template', action='store', type=str, default="TTTT_templateV5.txt",
                        help='directory for analysis inputs and outputs')
    parser.add_argument('--verbose', dest='verbose', action='store_true',
                        help='Enable more verbose output during actions')

    args = parser.parse_args()

    print("Function called from FTPlotting.py with --combineInput $VAR and --combineCards will integrate template counts into the generated cards.")
    write_combine_cards(args.analysisDirectory, args.era, args.channel, args.variable, args.categories, template=args.template)
