import requests
from bs4 import BeautifulSoup
import time
import rtmidi_python as rtmidi
from threading import Timer
import math

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def get_soup(url=None):

    r = requests.get(url)
    soup = BeautifulSoup(r.text)

    return soup

def scraper(soup):

    print('SEARCHING')
    alldata = []
    table = soup.find('table')
    table_body = table.find('tbody')

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        alldata.append([ele for ele in cols if ele]) # Get rid of empty values

    castletownbere = alldata[4]
    dingle = alldata[5]
    kilrush = alldata[12]
    fenit = alldata[15]
   #print(castletownbere)
    #print(dingle) 
    print(kilrush) 
   # print(fenit) 
    list = [castletownbere, dingle, kilrush, fenit]

    return kilrush

def processData(url=None):
    soup = get_soup(url)
    data_you_want = scraper(soup)
    f = open("TideData.txt","a+")
    f.write("\n" + data_you_want[2])
    tideData = data_you_want[2]
    print('initial: ' + str(tideData))

    scaledNo = float(tideData)*25
    print('scaledNo: ' + str(scaledNo))
    
    roundedNo = int(math.floor(int(scaledNo)))
    print('rounded: ' + str(roundedNo))


    midiout = rtmidi.MidiOut()
    available_ports = midiout.ports

    if available_ports:
        midiout.open_port(1)
    else:
        midiout.open_virtual_port("My virtual output")

    note_on = [0x90, roundedNo, 112] # channel 1, middle C, velocity 112
    note_off = [0x80, roundedNo, 0]
    midiout.send_message(note_on)
    time.sleep(0.5)
    midiout.send_message(note_off)
    print('MIDI OUT:' + str(roundedNo))
    del midiout

if __name__ == '__main__':
    url = 'http://webapps.marine.ie/observations/IWPData/default.aspx?ProjectID=3'
    rt = RepeatedTimer(300, processData, url)
    print('Starting scrape to midi')
