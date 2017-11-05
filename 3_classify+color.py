# Categorise data, assign B-V values and work out a representative colour in HSB 
import csv
import pandas as pd
import numpy as np
import os
import sys

directory  = os.path.dirname(os.path.abspath(__file__))
os.chdir(directory)
dirname = os.path.dirname
datadir = os.path.join(dirname(dirname(directory)), 'lookup_tables/')

csvFile = 'gaiadata.csv'
outFile = 'gaia_colored.csv'
lookupMainSequence = datadir + 'SCM_ms.csv'
lookupGiants = datadir + 'SCM_giants.csv'

def Classify():
    # M > 0 = A stars and smaller; M < 0 = giants accordingly

    with open(csvFile) as counter:
        numRows = sum(1 for row in counter)
        print('Total rows = ', numRows)
    
    chunksize = 2000

    dwarfData = pd.read_csv(lookupMainSequence, sep=',')
    giantData = pd.read_csv(lookupGiants, sep=',')
    giantData = giantData[giantData.Mv != -1]  # eliminate duplicated
    giantData = giantData[giantData.Mv != 0.25]  # elimiate duplicates

    size_label = ['giant', 'dwarf']
    Mbins = [-50, 0, 50]

    dwarfMags = pd.DataFrame(columns=['Mag'])  # empty dataframe
    giantMags = pd.DataFrame(columns=['Mag'])  # empty dataframe

    dwarfBins = dwarfData['Mv']
    dwarfLabels = dwarfData['B-V']
    dwarfLabels = dwarfLabels.drop(dwarfLabels.index[0])
    # dwarfMags['BV'] = pd.cut(dwarfMags['Mag'], dwarfBins, labels=dwarfLabels, include_lowest=False)
    # print(dwarfMags)

    giantBins = giantData['Mv']
    giantBins = giantBins.sort_values(0)
    giantLabels = giantData['B-V']
    giantLabels = giantLabels.drop(giantLabels.index[0])
    giantMags['BV'] = pd.cut(giantMags['Mag'], giantBins, labels=giantLabels, include_lowest=False)
    # fill values not in lookup table with a bit of hack (-0.16), eyeballed from main sequence
    giantMags['BV'] = pd.to_numeric(giantMags['BV'], errors='coerce')
    giantMags['BV'] = giantMags['BV'].fillna(-0.16)
    # print(giantMags)

    minBV = 0.16 # min(csvData['BV']) -- ABSOLUTE VALUE -- read this of previous table process
    maxBV = 1.66 + 0.16 # max(csvData['BV']) + abs(minBV)

    firstLoop = True
    
    for line in range(0,numRows,chunksize):

        csvData = pd.read_csv(csvFile, sep=',', nrows=chunksize, skiprows=line)
        #print(i)
        csvData['BV'] = 0.0
        csvData['H'] = 0.0  # Hue
        csvData['S'] = 50.0  # Saturation - set to 50% for now
        csvData['B'] = 50.0  # Brightness - set to 50% for now
        # print(csvData)


        csvData['size'] = pd.cut(csvData.iloc[:,6], Mbins, labels=size_label, include_lowest=True)
        #print(pd.value_counts(csvData['size']))

        i = 0; j = 0
        # wite to seperate dwarf and giant dataframes
        for row in csvData.itertuples():
            if row.size == 'dwarf':
                if i >= 0:
                    dwarfMags.loc[i, 'Mag'] = csvData.iloc[row.Index, 6]
                    i += 1
            elif row.size == 'giant':
                if j >= 0:
                    giantMags.loc[j, 'Mag'] = csvData.iloc[row.Index, 6]
                    j += 1

        # bin magnitudes and assign values according to lookup table
        dwarfMags['BV'] = pd.cut(dwarfMags['Mag'], dwarfBins, labels=dwarfLabels, include_lowest=False)

        giantMags['BV'] = pd.cut(giantMags['Mag'], giantBins, labels=giantLabels, include_lowest=False)
        # fill values not in lookup table with a bit of hack (-0.16), eyeballed from main sequence
        giantMags['BV'] = pd.to_numeric(giantMags['BV'], errors='coerce')
        giantMags['BV'] = giantMags['BV'].fillna(-0.16)

        k = 0; l = 0;
        # hack table back together
        for row in csvData.itertuples():
            if row.size == 'dwarf':
                if k >= 0:
                    csvData.iloc[row.Index, 10] = dwarfMags.iloc[k, 1]
                    k += 1
            elif row.size == 'giant':
                if l >= 0:
                    csvData.iloc[row.Index, 10] = giantMags.iloc[l, 1]
                    l += 1

        percent = (line/numRows)*100
        print('Rows processed: %i -- %.2f%%' % (line, percent), '\r', end='')
        sys.stdout.flush()

        # Finally use BV to find a value for H -- add min to every number, divide by new max and * 100
        # print('minH = ', minBV); print('maxBV = ', maxBV)
        for row in csvData.itertuples():
             csvData.loc[row.Index, 'H'] = (csvData.loc[row.Index, 'BV'] + minBV)/maxBV * 280

        if firstLoop == True:
            csvData.to_csv(outFile, sep=',', encoding='utf-8', index=False, header=True, chunksize=chunksize)
        else:
            csvData.to_csv(outFile, sep=',', encoding='utf-8', index=False, header=False, mode='a', chunksize=chunksize)

        firstLoop =  False

    # scale the H column -- possibly with sklearn.preprocessing

    print('\n','\r' 'All done!')
    
Classify()