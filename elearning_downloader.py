import PySimpleGUI as sg
import requests
import browser_cookie3
from bs4 import BeautifulSoup
import re
import os

# funzione per trovare il nome file
def getFilename_fromCd(cd):
	if not cd:
		return None
	fname = re.findall('filename=(.+)', cd)
	if len(fname) == 0:
		return None
	return fname[0]

layout = [  [sg.Text('Url Corso'),sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Elearning Course Downloader', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    url=values[0]
    window.close()
    lista=[]
    # imposta il cookie e fai la richiesta all'url
    cj = browser_cookie3.load(domain_name='elearning.unibs.it')
    session = requests.Session()
    session.cookies = cj
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    #trova solo url di file scaricabili e inserisci in lista
    for a in soup.find_all('a', href=True):
      if str(a).find("mod/resource")!= -1:
        lista.append((str(a).split('href="')[1]).split('"')[0])
    
    layout_pb = [[sg.Text('Download in corso:')],
                [sg.ProgressBar(len(lista), orientation='h', size=(20, 20), key='progressbar')]]
    window_pb = sg.Window('Elearning Course Downloader', layout_pb,no_titlebar=True)
    progress_bar = window_pb['progressbar']
    #scarica file in lista con nome corretto    	
    for i in range(0,len(lista)):
      r = session.get(lista[i],allow_redirects=True)
      filename = getFilename_fromCd(r.headers.get('content-disposition'))
      if os.path.exists((filename.split('"')[1]).split('"')[0])==False:
        print("download file "+str(i+1)+"/"+str(len(lista)))
        open((filename.split('"')[1]).split('"')[0], 'wb').write(r.content)
      event, values = window_pb.read(timeout=10)
      progress_bar.UpdateBar(i + 1)
    window_pb.close()



