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

hStack = THStack("Efficiency Comparison",";Efficiency;")

fName1 = sys.argv[1]
#fName2 = sys.argv[2]

#cHistories = [TCanvas("cHistory%d" % i) for i in range(2)]

Effhist_cat1 = TH1F("All Zero",";Efficiency;",100,0,1)
Effhist_cat2 = TH1F("All Good",";Efficiency;",100,0,1)
Effhist_cat3 = TH1F("Restoring",";Efficiency;",100,0,1)
Effhist_cat4 = TH1F("Others",";Efficiency;",100,0,1)
Effhist_all = TH1F("All categories",";Efficiency;",100,0,1)

#hFrame = TH1F("Comp","Comp;2017;2018",10,0,1)
#hFrame.SetMaximum(1.0)
#hFrame.Draw()

effs1 = {}
effs2 = {}
for line in open(fName1).readlines():
    cat, name, nominaleff = line.strip().split()
    effs1[name] = [int(cat), float(nominaleff)]

cHistories = [TCanvas("cHistory%d" % i) for i in range(7)]

for name in list(effs1.keys()):
    cat1 = effs1[name][0]
    eff1 = effs1[name][1]
    
    if cat1 == 1:
        Effhist_cat1.Fill(eff1)
    elif cat1 == 2:
        Effhist_cat2.Fill(eff1)
    elif cat1 == 3:
        Effhist_cat3.Fill(eff1)
    else:
        Effhist_cat4.Fill(eff1)

    Effhist_all.Fill(eff1)
'''
Effhist_cat1.SetLineColor(kBlue)
Effhist_cat2.SetLineColor(kBlue)
Effhist_cat3.SetLineColor(kBlue)
Effhist_cat4.SetLineColor(kBlue)
Effhist_all.SetLineColor(kBlue)
'''
Effhist_cat1.SetFillColor(kRed)
Effhist_cat2.SetFillColor(kBlue-9)
Effhist_cat3.SetFillColor(kGray+1)
Effhist_cat4.SetFillColor(kGreen+1)
Effhist_all.SetFillColor(kAzure+6)

leg1 = TLegend(0.3, 0.7, 0.7, 0.8)
leg1.SetFillStyle(0)
leg1.SetBorderSize(0)
leg1.AddEntry(Effhist_cat1, "All Zero, Mean = %.2f" %Effhist_cat1.GetMean(), "f")
leg2 = TLegend(0.3, 0.7, 0.7, 0.8)
leg2.SetFillStyle(0)
leg2.SetBorderSize(0)
leg2.AddEntry(Effhist_cat2, "All Good, Mean = %.2f" %Effhist_cat2.GetMean(), "f")
leg3 = TLegend(0.3, 0.7, 0.7, 0.8)
leg3.SetFillStyle(0)
leg3.SetBorderSize(0)
leg3.AddEntry(Effhist_cat3, "Sudden Drop, Mean = %.2f" %Effhist_cat3.GetMean(), "f")
leg4 = TLegend(0.3, 0.7, 0.7, 0.8)
leg4.SetFillStyle(0)
leg4.SetBorderSize(0)
leg4.AddEntry(Effhist_cat4, "Others, Mean = %.2f" %Effhist_cat4.GetMean(), "f")
legall = TLegend(0.3, 0.7, 0.7, 0.8)
legall.SetFillStyle(0)
legall.SetBorderSize(0)
legall.AddEntry(Effhist_all, "All categories, Mean = %.2f" %Effhist_all.GetMean(), "f")

legcat = TLegend(0.3, 0.7, 0.7, 0.9)
legcat.SetFillStyle(0)
legcat.SetBorderSize(0)
legcat.AddEntry(Effhist_cat1, "All Zero, Mean = %.2f" %Effhist_cat1.GetMean(), "f")
legcat.AddEntry(Effhist_cat2, "All Good, Mean = %.2f" %Effhist_cat2.GetMean(), "f")
legcat.AddEntry(Effhist_cat3, "Sudden Drop, Mean = %.2f" %Effhist_cat3.GetMean(), "f")
legcat.AddEntry(Effhist_cat4, "Others, Mean = %.2f" %Effhist_cat4.GetMean(), "f")

cHistories[0].cd()
Effhist_cat1.SetTitle("CCC")
Effhist_cat1.Draw()
leg1.Draw("same")
cHistories[1].cd()
Effhist_cat2.Draw()
leg2.Draw("same")
cHistories[2].cd()
Effhist_cat3.Draw()
leg3.Draw("same")
cHistories[3].cd()
Effhist_cat4.Draw()
leg4.Draw("same")
cHistories[4].cd()
Effhist_all.Draw()
legall.Draw("same")
cHistories[5].cd()
Effhist_cat2.Draw()
Effhist_cat1.Draw("same")
Effhist_cat3.Draw("same")
Effhist_cat4.Draw("same")
legcat.Draw("same")
cHistories[6].cd()
hStack.Add(Effhist_cat1)
hStack.Add(Effhist_cat3)
hStack.Add(Effhist_cat4)
hStack.Add(Effhist_cat2)
hStack.Draw()
legcat.Draw("same")

for c in cHistories:
    c.Modified()
    c.Update()
