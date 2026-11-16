import importlib.util
import json
import pathlib
import tempfile
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "verify-pages.py"
spec = importlib.util.spec_from_file_location("verify_pages", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class PublicationContract(unittest.TestCase):
    def setUp(self):
        self.site = "https://example.invalid/sefa/"
        self.assets = {name: name.encode() for name in mod.FILES}
        self.manifest = {"schema":"sefa-release-v1","commit":"a"*40,
                         "files":{name:mod.digest(data) for name,data in self.assets.items()}}
        self.live = {self.site + ("release-manifest.json"): json.dumps(self.manifest).encode()}
        self.live.update({self.site + ("" if name=="index.html" else name): data for name,data in self.assets.items()})
    def test_exact_bytes(self):
        self.assertTrue(all(x["match"] for x in mod.verify_once(self.site,self.manifest,self.live.__getitem__).values()))
    def test_changed_html(self):
        self.live[self.site] = b"old page"
        self.assertFalse(mod.verify_once(self.site,self.manifest,self.live.__getitem__)["index.html"]["match"])
    def test_stale_release(self):
        self.live[self.site+"release-manifest.json"] = json.dumps({**self.manifest,"commit":"b"*40}).encode()
        with self.assertRaises(ValueError):
            mod.verify_once(self.site,self.manifest,self.live.__getitem__)
    def test_unexpected_file(self):
        wrong = {**self.manifest,"files":{**self.manifest["files"],"private.csv":"0"*64}}
        with self.assertRaises(ValueError):
            mod.validate(wrong)
    def test_missing_file(self):
        wrong = {**self.manifest,"files":{k:v for k,v in self.manifest["files"].items() if k!="index.html"}}
        with self.assertRaises(ValueError):
            mod.validate(wrong)
    def test_no_success_without_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = pathlib.Path(tmp)/"report.json"
            self.assertFalse(mod.verify(self.site,self.manifest,report,max_seconds=0))
            self.assertEqual(json.loads(report.read_text())["status"],"FAIL")

if __name__ == "__main__":
    unittest.main()
