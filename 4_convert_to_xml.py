import pandas as pd
import os

directory  = os.path.dirname(os.path.abspath(__file__))
os.chdir(directory)

csvFile = 'gaia_colored.csv'
xmlFile = 'gaia_colored.xml'

def ConvertToXML():

    csvData = pd.read_csv(csvFile, sep=',')
    nrows = len(csvData.index)

    print('Number of rows: ', nrows)

    xmlData = open(xmlFile, 'w')
    xmlData.write('<?xml version="1.0"?>' + '\n')
    xmlData.write('<RESOURCE>' + '\n')
    xmlData.write('<TABLE name= "' + directory + '" nrows=>"' + str(nrows) +'">' + '\n')

    for field in csvData.columns.values:
        dtype = csvData[field].dtype
        xmlData.write('<FIELD datatype="' + str(dtype) + '" name="' + str(field) + '"/>' '\n')

    xmlData.write('<DATA>' + '\n')
    xmlData.write('<TABLEDATA>' + '\n')

    cols = csvData.columns.values
    matrix = csvData.as_matrix()
    rowNum = 0

    for row in range(nrows):
        xmlData.write('  <TR>' + '\n')
        for i in range(len(cols)):
            xmlData.write('    <TD>' + str(matrix[rowNum, i]) + '</TD>' + '\n')
        xmlData.write('  </TR>' + '\n')

    xmlData.write('</TABLEDATA>' + '\n')
    xmlData.write('</DATA>' + '\n')
    xmlData.write('</TABLE>' + '\n')
    xmlData.write('</RESOURCE>' + '\n')
    xmlData.close()

ConvertToXML()
