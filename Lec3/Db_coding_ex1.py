#!/usr/bin/env python3
# Author: Mathias Rahbek-Borre (s183447)
# Date: 20-2-2022
# Course: 22112

import mysql.connector

# open connection and cursor
cnx = mysql.connector(user='s183447', passwd='', db='s183447', host='localhost')
cur = cnx.cursor()

# get content of the marriage table
cur.execute('''SELECT * FROM Marriages''')
mar_list = cur.fetchall()

mar_dict = dict()
# create
for mar in mar_list:
    key = frozenset(mar[0], mar[1])

    val = [mar[2], mar[3]]

    if mar_dict.get(key):
        mar_dict[key].append(val)
    else:
        mar_dict[key] = [val]
