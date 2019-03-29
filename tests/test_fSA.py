import unittest
import fluorescenceSelfAbsorption as fSA


class TestFSA(unittest.TestCase):

    def test_scan(self):
        scanDataFile = fSA.jsonDataFile("ScanData.json")
        scanData = scanDataFile.getJsonData()
        scan = fSA.scan(scanDataFile)
        self.assertEqual(scan.getAbsorptionTomo(),
                         scanData["absorptionTomo"]["path"])


if __name__ == 'main':
    unittest.main()
