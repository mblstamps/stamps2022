#! /usr/bin/env python
"""
Convert 'sourmash tax genome' CSV output into a sourmash taxonomy file,
suitable for use with 'sourmash tax metagenome'.

This script will soon be integrated into sourmash :).
See https://github.com/sourmash-bio/sourmash/issues/2153 for more info.

CTB 7/26/22.
"""
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

    n = 0
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

                n += 1

    print(f"Converted {n} rows from tax output to lineage CSV.")


if __name__ == '__main__':
    sys.exit(main())
