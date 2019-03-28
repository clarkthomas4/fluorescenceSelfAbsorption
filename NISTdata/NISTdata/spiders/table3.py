###############################################################################
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

import scrapy

BASE_URL = 'http://physics.nist.gov/PhysRefData/XrayMassCoef'
TABLE3_URL = '/'.join([BASE_URL, 'ElemTab/z{:02d}.html'])


def is_float(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


class Table3Spider(scrapy.Spider):
    name = 'table3'

    start_urls = [TABLE3_URL.format(z) for z in range(1, 93)]

    def parse(self, response):
        # Retrieving the atomic number from the URL
        z = int(response.url[-7:-5])

        pre = response.css('pre').extract_first()
        lines = pre.splitlines()
        all_rows = ([x for x in line.split() if is_float(x)]
                    for line in lines[6:-1])
        rows = [r for r in all_rows if r is not None and r != []]
        yield {z: rows}
