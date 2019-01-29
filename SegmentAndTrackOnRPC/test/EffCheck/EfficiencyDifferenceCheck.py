#!/usr/bin/env python

import sys, os
from ROOT import *

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()

gStyle.SetOptStat(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)

fName1 = sys.argv[1]
fName2 = sys.argv[2]

effMap1, effMap2 = {}, {}
for line in open(fName1).readlines():
	if line.startswith('#'): continue
	if len(line) == 0: continue
	rollName, eff, errLo, errHi, nEff = line.strip().split()
	eff, errLo, errHi, nEff = 100*float(eff), 100*float(errLo), 100*float(errHi), 100*float(nEff)
	effMap1[rollName] = [eff, errLo, errHi]

for line in open(fName2).readlines():
	if line.startswith('#'): continue
	if len(line) == 0: continue
	rollName, eff, errLo, errHi, nEff = line.strip().split()
	eff, errLo, errHi, nEff = 100*float(eff), 100*float(errLo), 100*float(errHi), 100*float(nEff)
	effMap2[rollName] = [eff, errLo, errHi]

GBarrel = TGraphAsymmErrors()
GEndcap = TGraphAsymmErrors()

for rollName in effMap1:
	eff1, errLeft, errRight = effMap1[rollName]
	eff2, errDown, errUp = effMap2[rollName]

	if eff1 - eff2 > 15. : print "[Eff Dif > 15] ", rollName, "  ", eff1, eff2
	#if eff1 < 70. : print "[PEff < 70] ", rollName, "  ", eff1
	#if eff2 < 70. : print "[CEff < 70] ", rollName, "  ", eff2

	#print errLeft, errRight, errUp, errDown

	n1 = GBarrel.GetN()
	n2 = GEndcap.GetN()
	
	if rollName.startswith("W"):
		GBarrel.SetPoint(n1, eff1, eff2)
		GBarrel.SetPointError(n1, errLeft, errRight, errDown, errUp)
	if rollName.startswith("R"):
                GEndcap.SetPoint(n2, eff1, eff2)
                GEndcap.SetPointError(n2, errLeft, errRight, errDown, errUp)
	
GBarrel.SetMarkerStyle(20)
GBarrel.SetMarkerColor(kRed)
GBarrel.SetMarkerSize(.5)
GEndcap.SetMarkerStyle(24)
GEndcap.SetMarkerColor(kBlue)
GEndcap.SetMarkerSize(.5)

GBarrel.Draw('AP')
GEndcap.Draw('sameP')
'''
Titlename = TLatex(0.3,0.945,"Efficiency Change Check")
Titlename.SetNDC()
Titlename.SetTextFont(52)
Titlename.SetTextAlign(11)
Titlename.SetTextSize(0.05)
'''
XaxisText = TLatex(0.63,0.03,"2017All Efficiency[%]")
XaxisText.SetNDC()
XaxisText.SetTextFont(52)
XaxisText.SetTextAlign(11)
XaxisText.SetTextSize(0.035)
YaxisText = TLatex(0.01,0.88,"#splitline{#splitline{2018A}{Efficiency}}{[%]}")
YaxisText.SetNDC()
YaxisText.SetTextFont(52)
YaxisText.SetTextAlign(11)
YaxisText.SetTextSize(0.035)
#YaxisText.SetTextAngle(270)

leg = TLegend(0.25, 0.75, 0.5, 0.85)
#leg.SetHeader("","C")
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.AddEntry(GBarrel, "Barrel", "lep")
leg.AddEntry(GEndcap, "Endcap", "lep")
leg.Draw("same")

XaxisText.Draw("same")
YaxisText.Draw("same")
#Titlename.Draw("same")

'''
n = 3000
i = 0

prev = []
latt = []

for line1 in open(fName1).readlines():
	#rollName1, eff1, Son1, Mother1 = line1.strip().split()
	rollName1, eff1 = line1.strip().split()
	disk1, ring1, channel1, roll1 = rollName1.split('_')


	if float(eff1) < 70. :
		print rollName1


	for line2 in open(fName2).readlines():
		#rollName2, eff2, Son2, Mother2 = line2.strip().split()
		rollName2, eff2 = line2.strip().split()
		disk2, ring2, channel2, roll2 = rollName2.split('_')
		
		if rollName1 == rollName2:
			prev.append(float(eff1))
			latt.append(float(eff2))
			i += 1
			if i == 20 : print prev

g0 = TGraph(n, prev, latt)
c1 = TCanvas("c1","compare",200,10,500,300)
g0.Draw()
'''
