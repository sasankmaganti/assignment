# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 06:25:30 2019

@author: Sasank Maganti

main.py
"""
import os
import scrape

#change the working directory to the directory in which the file is located
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

if __name__ == '__main__':
    scrape.scrape_idaho()
