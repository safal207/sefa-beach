"""Check published GitHub Pages release against the current main source tree."""
import argparse
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verify_pages',ROOT/'scripts'/'verify-pages.py')
verify_pages=importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_pages)

def expected_manifest(root,head):
    if not re.fullmatch(r'[0-9a-f]{40}',head):raise ValueError('Invalid commit SHA')
    files={}
    for name in sorted(verify_pages.FILES):
        p=root/name
        if not p.is_file():raise ValueError('Missing source asset: '+name)
        files[name]=verify_pages.digest(p.read_bytes())
    m={'schema':'sefa-release-v1','commit':head,'files':files}
    verify_pages.validate(m)
    return m

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--site',required=True)
    parser.add_argument('--report',required=True)
    args=parser.parse_args()
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
    expected=expected_manifest(ROOT,head)
    pathlib.Path(args.report).parent.mkdir(parents=True,exist_ok=True)
    print('Expect main Pages release:',head,flush=True)
    return 0 if verify_pages.verify(args.site,expected,args.report,max_seconds=180) else 1

if __name__=='__main__':sys.exit(main())
