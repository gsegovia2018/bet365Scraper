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
import sys
import pandas as pd
browser = webdriver.Firefox()
#browser = webdriver.PhantomJS()
#browser.minimize_window()
# Después cargar el driver vamos a la dirección que queramos, en este caso la pagina de bet365.
browser.get("https://www.whoscored.com/Regions/206/Tournaments/4/Seasons/7466/Stages/16546/TeamStatistics/Spain-La-Liga-2018-2019")
soup = BeautifulSoup(browser.page_source, 'html.parser')
browser.close()
tm = sys.argv[1]
teams = []
goals = []
rank = []
shots = []
possession = []
passes = []
aerialWon = []
rating = []
stats = soup.find(id= 'top-team-stats-summary-grid')
teams_html = stats.find_all('td', class_= "tn")
goals_html = stats.find_all('td', class_= "goal")
rank_html = stats.find_all('td', class_= "o")
shots_html = stats.find_all('td', class_= "shotsPerGame")
possession_html = stats.find_all('td', class_= "possession")
passes_html = stats.find_all('td', class_= "passSuccess")
aerial_html = stats.find_all('td', class_= "aerialWonPerGame")
rating_html = stats.find_all('td', class_= "sorted")
for i in range(len(teams_html)):
    teams.extend([teams_html[i].get_text()])
    goals.extend([goals_html[i].get_text()])
    rank.extend([rank_html[i].get_text()])
    possession.extend([possession_html[i].get_text()])
    passes.extend([passes_html[i].get_text()])
    aerialWon.extend([aerial_html[i].get_text()])
    rating.extend([rating_html[i].get_text()])
print(teams)
df = pd.DataFrame()
df['rank'] = rank
df['team'] = teams
df['goals'] = goals
df['possession%'] = possession
df['passes%'] = passes
df['aerialWon%'] = aerialWon
df['rating'] = rating
datos = []
if tm in teams:
    i = teams.index("Barcelona")
    datos.extend([rank[i]])
    datos.extend([teams[i]])
    datos.extend([goals[i]])
    datos.extend([possession[i]])
    datos.extend([passes[i]])
    datos.extend([rating[i]])
    print(datos)