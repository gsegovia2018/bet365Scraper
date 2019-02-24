
import pandas as pd
import time
import sys
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from futStatsScraper import scrapefut

futStats = scrapefut()
homeStats = futStats.loc[futStats['team'].str.lower() == 'atletico madrid']
print(homeStats)