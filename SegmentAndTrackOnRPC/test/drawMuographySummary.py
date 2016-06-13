#!/usr/bin/env python
from ROOT import *
gStyle.SetOptStat(0)

run=274442

f = TFile("hist.root")

hBarrel = [
  f.Get("rpcPoint/Run%d/Barrel/hZPhiExpBarrel1_1" % run),
  f.Get("rpcPoint/Run%d/Barrel/hZPhiExpBarrel2_1" % run),
  f.Get("rpcPoint/Run%d/Barrel/hZPhiExpBarrel3_1" % run),
  f.Get("rpcPoint/Run%d/Barrel/hZPhiExpBarrel1_2" % run),
  f.Get("rpcPoint/Run%d/Barrel/hZPhiExpBarrel2_2" % run),
  f.Get("rpcPoint/Run%d/Barrel/hZPhiExpBarrel4_1" % run),
]
hEndcapP = [
  f.Get("rpcPoint/Run%d/Endcap+/Disk_1/hXYExpDisk_1" % run),
  f.Get("rpcPoint/Run%d/Endcap+/Disk_2/hXYExpDisk_2" % run),
  f.Get("rpcPoint/Run%d/Endcap+/Disk_3/hXYExpDisk_3" % run),
  f.Get("rpcPoint/Run%d/Endcap+/Disk_4/hXYExpDisk_4" % run),
]
hEndcapN = [
  f.Get("rpcPoint/Run%d/Endcap-/Disk_-1/hXYExpDisk_-1" % run),
  f.Get("rpcPoint/Run%d/Endcap-/Disk_-2/hXYExpDisk_-2" % run),
  f.Get("rpcPoint/Run%d/Endcap-/Disk_-3/hXYExpDisk_-3" % run),
  f.Get("rpcPoint/Run%d/Endcap-/Disk_-4/hXYExpDisk_-4" % run),
]

maxZ = max([h.GetMaximum() for h in hBarrel+hEndcapP+hEndcapN])

cB = TCanvas("cB", "cB", 1200, 800)
cB.Divide(3,2)
for i, h in enumerate(hBarrel):
    cB.cd(i+1)
    h.SetMaximum(maxZ)
    h.Draw("COLZ")

cEP = TCanvas("cEP", "Endcap+", 800, 800)
cEP.Divide(2,2)
for i, h in enumerate(hEndcapP):
    cEP.cd(i+1)
    h.SetMaximum(maxZ)
    h.Draw("COLZ")

cEN = TCanvas("cEN", "Endcap-", 800, 800)
cEN.Divide(2,2)
for i, h in enumerate(hEndcapN):
    cEN.cd(i+1)
    h.SetMaximum(maxZ)
    h.Draw("COLZ")

