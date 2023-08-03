#!/usr/bin/env python3
import math
import ROOT

class RPCDetId:
    def __init__(self, name, rawId=0):
        self.name = name[:]
        #self.rawId = int(rawId)

        self.region = None
        self.sector, self.station = None, None
        self.roll = None
        self.wheel, self.layer = None, None
        self.disk, self.ring, self.channel = None, None, None

        if name.startswith("W"):
            self.region = 0
            w, sn, sector, roll = name.split('_')

            self.wheel = int(w[1:])
            self.sector = int(sector[1:].lstrip('0'))
            self.roll = roll[0]

            self.station = int(sn[2])
            if self.station <= 2:
                self.layer = (self.station-1)*2+1
                if 'out' in sn: self.layer += 1
            else:
                self.layer = 4+(self.station-2)
                self.roll += sn[3:] ## There are suffix, +, -, ++, --, etc

        elif name.startswith("RE"):
            d, r, ch, self.roll = name.split('_')
            d, self.ring, self.channel = int(d[2:]), int(r[1:]), int(ch[2:])

            self.disk = abs(d)
            self.region = d/self.disk

    def __eq__(self, another):
        for attr in ['region', 'sector', 'station', 'roll', 'wheel', 'layer', 'disk', 'ring', 'channel']:
            if not hasattr(another, attr) or getattr(self, attr) != getattr(another, attr): return False
        return True

    def __hash__(self):
        l = []
        for attr in ['region', 'sector', 'station', 'roll', 'wheel', 'layer', 'disk', 'ring', 'channel']:
            l.append(getattr(self, attr))
        return hash(tuple(l))

    def isBarrel(self):
        return self.region == 0

    def isEndcap(self):
        return abs(self.region) == 1

    def isIRPC(self):
        return self.isEndcap() and self.disk in (3,4) and self.ring == 1

