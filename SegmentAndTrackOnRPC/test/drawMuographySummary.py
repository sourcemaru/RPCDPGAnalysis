#!/usr/bin/env python

run = 274442
padW = 500

from ROOT import *
from array import array
gStyle.SetOptStat(0)

f = TFile("hist.root")

hBarrel = [
  ("Barrel/hZPhiExpBarrel1_1", "Barrel/hZPhiExpOnRPCBarrel1_1"),
  ("Barrel/hZPhiExpBarrel2_1", "Barrel/hZPhiExpOnRPCBarrel2_1"),
  ("Barrel/hZPhiExpBarrel3_1", "Barrel/hZPhiExpOnRPCBarrel3_1"),
  ("Barrel/hZPhiExpBarrel1_2", "Barrel/hZPhiExpOnRPCBarrel1_2"),
  ("Barrel/hZPhiExpBarrel2_2", "Barrel/hZPhiExpOnRPCBarrel2_2"),
  ("Barrel/hZPhiExpBarrel4_1", "Barrel/hZPhiExpOnRPCBarrel4_1"),
]
hEndcapP = [
  ("Endcap+/Disk_1/hXYExpDisk_1", "Endcap+/Disk_1/hXYExpOnRPCDisk_1"),
  ("Endcap+/Disk_2/hXYExpDisk_2", "Endcap+/Disk_2/hXYExpOnRPCDisk_2"),
  ("Endcap+/Disk_3/hXYExpDisk_3", "Endcap+/Disk_3/hXYExpOnRPCDisk_3"),
  ("Endcap+/Disk_4/hXYExpDisk_4", "Endcap+/Disk_4/hXYExpOnRPCDisk_4"),
]
hEndcapN = [
  ("Endcap-/Disk_-1/hXYExpDisk_-1", "Endcap-/Disk_-1/hXYExpOnRPCDisk_-1"),
  ("Endcap-/Disk_-2/hXYExpDisk_-2", "Endcap-/Disk_-2/hXYExpOnRPCDisk_-2"),
  ("Endcap-/Disk_-3/hXYExpDisk_-3", "Endcap-/Disk_-3/hXYExpOnRPCDisk_-3"),
  ("Endcap-/Disk_-4/hXYExpDisk_-4", "Endcap-/Disk_-4/hXYExpOnRPCDisk_-4"),
]

hDens, hEffs = [], []
maxMeanZ, maxZ = 0.0, 0.0

gROOT.ProcessLine("""struct customDivide { customDivide(const TH2D* h1, const TH2D* h2, TH2D* heff) {
  for ( int i=0, n=(h1->GetNbinsX()+1)*(h1->GetNbinsY()); i<n; ++i ) {
    const double den = h1->GetBinContent(i);
    const double num = h2->GetBinContent(i);
    heff->SetBinContent(i, den == 0 ? -1 : num/den);
  }
}};""")

cBDen = TCanvas("cBDen", "Barrel statistics", 3*padW, 2*padW)
cBDen.Divide(3,2)
cBEff = TCanvas("cBEff", "Barrel efficiency", 3*padW, 2*padW)
cBEff.Divide(3,2)
for i, (hDenName, hNumName) in enumerate(hBarrel):
    hDen = f.Get("rpcPoint/Run%d/%s" % (run, hDenName))
    hNum = f.Get("rpcPoint/Run%d/%s" % (run, hNumName))
    hDens.append(hDen)
    hEff = hNum.Clone()
    hEff.Reset()
    hEff.SetTitle(hEff.GetTitle().replace("Expected Points matched to RPC in", "Efficiency of"))
    hEffs.append(hEff)

    cBDen.cd(i+1)
    hDen.Draw("COLZ")

    sumZ = 0
    nBins = (hDen.GetNbinsX()+2)*(hDen.GetNbinsY()+2)
    customDivide(hDen, hNum, hEff)
    maxMeanZ = max(hDen.GetEntries()/nBins, maxMeanZ)
    #hEff.Divide(hNum, hDen)

    cBEff.cd(i+1)
    hEff.Draw("COLZ")

cEPDen = TCanvas("cEPDen", "Endcap+ statistics", 2*padW, 2*padW)
cEPDen.Divide(2,2)
cEPEff = TCanvas("cEPEff", "Endcap+ efficiency", 2*padW, 2*padW)
cEPEff.Divide(2,2)
for i, (hDenName, hNumName) in enumerate(hEndcapP):
    hDen = f.Get("rpcPoint/Run%d/%s" % (run, hDenName))
    hNum = f.Get("rpcPoint/Run%d/%s" % (run, hNumName))
    hDens.append(hDen)
    hEff = hNum.Clone()
    hEff.Reset()
    hEff.SetTitle(hEff.GetTitle().replace("Expected points matched to RPC in", "Efficiency of"))
    hEffs.append(hEff)

    cEPDen.cd(i+1)
    hDen.Draw("COLZ")
    hDen.GetXaxis().SetRangeUser(-800, 800)
    hDen.GetYaxis().SetRangeUser(-800, 800)

    sumZ = 0
    nBins = (hDen.GetNbinsX()+2)*(hDen.GetNbinsY()+2)
    customDivide(hDen, hNum, hEff)
    maxMeanZ = max(hDen.GetEntries()/nBins, maxMeanZ)
    #hEff.Divide(hNum, hDen)

    cEPEff.cd(i+1)
    hEff.Draw("COLZ")
    hEff.GetXaxis().SetRangeUser(-800, 800)
    hEff.GetYaxis().SetRangeUser(-800, 800)

cENDen = TCanvas("cENDen", "Endcap- statistics", 2*padW, 2*padW)
cENDen.Divide(2,2)
cENEff = TCanvas("cENEff", "Endcap- efficiency", 2*padW, 2*padW)
cENEff.Divide(2,2)
for i, (hDenName, hNumName) in enumerate(hEndcapN):
    hDen = f.Get("rpcPoint/Run%d/%s" % (run, hDenName))
    hNum = f.Get("rpcPoint/Run%d/%s" % (run, hNumName))
    hDens.append(hDen)
    hEff = hNum.Clone()
    hEff.Reset()
    hEff.SetTitle(hEff.GetTitle().replace("Expected points matched to RPC in", "Efficiency of"))
    hEffs.append(hEff)

    cENDen.cd(i+1)
    hDen.Draw("COLZ")
    hDen.GetXaxis().SetRangeUser(-800, 800)
    hDen.GetYaxis().SetRangeUser(-800, 800)

    sumZ = 0
    nBins = (hDen.GetNbinsX()+2)*(hDen.GetNbinsY()+2)
    customDivide(hDen, hNum, hEff)
    maxMeanZ = max(hDen.GetEntries()/nBins, maxMeanZ)
    #hEff.Divide(hNum, hDen)

    cENEff.cd(i+1)
    hEff.Draw("COLZ")
    hEff.GetXaxis().SetRangeUser(-800, 800)
    hEff.GetYaxis().SetRangeUser(-800, 800)

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
    c.Print("%s.png" % c.GetName())

rpcPalette = array('i', [kBlack,632,632,632,632,632,632,632,807,400,416,kBlue])
levels = array('d', [0.1*i+1e-9 for i in range(-1, 12)])
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
    c.Print("%s.png" % c.GetName())
