#! /usr/bin/env python
import sys
import csv
import argparse

from sourmash.lca.lca_utils import taxlist


def main():
    p = argparse.ArgumentParser()
    p.add_argument('tax_genome_csv')
    p.add_argument('lineage_out')
    args = p.parse_args()

    tax_names = taxlist(include_strain=False)

    with open(args.tax_genome_csv, newline='') as fp:
        r = csv.DictReader(fp)

        with open(args.lineage_out, 'w', newline='') as out_fp:
            w = csv.writer(out_fp)
            w.writerow(['ident', *tax_names])
            
            for row in r:
                name = row['query_name']
                lineage = row['lineage']

                lineage = lineage.split(';')
                w.writerow([name, *lineage])
    

if __name__ == '__main__':
    sys.exit(main())
