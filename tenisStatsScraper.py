from selenium import webdriver
# Para descargar el html y hacer el scraping
from bs4 import BeautifulSoup
# Ayuda a buscar cosas usando parmetros especificos
from selenium.webdriver.common.by import By 
# Te permite esperar a que la pagina web se cargue
from selenium.webdriver.support.ui import WebDriverWait 
# Para especificar qu estas buscando en una pgina para determinar si la pgina se ha cargado
from selenium.webdriver.support import expected_conditions as EC 
# Para controlar el error timeoutexception
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import sys
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import csv
import os

def statsExists(player):
    f = "./Tenis_Stats.csv"
    if os.path.exists(f) and len(stats) == 0:
        df = pd.read_csv("Tenis_Stats.csv")
        stats = df.loc[df['player'] == player]
        if stats.empty:
            return []
        else:
            return stats
def scrape(player):
    stats = statsExists(player)
    if stats != []:
        return stats
    else:
        options = Options()
        options.headless = True # Esto es para que no se habra la ventana de firefox
        profile = webdriver.FirefoxProfile()
        # 1 - Allow all images
        # 2 - Block all images
        # 3 - Block 3rd party images 
        profile.set_preference("permissions.default.image", 2) # Esto es para que no se carguen las imagenes
        browser = webdriver.Firefox(firefox_profile=profile, options=options)
        browser.get("https://www.ultimatetennisstatistics.com/")
        search = browser.find_element(By.XPATH, '//*[@id="player"]')
        search.send_keys(player)
        time.sleep(2)
        search.send_keys(Keys.ARROW_DOWN)
        search.send_keys(Keys.RETURN)
        time.sleep(3)
        browser.find_element(By.XPATH,"/html/body/ul[1]/li[9]/a").click()
        time.sleep(2)
        browser.find_element(By.XPATH,'//*[@id="statisticsPill"]').click()
        time.sleep(2)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        browser.close()
        serve_html = soup.find_all('table', class_= 'table table-condensed table-hover table-striped')
        for serve in serve_html:
            data = serve.find_all('th', {"class": ["text-right pct-data", "text-right"]})
            for i in data:
                i = i.get_text()
                if i != '' and '/' not in i:
                    pal = i.replace('%','').replace('\n','')
                    stats.extend([pal])
        return(stats)