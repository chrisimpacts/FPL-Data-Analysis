import pandas as pd
import numpy as np
import time

version='120623_fpl_fbref_v2'

from lxml import html
import bs4 as bs
from selenium import webdriver
import threading
from multiprocessing.pool import ThreadPool, Pool

start=time.perf_counter()

threadLocal = threading.local()

def get_driver():
    driver = getattr(threadLocal, 'driver', None)
    if driver is None:
        #Options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        #Get Source Code
        driver = webdriver.Chrome("ChromeDriver/chromedriver.exe"
                                ,chrome_options=chrome_options)#service=Service(ChromeDriverManager().install()))#webdriver.Chrome(ChromeDriverManager().install()) #webdriver.Chrome() #default path is python/FPL/... update driver @ #https://sites.google.com/chromium.org/driver/
        setattr(threadLocal, 'driver', driver)
    return driver

def parse(url):
    driver = get_driver()
    driver.get(url)
    sourceCode=driver.page_source
    return  sourceCode

def url_to_soup(url):
    soup = bs.BeautifulSoup(parse(url),'html.parser')
    return soup

#Player Summary List
    # Create names:links - For each row in the Player Summary table
    # get a dict of playername:links
def table_to_names_links(table):
    names_links={}
    table_rows = table.find_all('tr') #table rows
    for tr in table_rows:
        for td in tr.find_all('td',attrs={"data-stat": "player"}):
            for a in td.find_all('a',href=True):
                link=a['href']
                name=a.text
                names_links[name]=link
    return names_links

def ps_table_to_df(table):
    allrows=ps_table_to_rows(table) #defined function
    allcols=ps_table_columns(table) #defined function

    df = pd.DataFrame(allrows[0][2:], columns = allcols[1:])
    return df

def ps_table_to_rows(table):
    table_rows = table.find_all('tr') #table rows
    table_headers = table.find_all('th') #table headings

    allrows=[]
    row=[]
    for tr in table_rows:
        td = tr.find_all('td')
        row.append(tr.text for tr in td)
        allrows.append(row)
    # print(len(row))
    return allrows

def ps_table_columns(table):
    cols=[]
    for tx in table.find_all('th',attrs={"scope": "col"}):
        cols.append(tx.get('data-stat'))#also: data-tip 
    # print(len(cols))
    return cols

url="https://fbref.com/en/comps/9/stats/Premier-League-Stats"
soup=url_to_soup(url)
ps_table=soup.find('table',attrs={"id":"stats_standard"})
# df=ps_table_to_df(ps_table)
# print(df)
names_links=table_to_names_links(ps_table)

#Using all links for the first player, produce rows of a dataframe
def find_p_name(soup):
    name=[]
    for div in soup.find_all('div',attrs={"id":"meta"}):
        # print("div example")
        for h1 in div.find_all('h1'):#div.find_all('h1',attrs={"itemprop":"name"}):
            name.extend(h1.text.strip().splitlines())
    return name[0]

def find_season(soup):
    name=[]
    for div in soup.find_all('div',attrs={"id":"info"}):
        for h1 in div.find_all('h1'):#div.find_all('h1',attrs={"itemprop":"name"}):
            name.extend(h1.text.strip().splitlines())
    return ''.join(c for c in name[1] if c.isdigit()) #returns only digits

def get_that_year(end,year,stat):
    yeardata=[]
    url="https://fbref.com/"+str(end)
    url_name=url.split('/')[-1]
    url_code=url.split('/')[-2]
    matchlog_url="https://fbref.com/en/players/"+str(url_code)+"/matchlogs/"+str(year)+"/"+str(stat)+"/"+str(url_name)+"-Match-Logs"
    print(matchlog_url)

#For each url, parse html
    soup = bs.BeautifulSoup(parse(matchlog_url))

#Find table in the html        
    table = soup.find('table', id="matchlogs_all")
    table_rows = table.find_all('tr') #table rows

#Get rows from the table
    link=[]
    date=[]   
    
    p_name=find_p_name(soup) #defined function
    season=find_season(soup) #defined function
    
    for tr in table_rows:
        row = [] 
        
#Get dates for each row
        for th in tr.find_all('th',attrs={"data-stat": "date"}):
            for a in th.find_all('a',href=True):
                link=a['href']
                date=a.text
        td = tr.find_all('td')
        
        row.extend([tr.text for tr in td])
        for item in [p_name,season,date,"https://fbref.com/"+str(link)]:
            row.insert(0,item)

        yeardata.append(row)
        
    print(p_name," ",season," ",stat)
    print("\n")
    return yeardata[2:]

#for testing:
first5pairs = {k: names_links[k] for k in list(names_links)[:5]}

#Find the columns names for data-stat of each column in row 0
def cols_of_first_row(url):
    soup=url_to_soup(url) #This might not be needed as it can use a soup from the most recent loop
    cols=[]
    row=soup.find('tr',attrs={"data-row":"0"})
    
    td=row.find_all('td')
    for i in td:
        try:
            cols.append(i.get('data-stat'))
        except AttributeError as err:
            pass
    #add extra columns:
    for item in ['name','season','date','link']:
            cols.insert(0,item)
    print("Number of cols: "+str(len(cols)))
    # print(cols)
    return cols

