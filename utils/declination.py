#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2020 Jari Ojala (jari.ojala@iki.fi)

Licensed under the Apach License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import csv
import sys
import math

top_n = 3
top_3_rank=[] # [dist, decl, name]

def help():
        """Print usage."""
        app = sys.argv[0]
        print("Usage: %s -help" % app)
        print("       %s <east> <north>" % app)

def distance(e,n, east, north):
	return math.sqrt((e-east)**2 + (n-north)**2)

def main():

        if len(sys.argv) != 3:
                help()
                sys.exit(1)

        east = float(sys.argv[1])
        north = float(sys.argv[2])

        with open('Suomen_erantohila_2020.csv', 'r', encoding="utf8") as csvdata:
                recordreader = csv.reader(csvdata, delimiter='\t', quoting=csv.QUOTE_NONE, skipinitialspace=True)
                for record in recordreader:
                        if (len(record) > 0 and not record[0].startswith('#')):
                                dist,decl = distance(int(record[0]), int(record[1]), east, north), float(record[5])
                                if (len(top_3_rank) < top_n):
                                        top_3_rank.append([dist, decl, record[7]])
                                else:
                                        for i in range(len(top_3_rank)):
                                                if (dist < top_3_rank[i][0]):
                                                        top_3_rank[i] = [dist, decl, record[7]]
                                                        break

        sum = 0.0
        avg_decl = 0.0
        for i in range(len(top_3_rank)):
                sum = sum + top_3_rank[i][0]

        weight_sum = 0.0
        for i in range(len(top_3_rank)):
                weight = 1 / (top_3_rank[i][0] / sum)
                top_3_rank[i].append(weight)
                weight_sum = weight_sum + weight
                print("Map: " + top_3_rank[i][2] + ", dist: " + str(top_3_rank[i][0]) + ", decl: " + str(top_3_rank[i][1]) + ", weight: " + str(top_3_rank[i][3]))
                avg_decl = avg_decl + weight * top_3_rank[i][1]

        print("Avg decl: " + str(avg_decl / weight_sum))

if __name__ == "__main__":
        main()
