"""Offline checks without third-party dependencies; use `python -m unittest discover -s tests -v`."""
import ast
import io
import plistlib
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'app/server.py').read_text()
tree = ast.parse(source)
func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'inspect_ipsw')
module = ast.Module(body=[func], type_ignores=[])
ns = {'zipfile':zipfile, 'plistlib':plistlib}
exec(compile(module, '<ipsw-inspector>', 'exec'),ns)

class OfflineChecks(unittest.TestCase):
    def test_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'sample.ipsw'
            manifest = {'ProductVersion':'26.6.2','ProductBuildVersion':'23G90','SupportedProductTypes':['iPhone18,2'], 'BuildIdentities':[{'Info':{'DeviceClass':'v54ap'}}]}
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('BuildManifest.plist',plistlib.dumps(manifest))
            result=ns['inspect_ipsw'](p)
            self.assertEqual(result['product_version'],'26.6.2')
            self.assertEqual(result['supported_product_types'],['iPhone18,2'])
            self.assertEqual(result['device_classes'],['v54ap'])
            self.assertTrue(result['manifest_found'])
    def test_missing_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample.ipsw'
            with zipfile.ZipFile(p,'w') as z:z.writestr('README','test')
            result=ns['inspect_ipsw'](p)
            self.assertFalse(result['manifest_found'])
    def test_oversized_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample.ipsw'
            with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('BuildManifest.plist','x'*(11*1024*1024))
            with self.assertRaisesRegex(ValueError,'terlalu besar'):ns['inspect_ipsw'](p)
    def test_html_exists(self):
        html=(ROOT/'app/static/index.html').read_text()
        self.assertIn('/api/inspect',html)
        self.assertIn('/api/status',html)

if __name__ == '__main__':unittest.main()
