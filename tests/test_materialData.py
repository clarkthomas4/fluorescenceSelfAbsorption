import unittest
import materialsData as mD


class TestMD(unittest.TestCase):

    def test_getElement(self):
        elementData = mD.getElementData("Fe")
        self.assertEqual(elementData.name, "/Fe")
        self.assertEqual(elementData.shape, (38, 3))

    def test_getMAC(self):
        self.assertEqual(mD.getMassAttenCoeff('Cu', 0.02), 33.79)
        self.assertEqual(round(mD.getMassAttenCoeff('Pt', 0.008048), 3),
                         196.648)


if __name__ == 'main':
    unittest.main()
