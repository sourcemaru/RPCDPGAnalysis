import json
from dataclasses import dataclass
from typing import Optional
from functools import singledispatchmethod
from pathlib import Path
import numpy as np
import awkward as ak
import uproot
import numpy as np
import numpy.typing as npt
import pandas as pd
import uproot.writing
from hist.hist import Hist
from hist.axis import StrCategory
from hist.axis import IntCategory
from RPCDPGAnalysis.NanoAODTnP.RPCGeomServ import get_roll_name


@dataclass
class LumiBlockChecker:
    """
    https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideGoodLumiSectionsJSONFile
    """
    cert: dict[np.uint32, npt.NDArray[np.uint32]]

    @staticmethod
    def _transform_lumi_ranges(lumi: list[tuple[int, int]]
    ) -> npt.NDArray[np.uint32]:
        """
        """
        flat_lumi = np.array(lumi, dtype=np.uint32).flatten()
        # [first, last] to (first, last]
        flat_lumi[::2] -= 1
        return flat_lumi

    @classmethod
    def from_dict(cls, cert: dict[int, list[tuple[int, int]]]):
        flat_cert = {np.uint32(run): cls._transform_lumi_ranges(lumi_ranges)
                     for run, lumi_ranges in cert.items()}
        return cls(flat_cert)

    @classmethod
    def from_json(cls, path):
        with open(path) as stream:
            cert = json.load(stream)
        return cls.from_dict(cert)

    @staticmethod
    def _get_lumi_mask(lumi_arr: npt.NDArray[np.uint32],
                     ranges: npt.NDArray[np.uint32]
    ) -> npt.NDArray[np.bool_]:
        """
        """
        # odd(even) indices indicate good(bad) lumi blocks
        indices = np.searchsorted(ranges, lumi_arr)
        mask = (indices & 0x1).astype(bool)
        return mask

    @singledispatchmethod
    def get_lumi_mask(self, run, lumi: npt.NDArray[np.uint32]):
        raise NotImplementedError(f'expected np.uint32, npt.NDArray[np.uint32]'
                                  f' or int but got {type(run)}')

    @get_lumi_mask.register(int)
    @get_lumi_mask.register(np.uint32)
    def _(self,
          run: np.uint32,
          lumi: npt.NDArray[np.uint32]
    ) -> npt.NDArray[np.bool_]:
        """
        """
        if isinstance(run, int):
            run = np.uint32(run)

        if run in self.cert:
            mask = self._get_lumi_mask(lumi, ranges=self.cert[run])
        else:
            mask = np.full_like(lumi, fill_value=False, dtype=bool)
        return mask

    @get_lumi_mask.register(np.ndarray)
    def _(self,
          run: npt.NDArray[np.uint32],
          lumi: npt.NDArray[np.uint32]
    ) -> npt.NDArray[np.bool_]:
        """
        """
        mask = np.full_like(lumi, fill_value=False, dtype=bool)
        for each in np.unique(run):
            run_mask = run == each
            mask[run_mask] = self.get_lumi_mask(each, lumi[run_mask])
        return mask


def read_nanoaod(path,
                 cert_path: str,
                 treepath: str = 'Events',
                 name: str = 'rpcTnP',
):
    tree = uproot.open(f'{path}:{treepath}')

    aliases = {key.removeprefix(f'{name}_'): key
               for key in tree.keys()
               if key.startswith(name)}
    # number of measurements
    aliases['size'] = f'n{name}'
    expressions = list(aliases.keys()) + ['run', 'luminosityBlock']
    cut = f'(n{name} > 0)'

    data: dict[str, np.ndarray] = tree.arrays(
        expressions=expressions,
        aliases=aliases,
        cut=cut,
        library='np'
    )

    run = data.pop('run')
    lumi_block = data.pop('luminosityBlock')
    size = data.pop('size')

    lumi_block_checker = LumiBlockChecker.from_json(cert_path)
    mask = lumi_block_checker.get_lumi_mask(run, lumi_block)
    data = {key: value[mask] for key, value in data.items()}

    data = {key: np.concatenate(value) for key, value in data.items()}
    data['run'] = np.repeat(run[mask], size[mask])

    return ak.Array(data)


def flatten_nanoaod(input_path: Path,
                    cert_path: Path,
                    geom_path: Path,
                    output_path: Path,
                    name: str = 'rpcTnP',
):
    data = read_nanoaod(
        path=input_path,
        cert_path=cert_path,
        treepath='Events',
        name=name
    )

    name_arr = [get_roll_name(row.region, row.ring, row.station,
                              row.sector, row.layer, row.subsector,
                              row.roll)
                for row in data]
    name_arr = np.array(name_arr)

    geom = pd.read_csv(geom_path)

    with open(cert_path) as stream:
        cert = json.load(stream)

    roll_axis = StrCategory(geom['roll_name'].tolist(), name="Roll")
    run_axis = IntCategory(sorted(map(int, list(cert.keys()))), name="Run")

    h_total = Hist(roll_axis, run_axis) # type: ignore
    h_passed = h_total.copy()

    h_total.fill(name_arr[data.is_fiducial], data.run[data.is_fiducial])
    h_passed.fill(name_arr[data.is_fiducial & data.is_matched].tolist(), data.run[data.is_fiducial & data.is_matched].to_list())

    with uproot.writing.create(output_path) as output_file:
        output_file['tree'] = data
        output_file['total'] = h_total
        output_file['passed'] = h_passed
