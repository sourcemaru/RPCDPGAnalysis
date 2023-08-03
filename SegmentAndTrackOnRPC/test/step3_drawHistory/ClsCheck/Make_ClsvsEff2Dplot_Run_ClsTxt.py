#!/usr/bin/env python

import sys, os
from ROOT import *

from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import set_tdr_style
set_tdr_style()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)

hist = {}
meanset = {}

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

f1 = open("Cls_test.txt", 'w')

for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    RE4_avgsum = 0
    RE4_number = 0
    Endcap_avgsum = 0
    Endcap_number = 0
    Barrel_avgsum = 0
    Barrel_number = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, nEntries, mean, err2 = line.split()
        mean = float(mean)
        if mean == 0 : continue

        if name.startswith("RE+4")or name.startswith("RE-4"):
            RE4_number += 1
            RE4_avgsum += mean
        elif name.startswith("W"):
            Barrel_number += 1
            Barrel_avgsum += mean
        else:
            Endcap_number += 1
            Endcap_avgsum += mean
    if RE4_number == 0 : RE4_runavg = -1
    else :RE4_runavg = RE4_avgsum/RE4_number
    if Barrel_number == 0 : Barrel_runavg = -1
    else :Barrel_runavg = Barrel_avgsum/Barrel_number
    if Endcap_number == 0 : Endcap_runavg = -1
    else :Endcap_runavg = Endcap_avgsum/Endcap_number

    linename = str(run) + " " + str(Endcap_runavg) + " " + str(Barrel_runavg) + " " + str(RE4_runavg) + "\n"
    f1.write(linename)

f1.close()
