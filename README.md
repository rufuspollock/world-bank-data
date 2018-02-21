Automated access to World Bank data and conversion to data packages.

## World Development Indicators

World Bank World Development Indicators like: https://data.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS

We have a script to automate access and data extraction for these.

1. Downloading the metadata data
2. Extracting metadata and data
3. Converting to a [Data Package][]

[Data Package]: https://frictionlessdata.io/data-packages

The script is python based and uses python 3.0. It has no dependencies outside of the standard library. Try it:

```
python scripts/get.py

# download and extract this indicator
python scripts/get.py https://data.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS
```


## Research: The World Bank data API

You can get data in CSV, JSON and XML (default).

Per indicator:

```bash
https://api.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS?format=csv

# for some reason json format just yields metadata
https://api.worldbank.org/indicator/GC.DOD.TOTL.GD.ZS?format=json
```

More elaborate queries via http://blogs.worldbank.org/opendata/first-steps-in-integrating-open-data:

```
http://api.worldbank.org/en/countries/KE;XF;XM/indicators/EN.ATM.CO2E.PC?date=1961:2011&format=csv


http://api.worldbank.org/en/countries/KE;XF;XM/indicators/EN.ATM.CO2E.PC?date=1961:2011&format=json
```

## Motivation: User Stories

As a Data Wrangler I want to convert a world bank indicator into a tabular data package automatically.

* And keep it up to date ...

As a Data Wrangler I want to get existing world bank indicator as if it were a data package 

* use data get
* use data info (?)
* use data cat

