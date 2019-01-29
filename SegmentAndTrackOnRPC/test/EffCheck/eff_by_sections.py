#!/usr/bin/env python
import sys, os
from ROOT import *
gStyle.SetOptStat(0)

if len(sys.argv) < 2:
	print "Usage: python -i %s FILENAME.txt" % sys.argv[0]
	sys.exit(1)

fName = sys.argv[1]
numBySectREm3, denBySectREm3 = [0.0]*36, [0.0]*36
numBySectREm4, denBySectREm4 = [0.0]*36, [0.0]*36
numBySectRExx, denBySectRExx = [0.0]*36, [0.0]*36

grpEffREm3 = TGraphAsymmErrors()
grpEffREm4 = TGraphAsymmErrors()
grpEffRExx = TGraphAsymmErrors()

for line in open(fName).readlines():
	rollName, eff, num, den = line.strip().split()
	num, den = float(num), float(den)
	if rollName.startswith('W'): continue

	disk, ring, ch, roll = rollName.split('_')
	ch = int(ch[2:].lstrip('0'))
	ring = int(ring[1:])

	if disk == "RE-3":
		numBySectREm3[ch-1] += num
		denBySectREm3[ch-1] += den
	elif disk == "RE-4":
		numBySectREm4[ch-1] += num
		denBySectREm4[ch-1] += den
	else:
		numBySectRExx[ch-1] += num
		denBySectRExx[ch-1] += den

for ch in range(1, 37):
	numREm3, denREm3 = numBySectREm3[ch-1], denBySectREm3[ch-1]
	numREm4, denREm4 = numBySectREm4[ch-1], denBySectREm4[ch-1]
	numRExx, denRExx = numBySectRExx[ch-1], denBySectRExx[ch-1]

	effREm3 = numREm3/denREm3
	effREm4 = numREm4/denREm4
	effRExx = numRExx/denRExx

	errUpREm3 = TEfficiency.ClopperPearson(denREm3, numREm3, 0.683, True)-effREm3
	errLoREm3 = effREm3-TEfficiency.ClopperPearson(denREm3, numREm3, 0.683, False)
	errUpREm4 = TEfficiency.ClopperPearson(denREm4, numREm4, 0.683, True)-effREm4
	errLoREm4 = effREm4-TEfficiency.ClopperPearson(denREm4, numREm4, 0.683, False)
	errUpRExx = TEfficiency.ClopperPearson(denRExx, numRExx, 0.683, True)-effRExx
	errLoRExx = effRExx-TEfficiency.ClopperPearson(denRExx, numRExx, 0.683, False)

	np = grpEffREm3.GetN()

	grpEffREm3.SetPoint(np, ch, effREm3)
	grpEffREm3.SetPointError(np, 0.5, 0.5, errLoREm3, errUpREm3)
	grpEffREm4.SetPoint(np, ch, effREm4)
	grpEffREm4.SetPointError(np, 0.5, 0.5, errLoREm4, errUpREm4)
	grpEffRExx.SetPoint(np, ch, effRExx)
	grpEffRExx.SetPointError(np, 0.5, 0.5, errLoRExx, errUpRExx)

grpEffREm3.SetLineColor(kBlue+1)
grpEffREm4.SetLineColor(kRed+1)
grpEffRExx.SetLineColor(kBlack)

grpEffREm3.SetLineWidth(2)
grpEffREm4.SetLineWidth(2)
grpEffRExx.SetLineWidth(2)

leg = TLegend(0.7, 0.15, 0.9, 0.3)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.AddEntry(grpEffREm3, "RE-3", "l")
leg.AddEntry(grpEffREm4, "RE-4", "l")
leg.AddEntry(grpEffRExx, "RE others", "l")

c = TCanvas("c", "c", 800, 600)
hFrame = TH1F("hFrame", ";Sector;Efficiency", 36, 0, 37)
hFrame.SetMinimum(0.8)
hFrame.SetMaximum(1.0)
hFrame.Draw()
grpEffREm3.Draw("pz")
grpEffREm4.Draw("pz")
grpEffRExx.Draw("pz")
leg.Draw()
