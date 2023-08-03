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

hFrame1 = TH1F("Barrel","Comp;Cls;#",6,0,6)
hFrame2 = TH1F("Endcap","Comp;Cls;#",6,0,6)

hFrame1.GetXaxis().SetLabelSize(0.05)
hFrame1.GetXaxis().SetLabelOffset(0.03)
hFrame1.GetXaxis().SetTitle("Mean Cluster size")
hFrame1.GetXaxis().SetTitleSize(0.04)
hFrame1.GetXaxis().SetNdivisions(505)
hFrame1.GetXaxis().SetTitleOffset(1.35)

hFrame1.GetYaxis().SetLabelSize(0.05)
hFrame1.GetYaxis().SetTitle("Normalized")
hFrame1.GetYaxis().SetNdivisions(505)
hFrame1.GetYaxis().SetTitleSize(0.04)
hFrame1.GetYaxis().SetTitleOffset(1.85)

hFrame2.GetXaxis().SetLabelSize(0.05)
hFrame2.GetXaxis().SetLabelOffset(0.03)
hFrame2.GetXaxis().SetTitle("Mean Cluster size")
hFrame2.GetXaxis().SetTitleSize(0.04)
hFrame2.GetXaxis().SetNdivisions(505)
hFrame2.GetXaxis().SetTitleOffset(1.35)

hFrame2.GetYaxis().SetLabelSize(0.05)
hFrame2.GetYaxis().SetTitle("Normalized")
hFrame2.GetYaxis().SetNdivisions(505)
hFrame2.GetYaxis().SetTitleSize(0.04)
hFrame2.GetYaxis().SetTitleOffset(1.85)

cHistories = [TCanvas("cHistory%d" % i) for i in range(2)]

runs = []
for line in open(sys.argv[1]).readlines():
    line = line.strip()
    if len(line) == 0 or line.startswith('#'): continue
    name = line.split()[0]

for fName in sys.argv[1:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, Nentries, mean, err2 = line.split()

        Nentries, mean = float(Nentries), float(mean)

        if mean == 0: continue

        if name.startswith("W"): hFrame1.Fill(min(5,mean))
        else: hFrame2.Fill(min(5,mean))

hFrame1.SetFillColor(30)
hFrame1.SetLineColor(TColor.GetColor("#007700"))
hFrame2.SetFillColor(38)
hFrame2.SetLineColor(TColor.GetColor("#000099"))

AllTitlename1 = TLatex(0.2,0.82,"#splitline{CMS}{#bf{#it{Preliminary}}}")
AllTitlename1.SetNDC()
AllTitlename1.SetTextFont(62)
AllTitlename1.SetTextAlign(11)
AllTitlename1.SetTextSize(0.05)

DataTitlename = TLatex(0.95,0.94,"Run2 data, 141.23 fb^{-1} (13TeV)")
DataTitlename.SetNDC()
DataTitlename.SetTextFont(42)
DataTitlename.SetTextAlign(31)
DataTitlename.SetTextSize(0.04)

hFrame1.Scale(1./hFrame1.Integral())
hFrame2.Scale(1./hFrame2.Integral())

'''
DataPro1 = TLatex(0.9,0.4,"Mean : %.4s" %hFrame1.GetMean())
DataPro1.SetNDC()
DataPro1.SetTextFont(42)
DataPro1.SetTextAlign(31)
DataPro1.SetTextSize(0.04)

DataPro2 = TLatex(0.9,0.4,"Mean : %.4s" %hFrame2.GetMean())
DataPro2.SetNDC()
DataPro2.SetTextFont(42)
DataPro2.SetTextAlign(31)
DataPro2.SetTextSize(0.04)
'''
cHistories[0].cd()
hFrame1.Draw("hist")
AllTitlename1.Draw("same")
DataTitlename.Draw("same")
#DataPro1.Draw("same")

cHistories[1].cd()
hFrame2.Draw("hist")
AllTitlename1.Draw("same")
DataTitlename.Draw("same")
#DataPro2.Draw("same")

