# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 08:05:50 2019

@author: Sasank Maganti

System test
"""

from unittest import TestCase
import scrape
import os

class ScraperTest(TestCase):
    
    def setUp(self):
        self.scrape_idaho = scrape.scrape_idaho()
    
    def test_scrapper(self):
        self.assertEqual(os.path.isfile('results.csv'),True)
        