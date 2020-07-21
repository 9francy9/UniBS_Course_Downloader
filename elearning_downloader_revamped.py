import requests
from bs4 import BeautifulSoup
import re
import os
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import filedialog
from tkinter import *

# funzione per trovare il nome file
def getFilename_fromCd(cd):
	if not cd:
		return None
	fname = re.findall('filename=(.+)', cd)
	if len(fname) == 0:
		return None
	return fname[0]

#funzione per trovare il cookie
def getCookie(url):
    i=int(input("Scegli se usare Chrome [1] o Firefox [2]:"))
    if i==1:
        print("Avvio di Chrome in corso...")
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    if i==2:
        print("Avvio di firefox in corso...")
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    driver.get(url)
    while True:
        if driver.get_cookie("MoodleSessionunibs")!=None:
            cookie=str(driver.get_cookie("MoodleSessionunibs")).split("'")[7]
            break
    driver.quit()
    return cookie

#funzione per scaricare la pagina web e prendere il suo contenuto
def getPage(url,cookie):
    session = requests.Session()
    jar = requests.cookies.RequestsCookieJar()
    jar.set('MoodleSessionunibs', cookie)
    session.cookies = jar
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    return soup


#trova solo url di file scaricabili e inserisci in lista
def getFileLinks(soup):
    lista=[]
    for a in soup.find_all('a', href=True):
      if str(a).find("mod/resource")!= -1:
        lista.append((str(a).split('href="')[1]).split('"')[0])
    return lista

#trova il nome dei corsi
def getCourseNamesAndLinks(soup):
    lista=[]
    for a in soup.find_all('h3',{"class": "coursename"}):
        lista.append(a)
    return lista

#scarica file in lista con nome corretto   
def fileDownloader(lista,cookie,folder): 	
    for i in range(0,len(lista)):
        session = requests.Session()
        jar = requests.cookies.RequestsCookieJar()
        jar.set('MoodleSessionunibs', cookie)
        session.cookies = jar
        r = session.get(lista[i],allow_redirects=True)
        filename = getFilename_fromCd(r.headers.get('content-disposition'))
        if os.path.exists((filename.split('"')[1]).split('"')[0])==False:
            print("download file "+str(i+1)+"/"+str(len(lista)), end="\r", flush=True)
            open(folder+"/"+(filename.split('"')[1]).split('"')[0], 'wb').write(r.content)

def main():
    root = Tk()
    root.withdraw()
    os.environ['WDM_LOG_LEVEL'] = '0'
    cookie=getCookie("https://elearning.unibs.it/my/")
    soup=getPage("https://elearning.unibs.it/",cookie)
    lista=getCourseNamesAndLinks(soup)
    for i in range(0,len(lista)):
        print("["+str(i+1)+"] "+((str(lista[i]).split(">")[2]).split("<")[0])+"\n")
    n = int(input('Numero del corso che si vuole scaricare: '))
    soup=getPage(str(lista[n-1]).split('"')[5],cookie)
    lista=getFileLinks(soup)
    folder= filedialog.askdirectory()
    fileDownloader(lista,cookie,folder)
if __name__ == "__main__":
    main()