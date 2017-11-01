import csv
import gzip
import numpy as np
import os

directory  = os.path.dirname(os.path.abspath(__file__))
os.chdir(directory)

datadir = os.path.join(directory, 'data')

maxrows = 0  # set to 0 to import everything

def main():
    
    files = []
    for name in os.listdir(datadir):
        if name.endswith('.csv.gz'):
            files.append(os.path.join(datadir, name))
    files.sort()
    
    # print(files)

    datafile = open('gaiadata.csv', 'wt')
    fieldnames = ['name', 'b', 'l', 'parallax', 'dist_pc', 'mag', 'M', 'xpc', 'ypc', 'zpc']
    writer = csv.writer(datafile, delimiter=',')
    writer.writerow(fieldnames)
    
    count = 0
    skip = 0
    for filename in files:
        if maxrows > 0 and count >= maxrows:
            break
            print('break')
        with gzip.open(filename, 'rt') as fp:
            print('reading', filename)
            reader = csv.reader(fp)
            header = next(reader)
            header = {name: index for (index, name) in enumerate(header)}

            for row in reader:
               #print(row)
                if maxrows > 0 and count >= maxrows:
                    break
                    print('break')
                
                # skip negative parallax entries
                p_val = float(row[header['parallax']])
                try:                    
                    if p_val > 0:
                        parallax = p_val / 1000  # original units in mas
                    else:
                        # print ('negative parallax, skipping entry', count)
                        skip += 1
                        raise Exception
                except Exception:
                    continue

                if row[header['tycho2_id']] is '':
                    name = 'HIP_'+row[header['hip']]
                else:
                    name = row[header['tycho2_id']]

                b = float(row[header['b']])  # galactic lattitude
                l = float(row[header['l']])  # galactic longtitude

                dist_pc = 1.0 / parallax
                mag = float(row[header['phot_g_mean_mag']])
                M = mag - 5 * np.log10(dist_pc) + 5

                b_rad = np.radians(b)
                l_rad = np.radians(l)

                xpc = dist_pc*(np.cos(b_rad) * np.cos(l_rad))
                ypc = dist_pc*(np.cos(b_rad) * np.sin(l_rad))
                zpc = dist_pc*(np.sin(b_rad))

                row = [name, b, l , parallax, dist_pc, mag, M, xpc, ypc, zpc]
                writer.writerow(row)

                count += 1
        
        print('Rows processed:', count)
        print('Rows skipped:', skip)

main()
