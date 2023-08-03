#!/usr/bin/env python3
import os
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from hist.intervals import clopper_pearson_interval
import ROOT
from ROOT import gROOT
from ROOT import gStyle
from RPCDPGAnalysis.SegmentAndTrackOnRPC.buildLabels import buildLabel
from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import fix_overlay
from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import set_tdr_style
from RPCDPGAnalysis.SegmentAndTrackOnRPC.RPCGeom import RPCDetId
from RPCDPGAnalysis.SegmentAndTrackOnRPC.RPCGeom import RPCShapes


def collect_counts(path_list: list[Path]) -> pd.DataFrame:
    """Collect per-roll counts"""
    # read 'roll_name' column as index
    # aggregate run-by-run counts
    df = sum(pd.read_csv(each, index_col=0) for each in path_list)
    # then convert index to a column
    df = df.reset_index()
    return df


def compute_efficiency(input_df: pd.DataFrame,
                       coverage: float = 0.683
) -> pd.DataFrame:
    """
    """
    den = input_df.denominator.to_numpy()
    num = input_df.numerator.to_numpy()
    eff = np.divide(num, den, out=np.zeros_like(den, dtype=np.float64),
                    where=(den != 0))
    # lower and upper bounds
    eff_lo, eff_hi = clopper_pearson_interval(num, den, coverage=coverage)
    # lower and upper error bars
    err_lo = eff - eff_lo
    err_hi = eff_hi - eff

    return pd.DataFrame({
        'roll_name': input_df.roll_name,
        'efficiency': eff,
        'err_low': err_lo,
        'err_high': err_hi,
        'denominator': den,
    })


def set_style():
    set_tdr_style() # type: ignore
    gStyle.SetOptStat(0)
    gStyle.SetPadTopMargin(0.07)
    gStyle.SetPadLeftMargin(0.12)
    gStyle.SetPadRightMargin(0.048)
    gStyle.SetPadBottomMargin(0.12)
    gStyle.SetTitleSize(0.06, "X");
    gStyle.SetTitleSize(0.06, "Y");


# FIXMXE rename
def plot_geom(df_eff: pd.DataFrame,
              output_dir: Path,
              era: str,
              min_denominator: int = 100,
              output_suffix_list: list[str] = ['.png', '.pdf', '.C']
):
    ###########################################################################
    cmssw_base = Path(os.environ["CMSSW_BASE"])
    rpc_shape_path = cmssw_base / "src/RPCDPGAnalysis/SegmentAndTrackOnRPC/data/rpcGeom.txt"
    rpc_shapes = RPCShapes(rpc_shape_path)
    shape_canvas_list, shape_pads = rpc_shapes.buildCanvas()

    # init
    for key, bin in rpc_shapes.idToBin.values():
        rpc_shapes.h2ByWheelDisk[key].SetBinContent(bin, -1)

    for _, row in df_eff.iterrows():
        rpc_id = RPCDetId(row.roll_name)
        try:
            key, bin = rpc_shapes.idToBin[rpc_id]
        except:
            print(f'RPCDetId not found from {rpc_id}')
        # FIXME
        if row.denominator <= min_denominator:
            # TODO warnings.warn
            # warnings.warn(f"{rpc_id} does not pass the minimum denominator.")
            continue
        rpc_shapes.h2ByWheelDisk[key].SetBinContent(bin, 100 * row.efficiency)

    # FIXME
    levels = np.array([-1] + [10. * i + 1e-9 for i in range(8)] + [100 * x + 1e-9 for x in [0.75, 0.80, 0.85, 0.90, 0.95, 1.0, 1.1]], dtype=np.float64)
    for hist in rpc_shapes.h2ByWheelDisk.values():
        hist.SetMinimum(0 - 1e-9)
        hist.SetMaximum(100)
        hist.SetContour(len(levels) - 1, levels)

    for pad_list in shape_pads.values():
        for pad in pad_list:
            pad.Modified()
            pad.Update()

    for canvas in shape_canvas_list:
        canvas.Modified()
        canvas.Update()

        output_path = output_dir / f'{era}_{canvas.GetName()}'
        for suffix in output_suffix_list:
            canvas.Print(str(output_path.with_suffix(suffix)))


