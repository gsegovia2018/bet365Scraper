"""
TO DO: En tenis diferenciar si hay dobles o no (?)
@author: Marcos Gomez-Espana
"""
import sys
import datetime
import os
import time
import selenium.common.exceptions
# module to control browser, in this case firefox
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
from selenium.webdriver.firefox.options import Options
from tenisStatsScraper import scrape
from futStatsScraper import scrapefut
from difflib import SequenceMatcher
import unidecode

options = Options()
options.headless = True # Esto es para que no se habra la ventana de firefox
profile = webdriver.FirefoxProfile()
# 1 - Allow all images
# 2 - Block all images
# 3 - Block 3rd party images 
profile.set_preference("permissions.default.image", 2) # Esto es para que no se carguen las imagenes
browser = webdriver.Firefox(firefox_profile=profile, options=options)
# Ask for the sport to scrape
sport = input("Sport to scrape: ")
# Si no tuviesemos el driver en el PATH deberiamos poner webdriver.Firefox(executable_path="/path/to/driver")
# Después cargar el driver vamos a la dirección que queramos, en este caso la pagina de bet365.
browser.get("http://www.bet365.es/")
# Vamos a darle unos 10 segundos para cargar, si no se ha cargado un elemento que le pasamos por XPATH damos un error y nos salimos
timeout = 10
try:
    WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/form/div[3]/center/div/div[3]/div/div[1]/div/div/a')))
except TimeoutException:
    print("Timed out waiting for bet365 main page to load")
    browser.quit()     
    sys.exit()
# Debemos pinchar en deportes porque la página bet365.es en si no tiene nada, es como una portada. Para sacar el XPATH simplemente pinchas
# en donde quieras ir con el clic derecho y le das a inspeccionar, click derecho al código y copiar como XPATH
try:
    browser.find_element(By.XPATH, '//*[@id="dv1"]/a').click()
except selenium.common.exceptions.InvalidSelectorException:
    print("Error: The structure of the page bet365 has changed")
    browser.quit() 
    sys.exit()

try:
    WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/img')))
except TimeoutException:
    print("Timed out waiting for main page to load")
    browser.quit()     
    sys.exit()

if (sport == "futbol") or (sport == "fútbol") or (sport == "fut") or (sport == "football"):
    futStats = scrapefut()
    # Nos vamos a la pestaña futbol y dentro de futbol a España
    try:
        browser.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div[15]').click()
    except selenium.common.exceptions.InvalidSelectorException:
        print("Error: Cambio en la estructura de la pagina")
        browser.quit() 
        sys.exit()
    try:
        WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[14]/div/div')))
    except TimeoutException:
        print("Timed out waiting for football page to load")
        browser.quit()     
        sys.exit()
    # Buscamos el elemento españa por css_selector por variar
    try:
        browser.find_element(By.CSS_SELECTOR, 'div.sm-Market:nth-child(1) > div:nth-child(2) > div:nth-child(4) > div:nth-child(1)').click()
    except selenium.common.exceptions.InvalidSelectorException:
        print("Error: Cambio en la estructura de la pagina")
        browser.quit() 
        sys.exit()
    try:
        WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div')))
    except TimeoutException:
        print("Timed out waiting for tenis page to load")
        browser.quit()     
        sys.exit()
    # Guardamos la información de esta pagina en soup y procedemos a hacer el scrape.
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    # Una vez descargada la página podemos cerrar el browser
    browser.close()
    # Declaramos las variables pues es mas facil si queremos ampliarlo para todas las competiciones
    wins = []
    draws = []
    loss = []
    equipoLocal = []
    equipoVisitante = []
    torneo = []
    homeRank = []
    awayRank = []
    homeGoals = []
    homePossession = []
    homePasses = []
    homeAerialWon = []
    homeRating = []
    awayGoals = []
    awayPossession = []
    awayPasses = []
    awayAerialWon = []
    awayRating = []
    # Puede haber varias competiciones, cogemos la liga que es la primera, es facil ampliarlo para todas
    torneos = soup.find_all('div', class_='gl-MarketGroup cm-CouponMarketGroup cm-CouponMarketGroup_Open')
    for trn in torneos:
        t = trn.find('span', class_='cm-CouponMarketGroupButton_Text').get_text().split('-')[1]
        if('1' not in t):
            break
        else:
            # Buscamos las cuotas
            cuotaHtml = trn.find_all('span', class_="gl-ParticipantOddsOnly_Odds")
            cuota = [cuot.get_text() for cuot in cuotaHtml]
            numeroPartidos = len(cuota)//3
            # y las insertamos en nuestras variables
            wins.extend((cuota[0:numeroPartidos]))
            draws.extend((cuota[numeroPartidos:int(2)*numeroPartidos]))
            loss.extend(cuota[int(2)*numeroPartidos:int(3)*numeroPartidos])
            # Buscamos el nombre del torneo
            # Buscamos el nombre de los dos tenistas
            equiposHtml = trn.find_all('div', class_= 'sl-CouponParticipantWithBookCloses_NameContainer')
            for i, eq in enumerate(equiposHtml):
                equipo = eq.get_text().split(' v ')
                if len(equipo) == 2:
                    # Añadimos el primer tenista a ten_1
                    equipoLocal.extend([equipo[0]])
                    # Añadimos el segundo tenista a ten_2
                    equipoVisitante.extend([equipo[1]])
                    # Metemos el nombre del torneo por cada partido que haya
                    torneo.extend([t])
                    # SequenceMatcher(None, a, b).ratio()
                    equipo[0] = unidecode.unidecode(equipo[0].lower().replace('de',' ').replace('real',' ').replace(' ',''))
                    equipo[1] = unidecode.unidecode(equipo[1].lower().replace('de',' ').replace('real',' ').replace(' ',''))
                    homeStats = futStats.loc[futStats['team'] == equipo[0]]
                    awayStats = futStats.loc[futStats['team'] == equipo[1]]
                    homeRank.extend(homeStats['rank'].values)
                    awayRank.extend(awayStats['rank'].values)
                    homeGoals.extend(homeStats['goals'].values)
                    homePossession.extend(homeStats['possession%'].values)
                    homePasses.extend(homeStats['passes%'].values)
                    homeAerialWon.extend(homeStats['aerialWon%'].values)
                    homeRating.extend(homeStats['rating'].values)
                    awayGoals.extend(awayStats['goals'].values)
                    awayPossession.extend(awayStats['possession%'].values)
                    awayPasses.extend(awayStats['passes%'].values)
                    awayAerialWon.extend(awayStats['aerialWon%'].values)
                    awayRating.extend(awayStats['rating'].values)
                else:
                    del wins[i]
                    del draws[i]
                    del loss[i]       
    # Definimos el Dataframe
    df = pd.DataFrame()
    df['Equipo Local'] = equipoLocal
    df['Equipo Visitante'] = equipoVisitante
    df['Competicion'] = torneo
    df['1'] = wins
    df['X'] = draws
    df['2'] = loss
    df['HR'] = homeRank
    df['HG'] = homeGoals
    df['HP'] = homePossession
    df['HPA'] = homePasses
    df['HAE'] = homeAerialWon
    df['HRA'] = homeRating
    df['AR'] = awayRank    
    df['AG'] = awayGoals    
    df['AP'] = awayPossession    
    df['APA'] = awayPasses    
    df['AAE'] = awayAerialWon    
    df['ARA'] = awayRating
    print(df.to_string())
    df.to_csv(r'C:\Users\Marcos\Documents\Python\bet365Scraper\futbol_csv\cuotas_futbol_' + str(datetime.datetime.now().strftime("%Y_%m_%d")) + '.csv',index=False)

