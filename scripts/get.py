# script to a) extract world bank indicator data b) convert into data packages
# built for python3

import urllib.request
import urllib.parse
import json
import csv
import codecs
import os

class Processor(object):

    def __init__(self, indicator):
        self.indicator = indicator
        if 'http' in self.indicator:
            # https://data.worldbank.org/indicator/SL.GDP.PCAP.EM.KD?locations=BR&view=chart
            path = urllib.parse.urlparse(self.indicator)[2]
            self.indicator = path.split('/')[-1]

        self.meta_url = 'https://api.worldbank.org/indicator/%s?format=json' % self.indicator
        self.data_url = 'https://api.worldbank.org/indicator/%s?format=csv' % self.indicator
        self.meta_dest = os.path.join('cache', '%s.meta.json' % self.indicator)
        self.data_dest = os.path.join('cache', '%s.csv' % self.indicator)
    
    def execute(self, cache=True):
        '''Retrieve a world bank indicator and convert to a data package.

        Data Package is stored at ./indicators/{indicator-name}
        '''
        if cache:
            self.retrieve()
            (meta, data) = self.extract(open(self.meta_dest), open(self.data_dest))
        else:
            (meta, data) = self.extract(
                    urllib.request.urlopen(self.meta_url),
                    codecs.iterdecode(urllib.request.urlopen(self.data_url), 'utf-8')
                    )

        basepath = os.path.join('indicators', meta['name'])
        os.makedirs(basepath, exist_ok=True)
        self.datapackage(meta, data, basepath)
        return basepath

    def retrieve(self):
        os.makedirs('cache', exist_ok=True)
        urllib.request.urlretrieve(self.meta_url, self.meta_dest)
        urllib.request.urlretrieve(self.data_url, self.data_dest)

    @classmethod
    def extract(self, metafo, datafo):
        '''Extract raw metadata and data into nicely structured form.

        @metafo: world bank json metadata file object
        @datafo: world bank CSV data file object
        @return: (metadata, data) where metadata is Data Package JSON and data is normalized CSV.
        '''
        metadata = {}
        data = []
        tmpmeta = json.load(metafo)[1][0]
        # raw metadata looks like
        # [{"page":1,"pages":1,"per_page":"50","total":1},[{"id":"GC.DOD.TOTL.GD.ZS","name":"Central government debt, total (% of GDP)","source":{"id":"2","value":"World Development Indicators"},"sourceNote":"Debt is the entire stock of direct government fixed-term contractual obligations to others outstanding on a particular date. It includes domestic and foreign liabilities such as currency and money deposits, securities other than shares, and loans. It is the gross amount of government liabilities reduced by the amount of equity and financial derivatives held by the government. Because debt is a stock rather than a flow, it is measured as of a given date, usually the last day of the fiscal year.","sourceOrganization":"International Monetary Fund, Government Finance Statistics Yearbook and data files, and World Bank and OECD GDP estimates.","topics":[{"id":"3","value":"Economy & Growth"},{"id":"13","value":"Public Sector "}]}]]
        metadata = {
            'title': tmpmeta['name'],
            'name': tmpmeta['id'].lower(),
            'worldbank': {
                'indicator': tmpmeta['id'].lower()
            },
            'readme': tmpmeta['sourceNote'],
            'licenses': [{
                'name': 'CC-BY-4.0'
                }],
            'keywords': [ x['value'] for x in tmpmeta['topics'] ]
        }
        
        tmpdata = csv.reader(datafo)
        fields = tmpdata.__next__()
        # remove BOM that is at start of file ... 
        # '\ufeff"Country Name"'
        # https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
        fields[0] = fields[0][2:-1]
        outdata = [fields[:2] + ['Year', 'Value']]
        for row in tmpdata:
            for year,col in zip(fields[2:], row[2:]):
                if col.strip():
                    outdata.append(row[0:2] + [year, col])

        return (metadata, outdata)

    @classmethod
    def datapackage(self, metadata, data, basepath):
        dpjson = os.path.join(basepath, 'datapackage.json')
        readme = os.path.join(basepath, 'README.md')
        datafp = os.path.join(basepath, 'data.csv')

        metadata['resources'] = [{
            'name': 'data',
            'title': 'Indicator data',
            'path': 'data.csv',
            'format': 'csv',
            'mediatype': 'text/csv',
            'encoding': 'utf-8',
            'schema': {
                'fields': [
                    {
                        'name': 'Country Name',
                        'type': 'string',
                        'description': 'Country or Region name'
                    },
                    {
                        'name': 'Country Code',
                        'type': 'string',
                        'description': 'ISO 3-digit ISO code extended to include regional codes e.g. EUR, ARB etc'
                    },
                    {
                        'name': 'Year',
                        'type': 'year',
                        'description': 'Year'
                    },
                    {
                        'name': 'Value',
                        'type': 'number', # TODO check it is always numeric ...!
                        'description': metadata['readme']
                    }
                ]
            }
        }]

        with open(dpjson, 'w') as fo:
            json.dump(metadata, fo, indent=2)
        with open(readme, 'w') as fo:
            fo.write(metadata['readme'])
        with open(datafp, 'w') as fo:
            writer = csv.writer(fo)
            writer.writerows(data)


import tempfile
import os
def test_it():
    url = 'https://data.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS'
    indicator = 'GC.DOD.TOTL.GD.ZS'
    processor = Processor(url)

    assert processor.indicator == indicator

    (meta, data) = processor.extract(
            urllib.request.urlopen(processor.meta_url),
            codecs.iterdecode(urllib.request.urlopen(processor.data_url), 'utf-8')
            )
    assert meta['title'] == 'Central government debt, total (% of GDP)'
    print(data[0:2])
    assert data[0] == ['Country Name', 'Country Code', 'Year', 'Value']
    assert data[1] == ['Caribbean small states', 'CSS', '2006', '53.4626403130906']

    with tempfile.TemporaryDirectory() as basepath:
        processor.datapackage(meta, data, basepath)
        readme = open(os.path.join(basepath, 'README.md')) 
        dp = json.load(open(os.path.join(basepath, 'datapackage.json')))
        data = open(os.path.join(basepath, 'data.csv'))

        assert dp['resources'][0]['schema']['fields'][3]['name'] == 'Value'


import sys
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('''
Usage: python scripts/get.py {indicator or indicator url}

Example:

    python scripts/get.py https://data.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS
''')
        sys.exit(1)

    indicator = sys.argv[1] 
    processor = Processor(indicator)
    out = processor.execute()
    print('Indicator data package written to: %s' % out)

