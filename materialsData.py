import h5py
import numpy as np

DATABASE = "NISTdata/X-ray_mass_absorption_coefficients.hdf5"


def getElementData(element):
    '''
    Returns the NIST data for the specified element
    '''
    f = h5py.File(DATABASE, 'r')
    elementData = f[element]
    return elementData


def getMassAttenCoeff(element, energy):
    '''
    returns the mass atten coeff for an element at a specified energy
    '''
    data = getElementData(element)
    if energy in data[:, 0]:
        row = np.where(data[:, 0] == energy)
        return float(data[row, 1])
    else:
        print("interpolation required")
        data = np.interp(energy, data[:, 0], data[:, 1])
        return data


if __name__ == "__main__":
    print("Cu beam: ", getMassAttenCoeff('Cu', 0.02))
    print("Cu Cu: ", getMassAttenCoeff('Cu', 0.008048))
    print("Cu Pt: ", getMassAttenCoeff('Cu', 0.009439))
    print("Pt beam: ", getMassAttenCoeff('Pt', 0.02))
    print("Pt Cu: ", getMassAttenCoeff('Pt', 0.008048))
    print("Pt Pt: ", getMassAttenCoeff('Pt', 0.009439))