if(sport == "tennis") or (sport == "tenis") or (sport == "ten"):
    # Definimos 4 variables, la primera tendra los primeros tenistas la segunda los segundos, la tercera la cuota del primer
    # tenista y la segunda del segundo y torneos
    ten_1 = []
    ten_2 = []
    win_1 = []
    win_2 = []
    torneo = []
    browser.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div/div/div[25]').click()
    try:
        WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div')))
    except TimeoutException:
        print("Timed out waiting for tennis page to load")
        browser.quit()     
        sys.exit()
    browser.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div').click()
    try:
        WebDriverWait(browser,timeout).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]')))
    except TimeoutException:
        print("Timed out waiting for available matches page to load")
        browser.quit()     
        sys.exit()
    # Guardamos la información de esta pagina en soup y procedemos a hacer el scrape.
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    # Una vez descargada la página podemos cerrar el browser
    browser.close()
    torneos = soup.find_all('div', class_='gl-MarketGroup cm-CouponMarketGroup cm-CouponMarketGroup_Open')
    for trn in torneos:
        # Buscamos las cuotas
        cuotaHtml = trn.find_all('span', class_="gl-ParticipantOddsOnly_Odds")
        cuota = [cuot.get_text() for cuot in cuotaHtml]
        numeroPartidos = len(cuota)//2
        # y las insertamos en nuestras variables
        win_1.extend((cuota[0:numeroPartidos]))
        win_2.extend((cuota[numeroPartidos:int(2)*numeroPartidos]))
        # Buscamos el nombre del torneo
        t = trn.find('span', class_='cm-CouponMarketGroupButton_Text').get_text().split('-')[0]
        # Buscamos el nombre de los dos tenistas
        date = trn.find_all('div', class_= 'gl-MarketColumnHeader sl-MarketHeaderLabel sl-MarketHeaderLabel_Date')
        tenistasHtml = trn.find_all('div', class_= 'sl-CouponParticipantWithBookCloses_Name')
        for jg in tenistasHtml:
            player1 = jg.get_text().split(' v ')[0] 
            player2 = jg.get_text().split(' v ')[1]
            if '/' not in player1:
                dataPlayer1 = scrape(player1)
                dataPlayer2 = scrape(player2)
                # Añadimos el primer tenista a ten_1
                ten_1.extend([player1])
                # Añadimos el segundo tenista a ten_2
                ten_2.extend([player2])
                # Metemos el nombre del torneo por cada partido que haya
                torneo.extend([t])
                for i in range(len(dataPlayer1)):
                    print(dataPlayer1[i])
    df = pd.DataFrame()
    df['tenista_1'] = ten_1
    df['tenista_2'] = ten_2
    df['torneo'] = torneo
    df['1'] = win_1
    df['2'] = win_2
    print(df.to_string())
    df.to_csv(r'C:\Users\Marcos\Documents\Python\bet365Scraper\tenis_csv\cuotas_tenis_' + str(datetime.datetime.now().strftime("%Y_%m_%d")) + '.csv',index=False)     
    
    