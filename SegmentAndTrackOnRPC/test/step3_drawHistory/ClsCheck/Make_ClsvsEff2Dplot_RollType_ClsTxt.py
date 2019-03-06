#!/usr/bin/env python

import sys, os
from ROOT import *

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)

hist = {}
meanset = {}

Roll = {}

runs = []
for line in open(sys.argv[1]).readlines():
    line = line.strip()
    if len(line) == 0 or line.startswith('#'): continue
    name = line.split()[0]

    hist[name] = TH1F("%s" % name, ";Efficiency;", 100, 0, 1)

for fName in sys.argv[1:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

f1 = open("Cls_test2.txt", 'w')

for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, nEntries, mean, err2 = line.split()
        mean = float(mean)

        if name not in Roll : Roll[name] = [0.,0]
        if mean == 0 : continue

        Roll[name][0] += mean
        Roll[name][1] += 1

for name in Roll:
    if Roll[name][1] == 0 : Roll[name].append(-1)
    else : Roll[name].append(Roll[name][0]/Roll[name][1])

    linename = str(name) + " " + str(Roll[name][0]) + " " + str(Roll[name][1]) + " " + str(Roll[name][2]) + "\n"
    f1.write(linename)

f1.close()
