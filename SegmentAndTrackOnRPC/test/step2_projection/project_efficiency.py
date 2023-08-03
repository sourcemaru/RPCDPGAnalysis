#!/usr/bin/env python3
from pathlib import Path
import argparse
import pandas as pd
import tqdm
from ROOT import TFile
from RPCDPGAnalysis.SegmentAndTrackOnRPC.ProjectTHnSparse import THnSparseSelector


def run(input_path: str,
        common_selection: dict[str, tuple[float, float]],
        output_dir: Path,
        hist_path: str
):
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file = TFile(input_path)
    hist = input_file.Get(hist_path)

    selector = THnSparseSelector(hist)

    h_run = selector.Project1D('run', {'isFiducial': (1, 1)})
    run_list = [int(h_run.GetBinLowEdge(bin))
                for bin in range(1, 1 + h_run.GetNbinsX())
                if h_run.GetBinContent(bin) > 0]

    h_roll_name = selector.Project1D("roll_name", {}, copyAxisLabel=True)
    roll_name_list = [(bin, h_roll_name.GetXaxis().GetBinLabel(bin))
                      for bin in range(0, 2 + h_roll_name.GetNbinsX())
                      if h_roll_name.GetXaxis().GetBinLabel(bin) != ""]

    # TODO multiprocessing
    for run in (progress_bar := tqdm.tqdm(run_list)):
        progress_bar.set_description(f'Processing {run=}')

        selection = common_selection | {'run': (run, run)}

        den_selection = selection
        num_selection = selection | {'isMatched': (1, 1)}

        h_den = selector.Project1D('roll_name', den_selection, suffix='_den')
        h_num = selector.Project1D('roll_name', num_selection, suffix='_num')

        count = {name: [0, 0] for _, name in roll_name_list}
        for bin, name in roll_name_list:
            den = h_den.GetBinContent(bin)
            num = h_num.GetBinContent(bin)

            count[name][0] += int(den)
            count[name][1] += int(num)

        h_den.Delete()
        h_num.Delete()

        df = pd.DataFrame(
            [{'roll_name': name, 'denominator': den, 'numerator': num}
            for name, (den, num) in count.items()]
        )
        df.to_csv(output_dir / f'run-{run}.csv', index=False)


def main():
    parser = argparse.ArgumentParser(
    )
    parser.add_argument('-i', '--input-path', type=str, required=True,
                        help='input root file')
    parser.add_argument('--hist-path', type=str,
                        default='muonHitFromTrackerMuonAnalyzer/hInfo',
                        help='path to histogram')
    parser.add_argument('-o', '--output-dir', type=Path,
                        default=(Path.cwd() / 'data' / 'count'),
                        help='output directory')
    args = parser.parse_args()

    common_selection = {
        'isFiducial': (1.0, 1.0)
    }

    run(args.input_path, common_selection, args.output_dir,
        hist_path=args.hist_path)



if __name__ == "__main__":
    main()
