#!/usr/bin/env python

run = 0
#padW = 500
padW = 250

from ROOT import *
from array import array
import os, sys
from math import floor
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

f = TFile(sys.argv[1])
fName = os.path.basename(sys.argv[1])
hBarrelDen, hEndcapPDen, hEndcapNDen = [], [], []
hBarrelNum, hEndcapPNum, hEndcapNNum = [], [], []
for hName in [key.GetName() for key in f.GetListOfKeys()]:
    h = f.Get(hName)
    if not h.IsA().InheritsFrom("TH2"): continue

    if hName.endswith("Den"):
        if "Barrel" in hName: hBarrelDen.append(h)
        elif "EndcapP" in hName: hEndcapPDen.append(h)
        elif "EndcapN" in hName: hEndcapNDen.append(h)
    elif hName.endswith("Num"):
        if "Barrel" in hName: hBarrelNum.append(h)
        elif "EndcapP" in hName: hEndcapPNum.append(h)
        elif "EndcapN" in hName: hEndcapNNum.append(h)

gROOT.ProcessLine("""struct customDivide { customDivide(const TH2D* h1, const TH2D* h2, TH2D* heff) {
  for ( int i=0, n=(h1->GetNbinsX()+1)*(h1->GetNbinsY()); i<n; ++i ) {
    const double den = h1->GetBinContent(i);
    const double num = h2->GetBinContent(i);
    heff->SetBinContent(i, den == 0 ? -1 : num/den);
  }
}};""")
gROOT.ProcessLine("""struct effStat { effStat(const TH2D* h/*, const TH1D* heff*/) {
  const int nBins = h->GetNbinsX()*h->GetNbinsY();
  //const double width = h->GetXaxis()->GetBinLowEdge(h->GetNbinsX()+1) - h->GetXaxis()->GetBinLowEdge(1);
  //const double height = h->GetYaxis()->GetBinLowEdge(h->GetNbinsY()+1) - h->GetYaxis()->GetBinLowEdge(1);
  int nTotal = 0, nDead = 0;
  for ( int i=1; i<=h->GetNbinsX(); ++i ) {
    for ( int j=1; j<=h->GetNbinsY(); ++j ) {
      const double y = h->GetBinContent(i, j);
      //heff->Fill(y);
      if ( y >= 0 ) ++nTotal;
      if ( y == 0 ) ++nDead;
    }
  }
  //const double totalArea = width*height*nTotal/nBins/100/100;
  const double deadFrac = 1.0*nDead/nTotal;
  cout << "RPC dead fraction = " << (100.0*deadFrac) << "% at " << h->GetTitle() << " \\n";
}};""")

hDens, hEffs = [], []
maxMeanZ, maxZ = 0.0, 0.0

hBarrel = zip(hBarrelDen, hBarrelNum)
hEndcapP = zip(hEndcapPDen, hEndcapPNum)
hEndcapN = zip(hEndcapNDen, hEndcapNNum)

labels = []

cBDen = TCanvas("cBDen", "Barrel statistics", 3*padW, 2*padW)
cBDen.Divide(3,2)
cBEff = TCanvas("cBEff", "Barrel efficiency", 3*padW, 2*padW)
cBEff.Divide(3,2)
for i, (hDen, hNum) in enumerate(hBarrel):
    hDens.append(hDen)
    hEff = hNum.Clone()
    hEff.Reset()
    hEff.SetTitle(hEff.GetTitle().replace("Expected Points matched to RPC in", "Efficiency of"))
    hEffs.append(hEff)

    detLabel = ""
    if i < 4: detLabel = "RB%d%s" % (i/2+1, ["in", "out"][i%2])
    else: detLabel = "RB%d" % (i-1)
    l = TText()
    l.SetNDC()
    l.SetTextAlign(11)

    pad = cBDen.cd(i+1)
    hDen.Draw("COLZ")
    l.SetText(pad.GetLeftMargin(), 1-pad.GetTopMargin()+0.01, detLabel)
    l.Draw()

    sumZ = 0
    nBins = (hDen.GetNbinsX()+2)*(hDen.GetNbinsY()+2)
    customDivide(hDen, hNum, hEff)
    maxMeanZ = max(hDen.GetEntries()/nBins, maxMeanZ)
    #hEff.Divide(hNum, hDen)

    pad = cBEff.cd(i+1)
    hEff.Draw("COLZ")
    l.SetText(pad.GetLeftMargin(), 1-pad.GetTopMargin()+0.01, detLabel)
    l.Draw()

    labels.append(l)

