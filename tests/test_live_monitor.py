import importlib.util
import pathlib
import shutil
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('monitor_live',ROOT/'scripts'/'monitor-live.py')
mon=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mon)

class LiveMonitorContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        for name in mon.verify_pages.FILES:shutil.copyfile(ROOT/name,self.root/name)
    def test_expected_source_hashes(self):
        m=mon.expected_manifest(self.root,'a'*40)
        self.assertEqual(m['commit'],'a'*40)
        self.assertEqual(set(m['files']),mon.verify_pages.FILES)
        self.assertEqual(m['files']['index.html'],mon.verify_pages.digest((ROOT/'index.html').read_bytes()))
    def test_invalid_commit_rejected(self):
        with self.assertRaises(ValueError):mon.expected_manifest(self.root,'not-a-sha')
    def test_missing_asset_rejected(self):
        (self.root/'index.html').unlink()
        with self.assertRaises(ValueError):mon.expected_manifest(self.root,'a'*40)
    def test_changed_data_changes_manifest(self):
        a=mon.expected_manifest(self.root,'a'*40)
        p=self.root/'index.html';p.write_bytes(p.read_bytes()+b'changed')
        b=mon.expected_manifest(self.root,'a'*40)
        self.assertNotEqual(a['files']['index.html'],b['files']['index.html'])

if __name__=='__main__':unittest.main()
