#!/usr/bin/env python

mode = "RPC"
#mode = "DTCSC"

if mode == "RPC": chTitle = "Rolls"
else: chTitle = "Chambers"

lumiVal = 0.0

binW, xmin, xmax = 0.5, 70.5, 100
#binW, xmin, xmax = 1, -0.5, 100

from ROOT import *
from array import array
import os, sys
from math import sqrt
fName = sys.argv[1]

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

f = TFile(fName)
fout = open(fName.replace(".root",".txt"), "w")

rollNames = [[], []]
nExps = [[], []]
nRecs = [[], []]

hBarrel_Den  = f.Get("h_rollName_Barrel_detId_Den")
hBarrel_Num  = f.Get("h_rollName_Barrel_detId_Num")
hEndcapP_Den = f.Get("h_rollName_EndcapP_detId_Den")
hEndcapP_Num = f.Get("h_rollName_EndcapP_detId_Num")
hEndcapN_Den = f.Get("h_rollName_EndcapN_detId_Den")
hEndcapN_Num = f.Get("h_rollName_EndcapN_detId_Num")
for b in range(1, hBarrel_Den.GetNbinsX()+1):
    name = hBarrel_Den.GetXaxis().GetBinLabel(b+1)
    if name == '': break

    if name.startswith('W'):
        nExps[0].append(hBarrel_Den.GetBinContent(b))
        nRecs[0].append(hBarrel_Num.GetBinContent(b))
        rollNames[0].append(name)
    else:
        nExps[1].append(hEndcapP_Den.GetBinContent(b)+hEndcapN_Den.GetBinContent(b))
        nRecs[1].append(hEndcapP_Num.GetBinContent(b)+hEndcapN_Num.GetBinContent(b))
        rollNames[1].append(name)

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

for i in range(2):
    effs = []
    effs = [(name, 100*nRec/nExp) for name, nExp, nRec in zip(rollNames[i], nExps[i], nRecs[i]) if nExp > 0 and name not in blacklist]
    effs.sort(reverse=True, key=lambda x : x[1])

    hEffs[i].SetLineColor(TColor.GetColor("#000099"))
    hEffs[i].GetYaxis().SetNdivisions(505)
    hEffs[i].GetYaxis().SetTitleOffset(1.0)

    for eff in effs: hEffs[i].Fill(eff[1])

    peak = hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin())
    effsNoZero = [x[1] for x in effs if x[1] != 0.0]

    header = TLatex(gStyle.GetPadLeftMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                    "RPC Overall Efficiency - %s" % hEffs[i].GetTitle())
    header.SetNDC()
    header.SetTextAlign(11)
    header.SetTextFont(42)

    coverText1 = TLatex(0.17,0.82,"CMS")
    coverText2 = TLatex(0.17,0.80,"Preliminary")
    coverText3 = TLatex(0.17,0.75,"Data 2017")
    coverText1.SetNDC()
    coverText2.SetNDC()
    coverText3.SetNDC()
    coverText1.SetTextFont(62)
    coverText2.SetTextFont(52)
    coverText3.SetTextFont(52)
    coverText1.SetTextAlign(11)
    coverText2.SetTextAlign(13)
    coverText3.SetTextAlign(13)
    coverText1.SetTextSize(0.06)
    coverText2.SetTextSize(0.0456)
    coverText3.SetTextSize(0.0456)

    stats = ["Entries", "Mean", "RMS", "Underflow"], []
    stats[1].append("%d" % hEffs[i].GetEntries())
    stats[1].append("%.2f" % (sum([x for x in effsNoZero])/len(effsNoZero)))
    stats[1].append("%.2f" % sqrt(sum([x**2 for x in effsNoZero])/len(effsNoZero) - (sum([x for x in effsNoZero])/len(effsNoZero))**2))
    stats[1].append("%d" % len([x[1] for x in effs if x[1] < xmin]))

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

    canvs[i].cd()
    hEffs[i].Draw()
    coverText1.Draw()
    coverText2.Draw()
    coverText3.Draw()
    statPanel1.Draw()
    statPanel2.Draw()
    header.Draw()

    lumi = TLatex().DrawLatexNDC(1-gStyle.GetPadRightMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                                 "%.1f fb^{-1} (13 TeV)" % lumiVal)
    lumi.SetTextAlign(31)
    lumi.SetTextFont(42)

    fixOverlay()

    objs.extend([header, lumi, statPanel1, statPanel2])
    objs.extend([coverText1, coverText2, coverText3])

    for l in effs:
        print>>fout, l[0], l[1]

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

    c.Print("%s_%s.png" % (fName[:-5], c.GetName()))
    c.Print("%s_%s.pdf" % (fName[:-5], c.GetName()))
    c.Print("%s_%s.C" % (fName[:-5], c.GetName()))