def stat_to_df(stat): #Get all stats for all players for the first stat type: summary
    start=time.perf_counter()
    player=[]

    for end in names_links.values(): #: # #names_links.values() #first2pairs.values()
        for year in year_list:
            try:
                start_p=time.perf_counter()
                yeardata=[]
                yeardata=get_that_year(end,year,stat)
                player.extend(yeardata)
                finish_p=time.perf_counter()
                print("Getting data for ",end," was ",f'finished in {(finish_p-start_p)} second(s)')
            except: 
                continue
    print("df"+str(stat)+" finished!")
    
    #Get colnames from: https://fbref.com/en/players/4806ec67/matchlogs/2020-2021/summary/Jordan-Pickford-Match-Logs
    colnames=cols_of_first_row("https://fbref.com/en/players/4806ec67/matchlogs/"+str(year)+"/"+str(stat)+"/Jordan-Pickford-Match-Logs")
    
    df=pd.DataFrame(player,columns=colnames)
    finish=time.perf_counter()
    print("df"+str(stat)+" shape: ",str(df.shape),f'Finished in {round(((finish-start)/60),2)} minute(s)')
    
    return df


year_list=['2022-2023','2021-2022','2020-2021'] #if 17/18 stats wanted also: ['2017-2018','2018-2019','2019-2020','2020-2021'] #20-21 season summary is called "https://fbref.com/en/comps/9/stats/Premier-League-Stats" but the matchlogs are still in the 2020-2021 format
list_of_stat_types=['passing','passing_types','gca','defense','possession','misc']#'summary'

#Look at how to multithread these: #how to multithread with requests?

dfsummary=stat_to_df('summary')
#Create variable linking all dataframes
dfsummary['name_link'] = dfsummary[['name','link']].apply(tuple, axis=1)

dfdata=dfsummary
for stat in list_of_stat_types:
    temp_df = stat_to_df(stat)
    cols_to_use = list(temp_df.columns.difference(dfdata.columns))
    print(f"Adding {len(cols_to_use)} coloumns: {cols_to_use}")
    temp_df['name_link'] = temp_df[['name','link']].apply(tuple, axis=1)
    cols_to_use.append('name_link')
    print(f"df{stat} shape: ",temp_df[cols_to_use].shape)
    dfdata=dfdata.merge(temp_df[cols_to_use], how='left', on='name_link')
    del temp_df

#drop duplicates
print(dfdata.shape)
dfdata=dfdata.drop_duplicates(subset=['name_link'])
print("Final shape: ",dfdata.shape)

#Export data to excel
dfcsv=dfdata
dfcsv.to_csv('data/fbrefdata_'+str(version)+'.csv')
dfcsv.to_csv('data/fbrefdata_updated.csv')


finish=time.perf_counter()
print(f'Finished in {round(((finish-start)/60),2)} minute(s)')


#Betting Data

import csv
import requests
import io

def url_to_df(csv_url):
    req = requests.get(csv_url)
    url_content = req.content
    RawData = pd.read_csv(io.StringIO(url_content.decode('utf-8')))
    return RawData

files=[]

bettingurl="https://www.football-data.co.uk/englandm.php"
soup=url_to_soup(bettingurl)

links=soup.find_all('a')

for link in links:
    if link.text=="Premier League":
        try:
            print("https://www.football-data.co.uk/"+str(link.attrs["href"]))
            csv_url="https://www.football-data.co.uk/"+str(link.attrs["href"])
            df=url_to_df(csv_url)
            df['season']=str(csv_url.split("/")[4])
            files.append(df)
            print(df.shape)
        except:
            break     
betting_data = pd.concat(files, axis=0)
#Notes = https://www.football-data.co.uk/notes.txt

#Export data to excel
dfcsv=betting_data
dfcsv.to_csv('data/BettingData_'+str(version)+'.csv')
dfcsv.to_csv('data/BettingData_updated.csv')


#SPI Fixture Difficulty

# spi_matches.csv contains match-by-match SPI ratings and forecasts back to 2016.
csv_url="https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv"
spi_matches=url_to_df(csv_url)
#filter df to just 2020 & 2021 seasons of the premier league
filtered=(spi_matches['season']>=2020)&(spi_matches['league_id']==2411)
spi_matches=spi_matches[filtered].reset_index()
#Ready to merge with the xPoints dataset
spi_matches.to_csv('data/spi_matches_prem_updated'+str(version)+'.csv')
spi_matches.to_csv('data/spi_matches_prem_updated.csv')

#Can we do this again, but only as an 'update'
    #Re do the code so that it adds data line-by-line / openwith
    #Look at the newest date in the old file
    #Only take rows after that date
    #Then add it to the current data

#Create a database
    #Collect data in separate databases
    #Merge with SQL at the very end