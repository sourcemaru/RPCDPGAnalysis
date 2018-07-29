#!/usr/bin/env python

mode = "RPC"
#mode = "DTCSC"

if mode == "RPC": chTitle = "Rolls"
else: chTitle = "Chambers"

binW, xmin, xmax = 0.5, 70.5, 100
#binW, xmin, xmax = 1, -0.5, 100

from ROOT import *
from array import array
import os, sys
from math import sqrt
from RPCDPGAnalysis.SegmentAndTrackOnRPC.buildLabels_cff import *

era = "Run2017"
if len(sys.argv) > 2: era = sys.argv[1]

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()
gStyle.SetOptStat(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.12)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.06, "X");
gStyle.SetTitleSize(0.06, "Y");

blacklist = []
#blacklist.extend([x.strip().split()[1] for x in open("blackList_18May.txt").readlines() if x.strip() != ""])
#blacklist.extend(["RE+3_R2_CH%02d_C" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE-3_R2_CH%02d_C" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE+4_R2_CH%02d_B" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE-4_R2_CH%02d_B" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE+4_R2_CH%02d_C" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE-4_R2_CH%02d_C" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE+2_R3_CH%02d_A" % (ch+1) for ch in range(36)])
#blacklist.extend(["RE-2_R3_CH%02d_A" % (ch+1) for ch in range(36)])

## Collect per-roll counts
counts = {}
for fName in sys.argv[2:]:
    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if name not in counts: counts[name] = [den, num]
        else: counts[name] = [counts[name][0]+den, counts[name][1]+num]

effMap = {}
with open("efficiency.txt", "w") as fout:
    print>>fout, "#RollName efficiency errLo errHi"
    for name in sorted(counts.keys()):
        den, num = counts[name]
        if den == 0:
            print name, -1, 0, 0
            continue

        eff = num/den
        errLo = abs(eff - TEfficiency.ClopperPearson(den, num, 0.683, False))
        errHi = abs(TEfficiency.ClopperPearson(den, num, 0.683, True) - eff) 

        print>>fout, name, eff, errLo, errHi, den
        effMap[name] = [eff, errLo, errHi, den]

#######################################
## Draw plots
nbin = int((xmax-xmin)/binW)
objs = []
hEffs = [
    TH1F("hEffBarrel", "Barrel;Efficiency [%];Number of "+chTitle, nbin+1, xmin, xmax+binW),
    TH1F("hEffEndcap", "Endcap;Efficiency [%];Number of "+chTitle, nbin+1, xmin, xmax+binW),
]
canvs = [
    TCanvas("cBarrel", "cBarrel", 485, 176, 800, 600),
    TCanvas("cEndcap", "cEndcap", 485, 176, 800, 600),
]
hEffs[0].SetFillColor(30)
hEffs[1].SetFillColor(38)
hEffs[0].SetLineColor(TColor.GetColor("#007700"))
hEffs[1].SetLineColor(TColor.GetColor("#000099"))

effs = [
    [100*effMap[name][0] for name in effMap.keys() if name.startswith("W") and name not in blacklist and effMap[name][-1] > 100],
    [100*effMap[name][0] for name in effMap.keys() if not name.startswith("W") and name not in blacklist and effMap[name][-1] > 100],
]

for i in range(2):
    hEffs[i].GetYaxis().SetNdivisions(505)
    hEffs[i].GetYaxis().SetTitleOffset(1.0)

    for eff in effs[i]: hEffs[i].Fill(eff)
    effsNoZero = [eff for eff in effs[i] if eff != 0.0]
    effsOver70 = [eff for eff in effs[i] if eff > 70]
    effOver70 = sum(effsOver70)/len(effsOver70)

    header = TLatex(gStyle.GetPadLeftMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                    "RPC Overall Efficiency - %s" % hEffs[i].GetTitle())
    header.SetNDC()
    header.SetTextAlign(11)
    header.SetTextFont(42)

    stats = ["Entries", "Mean", "RMS", "Underflow"], []
    stats[1].append("%d" % hEffs[i].GetEntries())
    stats[1].append("%.2f" % (sum([x for x in effsNoZero])/len(effsNoZero)))
    stats[1].append("%.2f" % sqrt(sum([x**2 for x in effsNoZero])/len(effsNoZero) - (sum([x for x in effsNoZero])/len(effsNoZero))**2))
    stats[1].append("%d" % len([x for x in effs[i] if x < xmin]))

    statPanel1 = TPaveText(0.53,0.68,0.76,0.85,"brNDC")
    statPanel2 = TPaveText(0.53,0.68,0.76,0.85,"brNDC")
    for s in zip(stats[0], stats[1]):
        statPanel1.AddText(s[0])
        statPanel2.AddText(s[1])
    statPanel1.SetBorderSize(0)
    statPanel1.SetFillColor(0)
    statPanel1.SetFillStyle(0)
    statPanel1.SetTextSize(0.04)
    statPanel1.SetTextAlign(10)
    statPanel1.SetBorderSize(0)
    statPanel1.SetTextFont(62)
    statPanel2.SetBorderSize(0)
    statPanel2.SetFillColor(0)
    statPanel2.SetFillStyle(0)
    statPanel2.SetTextSize(0.04)
    statPanel2.SetTextAlign(31)
    statPanel2.SetBorderSize(0)
    statPanel2.SetTextFont(62)

    statPanelOver70 = TText(0.18, 0.5, "Mean (>70%%) = %.2f%%" % effOver70)
    statPanelOver70.SetTextSize(0.05)
    statPanelOver70.SetTextFont(62)
    statPanelOver70.SetNDC()

    canvs[i].cd()
    hEffs[i].Draw()
    statPanel1.Draw()
    statPanel2.Draw()
    statPanelOver70.Draw()
    header.Draw()
    lls = buildLabel(era, "inset")
    for ll in lls: ll.Draw()

    fixOverlay()

    objs.extend([statPanel1, statPanel2, statPanelOver70, header])
    objs.extend(lls)

for c in canvs:
    c.cd()

    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetBorderSize(2)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.04)
    c.SetTopMargin(0.08)
    c.SetBottomMargin(0.12)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)

    c.Modified()
    c.Update()

    c.Print("%s_%s.png" % (era, c.GetName()))
    c.Print("%s_%s.pdf" % (era, c.GetName()))
    c.Print("%s_%s.C" % (era, c.GetName()))
