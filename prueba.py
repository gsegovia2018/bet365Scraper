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
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

f = "./Tenis_Stats.csv"
df = None
if os.path.exists(f):
    df = pd.read_csv("Tenis_Stats.csv")
    df['hola'] = [1,2,3,4,5]
else:
    with open('Tenis_Stats.csv', 'w'):
        df = pd.read_csv("Tenis_Stats.csv")
        pass
df.insert(2,'new',1000)
df.to_csv("Tenis_Stats.csv")