class RPCShapes:
    def __init__(self, fileName="rpcGeom.txt", prefix=""):
        self.shapes = {}
        self.h2ByWheelDisk = {}
        self.binToId = {}
        self.idToBin = {}
        self.padLabels = {}
        self.padLabels2 = {}
        self.prefix = prefix
        pi = math.pi

        for l in open(fileName).readlines():
            if l.startswith('#'): continue
            l = l.strip().split()
            if len(l) != 15: continue

            name, rawId, area = l[0], int(l[1]), float(l[2])
            xs, ys, zs = [[float(l[3:][3*i+j]) for i in range(4)] for j in range(3)]
            rpcId = RPCDetId(name)#, rawId)

            ptss = []
            if rpcId.isEndcap():
                ptss = [zip(xs, ys)]
                ptss[0].append([xs[0], ys[0]])
            elif rpcId.isBarrel():
                phis = []
                for y, x in zip(ys, xs):
                    phi = math.atan2(y,x)
                    if phi < 0: phi += 2*pi
                    phis.append(phi)
                if abs(phis[0]-phis[2]) > pi: ## Regularize the shape in phi
                    for i, phi in enumerate(phis):
                        if phi > pi: phis[i] -= 2*pi

                ptss = [zip(zs, phis)]
                ptss[0].append([zs[0], phis[0]])
            else: continue

            shape = ROOT.TMultiGraph(name, name)
            for pts in ptss:
                grp = ROOT.TGraph()
                grp.SetTitle(name)
                grp.SetLineColor(ROOT.kGray+2)
                grp.SetLineWidth(1)
                grp.SetEditable(False)
                for i, (x, y) in enumerate(pts): grp.SetPoint(i, x, y)
                shape.Add(grp)

            self.shapes[rpcId] = shape

        for rpcId, shape in self.shapes.items():
            key = ""
            #if rpcId.isBarrel(): key = "W%+d" % rpcId.wheel
            if rpcId.isBarrel(): key = ('_'.join(rpcId.name.split('_')[1:2])).strip('+-')
            elif rpcId.isEndcap(): key = "RE%+d" % (rpcId.region*rpcId.disk)
            else: continue

            if key not in self.h2ByWheelDisk:
                if rpcId.isBarrel(): self.h2ByWheelDisk[key] = ROOT.TH2Poly("h"+self.prefix+key, key, -800, 800, -0.5, 7)
                else:                self.h2ByWheelDisk[key] = ROOT.TH2Poly("h"+self.prefix+key, key, -800, 800, -800, 800)
            h = self.h2ByWheelDisk[key]
            h.SetMinimum(1e-7)
            b = h.AddBin(shape)+1

            self.binToId[(key, b)] = rpcId
            self.idToBin[rpcId] = (key, b)

    def buildCanvas(self, canvases=[], drawOpt="COLZ"):
        w = 300
        pi = math.pi

        pads = {"RB":[], "RE+":[], "RE-":[]}
        if len(canvases) != 3:
            cB = ROOT.TCanvas("c%sRB" % self.prefix, "%s Barrel" % self.prefix, w*3, w*2)
            cEP = ROOT.TCanvas("c%sREP" % self.prefix, "%s Endcap+" % self.prefix, w*2, w*2)
            cEN = ROOT.TCanvas("c%sREN" % self.prefix, "%s Endcap-" % self.prefix, w*2, w*2)

            for c in cB, cEP, cEN:
                    c.SetFillColor(0)
                    c.SetFrameFillStyle(0)
                    c.SetFrameBorderMode(0)
        else:
            cEN, cB, cEP = canvases

        cB.Divide(3,2)
        #for i, key in enumerate(sorted([x for x in self.h2ByWheelDisk.keys() if x.startswith("W")], key=lambda x: int(x[1:]))):
        barrelLayers = ["RB1in", "RB1out", "RB2in", "RB2out", "RB3", "RB4"]
        for i, key in enumerate(sorted([x for x in self.h2ByWheelDisk.keys() if x.startswith("RB")], key=lambda x: barrelLayers.index(x))):
            pad = cB.cd(i+1)
            pad.SetBorderMode(0)
            pad.SetBorderSize(2)
            pad.SetLeftMargin(0.11)
            pad.SetRightMargin(0.13)
            pad.SetTopMargin(0.08)
            pad.SetBottomMargin(0.12)

            frame = pad.DrawFrame(-800, -0.5, 800, 7)
            frame.GetXaxis().SetTitle("z [cm]")
            frame.GetYaxis().SetTitle("#phi [radian]")
            frame.GetYaxis().SetTitleOffset(0.9)
            self.h2ByWheelDisk[key].Draw(drawOpt+"same")
            pads["RB"].append(pad)
            for b in range(self.h2ByWheelDisk[key].GetNumberOfBins()):
                self.shapes[self.binToId[(key, b+1)]].Draw()
            if barrelLayers[i] not in self.padLabels:
                l = ROOT.TText()
                l.SetNDC()
                l.SetText(pad.GetLeftMargin()+0.07, 1-pad.GetTopMargin()-0.04, barrelLayers[i])
                l.SetTextAlign(13)
                ll = ROOT.TLatex(pad.GetLeftMargin()+0.01,1-pad.GetTopMargin()+0.01,"CMS #bf{#it{Preliminary}}")
                ll.SetNDC()
                ll.SetTextFont(62)
                ll.SetTextAlign(11)
                ll.SetTextSize(0.05)
                self.padLabels[barrelLayers[i]] = l
                self.padLabels2[barrelLayers[i]] = ll
            self.padLabels[barrelLayers[i]].Draw()
            self.padLabels2[barrelLayers[i]].Draw()

        cEP.Divide(2,2)
        for i, key in enumerate(sorted([x for x in self.h2ByWheelDisk.keys() if x.startswith("RE+")])):
            pad = cEP.cd(i+1)
            pad.SetBorderMode(0)
            pad.SetBorderSize(2)
            pad.SetLeftMargin(0.15)
            pad.SetRightMargin(0.13)
            pad.SetTopMargin(0.10)
            pad.SetBottomMargin(0.13)

            frame = pad.DrawFrame(-800, -800, 800, 800)
            frame.GetXaxis().SetTitle("x [cm]")
            frame.GetYaxis().SetTitle("y [cm]")
            frame.GetYaxis().SetTitleOffset(1.2)
            self.h2ByWheelDisk[key].Draw(drawOpt+"same")
            pads["RE+"].append(pad)
            for b in range(self.h2ByWheelDisk[key].GetNumberOfBins()):
                self.shapes[self.binToId[(key, b+1)]].Draw()
            if "RE+%d" % (i+1) not in self.padLabels:
                l = ROOT.TText()
                l.SetNDC()
                l.SetText(pad.GetLeftMargin()+0.05, 1-pad.GetTopMargin()-0.05, "RE+%d" % (i+1))
                l.SetTextAlign(13)
                ll = ROOT.TLatex(pad.GetLeftMargin()+0.01,1-pad.GetTopMargin()+0.01,"CMS #bf{#it{Preliminary}}")
                ll.SetNDC()
                ll.SetTextFont(62)
                ll.SetTextAlign(11)
                ll.SetTextSize(0.05)
                self.padLabels["RE+%d" % (i+1)] = l
                self.padLabels2["RE+%d" % (i+1)] = ll
            self.padLabels["RE+%d" % (i+1)].Draw()
            self.padLabels2["RE+%d" % (i+1)].Draw()

        cEN.Divide(2,2)
        for i, key in enumerate(sorted([x for x in self.h2ByWheelDisk.keys() if x.startswith("RE-")])):
            pad = cEN.cd(i+1)
            pad.SetBorderMode(0)
            pad.SetBorderSize(2)
            pad.SetLeftMargin(0.15)
            pad.SetRightMargin(0.13)
            pad.SetTopMargin(0.10)
            pad.SetBottomMargin(0.13)

            frame = pad.DrawFrame(-800, -800, 800, 800)
            frame.GetXaxis().SetTitle("x [cm]")
            frame.GetYaxis().SetTitle("y [cm]")
            frame.GetYaxis().SetTitleOffset(1.2)
            self.h2ByWheelDisk[key].Draw(drawOpt+"same")
            pads["RE-"].append(pad)
            for b in range(self.h2ByWheelDisk[key].GetNumberOfBins()):
                self.shapes[self.binToId[(key, b+1)]].Draw()
            if "RE-%d" % (i+1) not in self.padLabels:
                l = ROOT.TText()
                l.SetNDC()
                l.SetText(pad.GetLeftMargin()+0.05, 1-pad.GetTopMargin()-0.05, "RE-%d" % (i+1))
                l.SetTextAlign(13)
                ll = ROOT.TLatex(pad.GetLeftMargin()+0.01,1-pad.GetTopMargin()+0.01,"CMS #bf{#it{Preliminary}}")
                ll.SetNDC()
                ll.SetTextFont(62)
                ll.SetTextAlign(11)
                ll.SetTextSize(0.05)
                self.padLabels["RE-%d" % (i+1)] = l
                self.padLabels2["RE-%d" % (i+1)] = ll
            self.padLabels["RE-%d" % (i+1)].Draw()
            self.padLabels2["RE-%d" % (i+1)].Draw()

        return [cB, cEP, cEN], pads