def plot_efficiency(df_eff: pd.DataFrame,
                    output_dir: Path,
                    era: str,
                    rpc_mode: bool = True,
                    bin_width: float = 0.5,
                    xmin: float = 70.5,
                    xmax: float = 100.0,
                    blacklist: list[str] = [],
                    min_denominator: int = 100,
                    output_suffix_list: list[str] = ['.png', '.pdf', '.C']
) -> None:
    """
    """
    output_path = output_dir / f'eff_{era}.root'
    output_file = ROOT.TFile(str(output_path), 'RECREATE')

    ch_title = "Rolls" if rpc_mode else 'Chambers'

    nbin = int((xmax - xmin) / bin_width)
    h_eff_list = [
        ROOT.TH1F(f"hEff{key}",
                  f"{key};Efficiency [%];Number of {ch_title}",
                  nbin + 1,
                  xmin,
                  xmax + bin_width)
        for key in ['Barrel', 'Endcap']
    ]
    for each in h_eff_list:
        each.SetDirectory(output_file)

    canvas_list = [
        ROOT.TCanvas(f"c{key}", f"c{key}", 485, 176, 800, 600)
        for key in ['Barrel', 'Endcap']
    ]
    h_eff_list[0].SetFillColor(30)
    h_eff_list[1].SetFillColor(38)
    h_eff_list[0].SetLineColor(ROOT.TColor.GetColor("#007700")) # moth green
    h_eff_list[1].SetLineColor(ROOT.TColor.GetColor("#000099")) # a kind of dark blue

    allowlist_mask = df_eff.roll_name.apply(lambda each: each not in blacklist)
    min_den_mask = df_eff.denominator > min_denominator
    good_roll_mask = allowlist_mask & min_den_mask

    barrel_mask = df_eff.roll_name.apply(lambda each: each.startswith('W')) # FIXME
    endcap_mask = df_eff.roll_name.apply(lambda each: each.startswith('RE')) # FIXME

    # percentage
    eff_list = [
        100 * df_eff[good_roll_mask & barrel_mask].efficiency.to_numpy(),
        100 * df_eff[good_roll_mask & endcap_mask].efficiency.to_numpy(),
    ]

    ###########################################################################
    #
    ###########################################################################

    # keep objects in memory to avoid gc
    objs = []

    for h_eff, eff_arr, canvas in zip(h_eff_list, eff_list, canvas_list):
        canvas.cd()

        h_eff.GetYaxis().SetNdivisions(505)
        h_eff.GetYaxis().SetTitleOffset(1.0)

        # pass nullptr to 3rd argument, indicating all weights are 1
        h_eff.FillN(len(eff_arr), eff_arr, ROOT.nullptr)

        eff_nonzero_arr = eff_arr[eff_arr != 0]
        eff_over_70_arr = eff_arr[eff_arr > 70]
        eff_over_70 = eff_over_70_arr.mean()

        # header
        header = ROOT.TLatex(gStyle.GetPadLeftMargin(),
                             1 - gStyle.GetPadTopMargin() + 0.01,
                             f"RPC Overall Efficiency - {h_eff.GetTitle()}")
        header.SetNDC()
        header.SetTextAlign(ROOT.kHAlignLeft + ROOT.kVAlignBottom)
        header.SetTextFont(42)

        # custom stat panels
        stat_dict = {
            'Entries': f'{int(h_eff.GetEntries()):d}',
            'Mean': f'{eff_nonzero_arr.mean().item():.2f}',
            'RMS': f'{eff_nonzero_arr.std().item():.2f}',
            'Underflow': f'{np.count_nonzero(eff_arr < xmin):d}'
        }

        panel_1 = ROOT.TPaveText(0.53, 0.68, 0.76, 0.85, "brNDC")
        panel_2 = ROOT.TPaveText(0.53, 0.68, 0.76, 0.85, "brNDC")
        for key, value in stat_dict.items():
            panel_1.AddText(key)
            panel_2.AddText(value)

        panel_1.SetBorderSize(0)
        panel_1.SetFillColor(0)
        panel_1.SetFillStyle(0)
        panel_1.SetTextSize(0.04)
        panel_1.SetTextAlign(ROOT.kHAlignLeft)
        panel_1.SetBorderSize(0)
        panel_1.SetTextFont(62)

        panel_2.SetBorderSize(0)
        panel_2.SetFillColor(0)
        panel_2.SetFillStyle(0)
        panel_2.SetTextSize(0.04)
        panel_2.SetTextAlign(ROOT.kHAlignRight + ROOT.kVAlignBottom)
        panel_2.SetBorderSize(0)
        panel_2.SetTextFont(62)

        panel_over_70 = ROOT.TText(0.18, 0.5,
                                   f"Mean (>70%) = {eff_over_70:.2f}%")
        panel_over_70.SetTextSize(0.05)
        panel_over_70.SetTextFont(62)
        panel_over_70.SetNDC()

        h_eff.Draw()
        panel_1.Draw()
        panel_2.Draw()
        panel_over_70.Draw()
        header.Draw()

        # labels
        label_list = buildLabel(era, "inset")
        for label in label_list:
            label.Draw()

        fix_overlay() # type: ignore

        objs += [panel_1, panel_2, panel_over_70, header]
        objs += label_list

    for canvas in canvas_list:
        canvas.cd()

        canvas.SetFillColor(0)

        canvas.SetBorderMode(0) # type: ignore
        canvas.SetBorderSize(2)

        canvas.SetLeftMargin(0.12)
        canvas.SetRightMargin(0.04)
        canvas.SetTopMargin(0.08)
        canvas.SetBottomMargin(0.12)

        canvas.SetFrameFillStyle(0)
        canvas.SetFrameBorderMode(0)
        canvas.SetFrameFillStyle(0)
        canvas.SetFrameBorderMode(0)

        canvas.Modified()
        canvas.Update()
        # write it to output_file
        canvas.Write()

        output_path = output_dir / f'{era}_{canvas.GetName()}'
        for suffix in output_suffix_list:
            canvas.Print(str(output_path.with_suffix(suffix)))

    output_file.Write()
    output_file.Close()

def run(input_dir: Path,
        era: str,
        output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    print('finding input files')
    input_path_list = list(input_dir.glob('*.csv'))

    print(f'collecting per-coll counts from {len(input_path_list)} files')
    df_count = collect_counts(input_path_list)#, output_path)
    df_count_path = output_dir / 'count.csv'
    print(f'writing per-coll counts into {df_count_path}')
    df_count.to_csv(df_count_path)

    print(f'computing per-roll efficiency')
    df_eff = compute_efficiency(df_count)
    df_eff_path = output_dir / 'efficiency.csv'
    print(f'writing per-roll efficiency into {df_eff_path}')
    df_eff.to_csv(df_eff_path)

    print(f'plotting efficiency')
    set_style()
    plot_efficiency(df_eff, output_dir, era=era)
    plot_geom(df_eff, output_dir, era=era)

def main():
    gROOT.SetBatch(True)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-i', '--input-dir', type=Path, required=True, help='Help text')
    parser.add_argument('-o', '--output-dir', default=(Path.cwd() / 'data' / 'efficiency'),
                        type=Path, help='Help text')
    parser.add_argument('--era', type=str, required=True, help='Help text')
    args = parser.parse_args()

    run(**vars(args))

if __name__ == "__main__":
    main()
