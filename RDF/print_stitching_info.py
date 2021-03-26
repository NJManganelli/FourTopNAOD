#ruamel may create environment conflicts, proceed with caution:
# pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps
import ruamel.yaml as yaml
import pdb

def print_stitching_info(ydict):
  for x, y in ydict.items():
    if "tt_" not in x:
      continue
    if "AH" in x or "GF" in x or "CR1-" in x or "CR2-" in x:
      continue
    y['splitProcess']['processes']
    keys = [kk for kk in y['splitProcess']['processes'].keys() if kk.endswith('_fr')]
    subXS = 0
    for kk in keys:
      subXS += y['splitProcess']['processes'][kk]['nominalXS']
    print("{:20}".format(x), "Sample XS*BR:", y.get("crossSection"), "     ", "Filtered Region XS*BR*FE:", subXS, "     ", "Ratio:", subXS/y.get("crossSection"))

test = None
# with open("../Kai/python/samplecards/2018_NanoAODv7.yaml", "r") as sample:
with open("../Kai/python/samplecards/2017_NanoAODv7.yaml", "r") as sample:
  test17 = yaml.load(sample)
  print("2017")
  print_stitching_info(test17)
with open("../Kai/python/samplecards/2018_NanoAODv7.yaml", "r") as sample:
  print("2018")
  test18 = yaml.load(sample)
  print_stitching_info(test18)

