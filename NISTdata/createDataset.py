import json
import h5py
import numpy as np

name = 'X-ray_mass_absorption_coefficients.hdf5'

with open('table1.json') as f:
    table1 = json.load(f)[0]
with open('table3.json') as f:
    table3 = dict(next(iter(i.items())) for i in json.load(f))

with h5py.File(name) as f:
    for z, attrs in table1.items():
        mu = [[np.float64(x) for x in row] for row in table3[z]]
        dset = f.create_dataset(attrs['symbol'],
                                data=np.asarray(mu))
        dset.attrs['name'] = attrs['name']
        dset.attrs['Z'] = np.int8(z)
        for key in ['Z/A', 'density [g/cm^3]']:
            dset.attrs[key] = np.float64(attrs[key])