cEPDen = TCanvas("cEPDen", "Endcap+ statistics", 2*padW, 2*padW)
cEPDen.Divide(2,2)
cEPEff = TCanvas("cEPEff", "Endcap+ efficiency", 2*padW, 2*padW)
cEPEff.Divide(2,2)
for i, (hDen, hNum) in enumerate(hEndcapP):
    hDens.append(hDen)
    hEff = hNum.Clone()
    hEff.Reset()
    hEff.SetTitle(hEff.GetTitle().replace("Expected points matched to RPC in", "Efficiency of"))
    hEffs.append(hEff)

    l = TText()
    l.SetNDC()
    l.SetText(.5, .5, "RE+%d" % (i+1))
    l.SetTextAlign(22)

    cEPDen.cd(i+1)
    hDen.Draw("COLZ")
    hDen.GetXaxis().SetRangeUser(-800, 800)
    hDen.GetYaxis().SetRangeUser(-800, 800)
    l.Draw()

    sumZ = 0
    nBins = (hDen.GetNbinsX()+2)*(hDen.GetNbinsY()+2)
    customDivide(hDen, hNum, hEff)
    maxMeanZ = max(hDen.GetEntries()/nBins, maxMeanZ)
    #hEff.Divide(hNum, hDen)

    cEPEff.cd(i+1)
    hEff.Draw("COLZ")
    hEff.GetXaxis().SetRangeUser(-800, 800)
    hEff.GetYaxis().SetRangeUser(-800, 800)
    l.Draw()

    labels.append(l)

cENDen = TCanvas("cENDen", "Endcap- statistics", 2*padW, 2*padW)
cENDen.Divide(2,2)
cENEff = TCanvas("cENEff", "Endcap- efficiency", 2*padW, 2*padW)
cENEff.Divide(2,2)
for i, (hDen, hNum) in enumerate(hEndcapN):
    hDens.append(hDen)
    hEff = hNum.Clone()
    hEff.Reset()
    hEff.SetTitle(hEff.GetTitle().replace("Expected points matched to RPC in", "Efficiency of"))
    hEffs.append(hEff)

    l = TText()
    l.SetNDC()
    l.SetText(.5, .5, "RE-%d" % (i+1))
    l.SetTextAlign(22)

    cENDen.cd(i+1)
    hDen.Draw("COLZ")
    hDen.GetXaxis().SetRangeUser(-800, 800)
    hDen.GetYaxis().SetRangeUser(-800, 800)
    l.Draw()

    sumZ = 0
    nBins = (hDen.GetNbinsX()+2)*(hDen.GetNbinsY()+2)
    customDivide(hDen, hNum, hEff)
    maxMeanZ = max(hDen.GetEntries()/nBins, maxMeanZ)
    #hEff.Divide(hNum, hDen)

    cENEff.cd(i+1)
    hEff.Draw("COLZ")
    hEff.GetXaxis().SetRangeUser(-800, 800)
    hEff.GetYaxis().SetRangeUser(-800, 800)
    l.Draw()

    labels.append(l)

maxMeanZ = max(1, maxMeanZ)

gStyle.SetPalette(kBird)
for h in hDens:
    h.SetMaximum(maxMeanZ*1.2)
    h.UseCurrentStyle()
for c in (cBDen, cEPDen, cENDen):
    for i in range(10):
        p = c.GetPad(i)
        if p == None: break
        p.Modified()
        p.Update()
    c.Print("%s_%s.png" % (fName[:-5], c.GetName()))
    c.Print("%s_%s.pdf" % (fName[:-5], c.GetName()))

levels     = array('d', [-1    ] + [0.1*i+1e-9 for i in range(8)]
                       +[x+1e-9 for x in [0.75, 0.80, 0.85, 0.90, 0.95, 1.0, 1.1]])
rpcPalette = array('i', [kBlack] + [kRed]*6
                       +[kOrange+7, kOrange-3, kOrange, kYellow, kSpring+8, kSpring+7, kSpring, kBlue])
gStyle.SetPalette(len(rpcPalette), rpcPalette);
for h in hEffs:
    h.SetMaximum(1.1)
    h.SetMinimum(-0.1)
    h.SetContour(len(levels)-1, levels)
    h.UseCurrentStyle()
for c in (cBEff, cEPEff, cENEff):
    for i in range(10):
        p = c.GetPad(i)
        if p == None: break
        p.Modified()
        p.Update()
    c.Print("%s_%s.png" % (fName[:-5], c.GetName()))
    c.Print("%s_%s.pdf" % (fName[:-5], c.GetName()))

fout = TFile("Efficiency.root", "RECREATE")
for h in hEffs:
    effStat(h)
    fout.cd()
    h.Write()
