#!/usr/bin/env python3
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Union
import argparse
from bs4 import BeautifulSoup
import tqdm


DEFAULT_URL = 'https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions22/'


def list_golden_json_urls(url: str) -> list[str]:
    with urllib.request.urlopen(url) as response:
        soup = BeautifulSoup(response.read(), 'lxml')

    if not url.endswith('/'):
        url += '/'

    output: list[str] = []
    for each in soup.find_all('a'):
        href = each.get('href')
        if href.startswith('Cert') and href.endswith('_Golden.json'):
            output.append(urllib.parse.urljoin(url, href))
    return output


def download_cert(url: str, output_path: Union[str, Path]) -> None:
    with urllib.request.urlopen(url) as response:
        data = response.read().decode('utf-8')

    with open(output_path, 'w') as stream:
        stream.write(data)


def run(url: str, output_dir: Path) -> None:
    golden_json_url_list = list_golden_json_urls(url)
    for each in (progress_bar := tqdm.tqdm(golden_json_url_list)):
        href = each.split('/')[-1]
        progress_bar.set_description(f'downloading {each}')
        output_path = output_dir / href
        download_cert(url=each, output_path=output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f'example: download-cert.py {DEFAULT_URL} -o ${{CMSSW_BASE}}/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/data/LumiJSON'
    )
    parser.add_argument('url', type=str,
                        help='a url of a web page containing cert files')
    parser.add_argument('-o', '--output-dir', type=Path, default=Path.cwd(),
                        help='an output directory. it will be created if not '
                             'exists. the default is the current directory')
    args = parser.parse_args()

    if not args.output_dir.exists():
        print(f'created directory: {args.output_dir}')
        args.output_dir.mkdir(parents=True)

    run(**vars(args))


if __name__ == '__main__':
    main()
