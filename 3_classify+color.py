# Categorise data, assign B-V values and work out a representative colour in HSB 

import pandas as pd
import numpy as np
import os

directory  = os.path.dirname(os.path.abspath(__file__))
os.chdir(directory)
dirname = os.path.dirname
datadir = os.path.join(dirname(dirname(directory)), 'lookup_tables/')

csvFile = 'gaiadata.csv'
lookupMainSequence = datadir + 'SCM_ms.csv'
lookupGiants = datadir + 'SCM_giants.csv'

def Classify():
    # M > 0 = A stars and smaller; M < 0 = giants accordingly

    csvData = pd.read_csv(csvFile, sep=',')
    numRows = len(csvData.index)
    csvData['BV'] = np.zeros(numRows)
    csvData['H'] = np.zeros(numRows)  # Hue
    csvData['S'] = 50.0  # Saturation - set to 50% for now
    csvData['B'] = 50.0  # Brightness - set to 50% for now

    dwarfMags = pd.DataFrame(columns=['Mag'])  # empty dataframe
    giantMags = pd.DataFrame(columns=['Mag'])  # empty dataframe
    # print(dwarfMags)

    minMag = min(csvData['M'])
    maxMag = max(csvData['M'])
    # print(maxMag, minMag)

    dwarfData = pd.read_csv(lookupMainSequence, sep=',')
    giantData = pd.read_csv(lookupGiants, sep=',')
    giantData = giantData[giantData.Mv != -1]
    giantData = giantData[giantData.Mv != 0.25]
    #giantData = giantData.sort_values(['B-V'])

    size_label = ['giant', 'dwarf']
    Mbins = [minMag, 0, maxMag]
    csvData['size'] = pd.cut(csvData['M'], Mbins, labels=size_label, include_lowest=True)
    print(pd.value_counts(csvData['size']))

    i = 0; j = 0
    # split dwarf and giants into seperate dataframes
    for row in csvData.itertuples():
        if row.size == 'dwarf':
            if i >= 0:
                dwarfMags.loc[i, 'Mag'] = csvData.loc[row.Index, 'M']
                i += 1
        elif row.size == 'giant':
            if j >= 0:
                giantMags.loc[j, 'Mag'] = csvData.loc[row.Index, 'M']
                j += 1

    dwarfBins = dwarfData['Mv']
    dwarfLabels = dwarfData['B-V']
    dwarfLabels = dwarfLabels.drop(dwarfLabels.index[0])
    dwarfMags['BV'] = pd.cut(dwarfMags['Mag'], dwarfBins, labels=dwarfLabels, include_lowest=False)

    giantBins = giantData['Mv']
    giantBins = giantBins.sort_values(0)
    giantLabels = giantData['B-V']
    giantLabels = giantLabels.drop(giantLabels.index[0])
    giantMags['BV'] = pd.cut(giantMags['Mag'], giantBins, labels=giantLabels, include_lowest=False)
    # fill values not in lookup table with a bit of hack (-0.16), eyeballed from main sequence
    giantMags['BV'] = pd.to_numeric(giantMags['BV'], errors='coerce')
    giantMags['BV'] = giantMags['BV'].fillna(-0.16)

    k = 0; l = 0; totalRows = 0
    # hack table back together
    for row in csvData.itertuples():
        if row.size == 'dwarf':
            if k >= 0:
                csvData.loc[row.Index, 'BV'] = dwarfMags.loc[k, 'BV']
                k += 1
        elif row.size == 'giant':
            if l >= 0:
                csvData.loc[row.Index, 'BV'] = giantMags.loc[l, 'BV']
                l += 1
        totalRows += 1

    # Finally use BV to find a value for H -- add min to every number, divide by new max and * 100
    minBV = min(csvData['BV'])
    maxBV = max(csvData['BV']) + abs(minBV)
    # print('minH = ', minBV); print('maxBV = ', maxBV)

    for row in csvData.itertuples():
        csvData.loc[row.Index, 'H'] = (csvData.loc[row.Index, 'BV'] + abs(minBV))/maxBV * 280

    print(np.max(csvData['H']))

    # print(dwarfMags)
    # print(giantMags)
    # print(csvData.loc[50])
    # print(csvData)

    csvData.to_csv('gaia_colored.csv', sep=',', encoding='utf-8', index=False )
    print('Rows processed: ', totalRows)
    
Classify()