#!/usr/bin/env  python3
# -*- coding: utf-8 -*-
"""
 File Name：  phonescrape01
 Author :  seven
 Change Activity:
     2018/11/11:
"""
#from phonescrape import scrape
#
# phones = ['10.61.2.50', '10.61.2.50']
#
# for phone in phones:
#     details = scrape.allDetails(phone)
#     print(details["FCH16229ZZ6"])
#
# FCH16229ZZ6

from phonescrape import scrape

phones = ['10.61.2.50', '10.61.2.51', '10.61.2.54', '10.61.2.58', '10.61.2.59', '10.61.2.56']
# phones = ['10.61.2.59']

for phone in phones:
    details = scrape.allDetails(phone)
    print(details)

print(type(details))
#FCH16229ZZ6

