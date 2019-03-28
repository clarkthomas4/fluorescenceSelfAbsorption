###############################################################################
# This file is a modification of code released as part of the following:
# Database of X-ray mass attenuation coefficients scraped from NIST database,
# using code by Sébastien Brisard, available at
# https://sbrisard.github.io/posts/20170531-Scrapy-ing_the_NIST_X-ray_Attenuation_Databases.html
#
# BSD 3-Clause License
#
# Copyright (c) 2017, Sébastien Brisard
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
###############################################################################


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
