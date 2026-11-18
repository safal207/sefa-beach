import importlib.util
import pathlib
import shutil
import tempfile
import unittest

mod_path=pathlib.Path(__file__).resolve().parents[1]/'scripts'/'audit-demo-boundary.py'
spec=importlib.util.spec_from_file_location('audit_demo_boundary',mod_path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class DemoBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        for name in ['index.html','revenue-dashboard-local.html','sales-lines-template.csv','sales-context-template.csv','menu-baseline.json']:
            shutil.copyfile(mod.ROOT/name,self.root/name)
    def test_current_demo_boundaries(self):
        self.assertEqual(mod.audit(self.root),[])
    def test_prevent_real_sales_rows(self):
        p=self.root/'sales-lines-template.csv'
        p.write_text(p.read_text()+'real-order,3,1,10,3,0,0,0,0\n')
        self.assertTrue(any('sales data' in x for x in mod.audit(self.root)))
    def test_detect_remote_submission(self):
        p=self.root/'index.html'
        p.write_text(p.read_text()+'<script>fetch("https://tracking.example/collect")</script>')
        self.assertTrue(any('network API' in x for x in mod.audit(self.root)))
    def test_detect_accidental_indexing(self):
        p=self.root/'revenue-dashboard-local.html'
        p.write_text(p.read_text().replace('noindex,nofollow','index,follow'))
        self.assertTrue(any('indexing' in x for x in mod.audit(self.root)))
    def test_detect_external_script(self):
        p=self.root/'index.html'
        p.write_text(p.read_text()+'<script src="https://cdn.invalid/x.js"></script>')
        self.assertTrue(any('external script' in x for x in mod.audit(self.root)))

if __name__=='__main__':unittest.main()
