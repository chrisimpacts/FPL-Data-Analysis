import pandas as pd
import time
from datetime import datetime
import bs4 as bs
import threading
from concurrent.futures import ThreadPoolExecutor

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

version='170823'

threadLocal = threading.local()

class Web_Scraper:
    """
    Web-Scraper class contains the methods needed to scrape FBREF data
    """
    def __init__(self, 
                 url_to_scrape: str
                 ): 
        """
        Constructor for Web-Scraper.
        Args:
            url_to_scrape (str): The URL to scrape data from.
        """
        self.url = url_to_scrape
    def get_driver(self):
        # Using Chrome WebDriver, get driver
        # Avoid creating a new instance of the driver every time by using getattr 
        self.driver = getattr(threadLocal, 'driver', None)
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options) #self.driver = webdriver.Chrome(self.driver_url,chrome_options=chrome_options) #update driver @ #https://sites.google.com/chromium.org/driver/downloads?authuser=0
            setattr(threadLocal, 'driver', self.driver)
        return self.driver
    def parse(self):
        # Use driver to get source code
        driver = Web_Scraper.get_driver(self)
        driver.get(self.url)
        self.sourceCode=driver.page_source
        return  self.sourceCode
    def url_to_soup(self):
        # Create a soup object from the source code
        soup = bs.BeautifulSoup(Web_Scraper.parse(self),'html.parser')
        return soup
    
class League:
    """
    League class contains the methods needed to transform URL soup to a dataframe
    """
    def __init__(self, soup): 
        """
        Constructor for League class.
        Args:
            soup (str): BeautifulSoup object
        """
        self.soup = soup
        self.table = self.soup.find('table',attrs={"id":"stats_standard"})
    
    def ps_table_to_rows(self):
        """
        ps_table_to_rows method get the names/links for all players from this URL
        Returns:
            names_links (dict): A dict of the player names and links to the player pages 
        """
        names_links={}
        self.table_rows = self.table.find_all('tr') #table rows
        for tr in self.table_rows:
            for td in tr.find_all('td',attrs={"data-stat": "player"}):
                for a in td.find_all('a',href=True):
                    link=a['href']
                    name=a.text
                    names_links[name]=link
        self.names_links = names_links

        allrows=[]
        row=[]
        for tr in self.table_rows:
            td = tr.find_all('td')
            row.append(tr.text for tr in td)
            allrows.append(row)
        self.allrows = allrows
        return self.allrows

    def ps_table_columns(self):
        """
        ps_table_columns method get the names of the columns from this URL
        Returns:
            cols (list): A list of data column names
        """
        cols=[]
        for tx in self.table.find_all('th',attrs={"scope": "col"}):
            cols.append(tx.get('data-stat'))
        self.cols = cols
        return self.cols
    
    def ps_table_to_df(self):
        """
        ps_table_to_df method uses table rows and columns to create a dataframe
        Returns:
            df (DataFrame): DataFrame of Player Data
            names_links (dict): A dict of the player names and links to the player pages 
        """
        allrows=League.ps_table_to_rows(self)
        allcols=League.ps_table_columns(self)
        self.df = pd.DataFrame(allrows[0][2:], columns = allcols[1:])
        return self.df, self.names_links
    
class Player:
    """
    Player class contains the methods needed to get all the data for every player
    """
    def __init__(self, 
                 names_links: dict,
                 year: str): 
        """
        Constructor for Player class.
        Args:
            names_links (dict): A dict of player names and links to their stat pages
            year (str): looping over a list of years, this specifies which year
        """
        self.names_links = names_links
        self.first5pairs = {k: self.names_links[k] for k in list(self.names_links)[:5]}
        self.year = year

    def find_p_name(self, soup):
        #get player name from URL
        name=[]
        for div in soup.find_all('div',attrs={"id":"meta"}):
            for h1 in div.find_all('h1'):
                name.extend(h1.text.strip().splitlines())
        return name[0]

    def find_season(self, soup):
        #get season (digits only) from URL
        name=[]
        for div in soup.find_all('div',attrs={"id":"info"}):
            for h1 in div.find_all('h1'):
                name.extend(h1.text.strip().splitlines())
        return ''.join(c for c in name[1] if c.isdigit()) #returns only digits

    def get_player_data(self,end,year,stat):
        """
        get_player_data method returns all rows of data from the given URL soup.
        Args:
            end (str): The end of the URL for this player
            year (str): The year
            stat (str): The stat type to scrape from
        Returns:
            playerdata (list): List of lists of appended rows of player data  
        """
        playerdata=[]
        url="https://fbref.com/"+str(end)
        url_name=url.split('/')[-1]
        url_code=url.split('/')[-2]
        self.matchlog_url="https://fbref.com/en/players/"+str(url_code)+"/matchlogs/"+str(year)+"/"+str(stat)+"/"+str(url_name)+"-Match-Logs"
    #For each url, parse html
        soup = Web_Scraper(self.matchlog_url).url_to_soup() #self.driver_url, 
    #Find table in the html
        table = soup.find('table', id="matchlogs_all") 
        table_rows = table.find_all('tr') #table rows
    #Get rows from the table
        link=[]
        date=[]
        p_name=Player.find_p_name(self, soup) #defined function
        season=Player.find_season(self, soup) #defined function
        for tr in table_rows:
            row = [] 
    #Get dates for each row
            for th in tr.find_all('th',attrs={"data-stat": "date"}):
                for a in th.find_all('a',href=True):
                    link=a['href']
                    date=a.text
            td = tr.find_all('td')
            row.extend([tr.text for tr in td])
            for item in [p_name,season,date,"https://fbref.com/"+str(link),url_code]:
                row.insert(0,item)
            playerdata.append(row)
        return playerdata[2:]
    
    #Find the columns names for data-stat of each column in row 0
    def cols_of_first_row(self, url):
        self.soup_colnames = Web_Scraper(url).url_to_soup() #self.driver_url, #This might not be needed as it can use a soup from the most recent loop
        cols=[]
        row=self.soup_colnames.find('tr',attrs={"data-row":"0"})
        td=row.find_all('td')
        for i in td:
            try:
                cols.append(i.get('data-stat'))
            except AttributeError as err:
                pass
        #add extra columns:
        for item in ['name','season','date','link','code']:
                cols.insert(0,item)
        self.cols = cols
        print("Number of cols: "+str(len(self.cols)))
        return self.cols

    def stat_to_df(self, stat): #, stat:str #Get all stats for all players for the first stat type: summary
        """
        stat_to_df method loops through each stat and each URL in names_links 
            and runs get_player_data method, stacking the data in allplayers before finally
            assembling the df
        Args:
            stat (str): The stat type to scrape from
        Returns:
            df (DataFrame): dataframe of all players for that stat type 
        """
        start=time.perf_counter()
        self.stat = stat
        allplayers = []
        for end in self.names_links.values(): #names_links.values() #first5pairs.values()
            try:
                start_p=time.perf_counter()
                player=Player.get_player_data(self,end,self.year,self.stat) #single year
                allplayers.extend(player)
                finish_p=time.perf_counter()
                print(f"Getting data for {end} was finished in {(finish_p-start_p)} second(s)")
            except AttributeError as e: 
                print(e)
                continue
        print(f"df{self.stat} finished!")
        
        #Create DF of all players for that stat
        #Get colnames from: https://fbref.com/en/players/4806ec67/matchlogs/2020-2021/summary/Jordan-Pickford-Match-Logs
        colnames=self.cols_of_first_row(url="https://fbref.com/en/players/4806ec67/matchlogs/"+str(self.year)+"/"+str(self.stat)+"/Jordan-Pickford-Match-Logs")
        #colnames=Player.cols_of_first_row(self, url="https://fbref.com/en/players/4806ec67/matchlogs/"+str(self.year)+"/"+str(self.stat)+"/Jordan-Pickford-Match-Logs")
        df=pd.DataFrame(allplayers,columns=colnames)
        finish=time.perf_counter()
        print("df"+str(self.stat)+" shape: ",str(df.shape),f'Finished in {round(((finish-start)/60),2)} minute(s)')
        return df

def add_new_stat_columns(df, year, stat, names_links):
        #Each time a new stat type is added, new columns need to be added to the column axis
        temp_df = Player(names_links,year).stat_to_df(stat)
        cols_to_use = list(temp_df.columns.difference(df.columns))
        temp_df['name_link'] = temp_df[['name','link']].apply(tuple, axis=1)
        cols_to_use.append('name_link')

        df=df.merge(temp_df[cols_to_use], how='left', on='name_link')
        del temp_df
        return df

def main():
    #main brings together all functions, collates the dfs into one df and saves the df to file
    year_list=['2023-2024']#['2022-2023','2021-2022','2020-2021'] #if 17/18 stats wanted also: ['2017-2018','2018-2019','2019-2020','2020-2021'] #20-21 season summary is called "https://fbref.com/en/comps/9/stats/Premier-League-Stats" but the matchlogs are still in the 2020-2021 format
    list_of_stat_types=['passing','passing_types','gca','defense','possession','misc']#'summary'

    for i, year in enumerate(year_list):
        # season_links={}
        url_to_scrape=f"https://fbref.com/en/comps/9/{year}/stats/{year}-Premier-League-Stats"
        print(url_to_scrape)
        ws = Web_Scraper(url_to_scrape)#driver_url,
        soup = ws.url_to_soup()
        df, names_links = League(soup).ps_table_to_df()

        #get first stat for first year
        dfsummary = Player(names_links, year).stat_to_df('summary') #names_links are specific to that season
        dfsummary['name_link'] = dfsummary[['name','link']].apply(tuple, axis=1) # change to code_link
        #get other stats for first year, concat to dfsummary then concat additional dfdata to dfdata
        dfdata = dfsummary
        for stat in list_of_stat_types:
            dfdata = add_new_stat_columns(dfdata, year, stat, names_links)
        #once all stats are added, dfdata is seasondata
        if i == 0:
            seasondata = dfdata
        #for following years, concat dfdata to previous season's data
        else:
            seasondata = pd.concat([seasondata, dfdata],axis=0)
            print(f"End of this year's scrape, seasondata shape: {seasondata.shape}")

    print(seasondata.shape)
    seasondata

    #drop duplicates
    seasondata=seasondata.drop_duplicates(subset=['name_link']).reset_index(drop=True)
    seasondata['scrape_datetime'] = datetime.now()
    print("Final shape: ",seasondata.shape)

    #Export data to excel
    dfcsv=seasondata
    dfcsv.to_csv('data/fbrefdata23_'+str(version)+'.csv', index=False)
    dfcsv.to_csv('data/fbrefdata23_OOP_updated.csv', index=False)

    #Insert into PSQL
    from sqlalchemy import create_engine, text
    from datetime import datetime
    import psycopg2 # python -> psql connection
    import psycopg2.extras

    #Import secret settings
    import CJDH_local_settings
    dbname = CJDH_local_settings.local_settings['TRDL_PSQL_Analysis']['dbname']
    user = CJDH_local_settings.local_settings['TRDL_PSQL_Analysis']['user']
    password = CJDH_local_settings.local_settings['TRDL_PSQL_Analysis']['password']
    host = "localhost"
    port = 5432

    #Create connection to psql via psycopg2 & sqlalchemy
    connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'
    engine = create_engine(connection_string)
    engine.autocommit = True  # read documentation understanding when to Use & NOT use # changes will be automatically committed to the database after each statement is executed.

    data20_22 = pd.read_csv('data/fbrefdata20-22_OOP_updated.csv')
    data23 = pd.read_csv('data/fbrefdata23_OOP_updated.csv')
    fbref = pd.concat([data20_22,data23])

    #Create staging table for player data 
    def create_staging_table_fbref(cursor):
    cursor.execute(text("""
        DROP TABLE IF EXISTS fbref CASCADE;
        CREATE UNLOGGED TABLE fbref (
            code           NUMERIC,
            link           TEXT,
            date           TIMESTAMP,
            season         NUMERIC,
            name           TEXT,
            dayofweek      TEXT,
            comp           TEXT,
            round          TEXT,
            venue          TEXT,
            result         TEXT,
            team           TEXT,
            opponent       TEXT,
            game_started   TEXT,
            position       TEXT,
            minutes        NUMERIC,
            goals          NUMERIC,
            assists        NUMERIC,
            pens_made      NUMERIC,
            pens_att       NUMERIC,
            shots          NUMERIC,
            shots_on_target NUMERIC,
            cards_yellow   NUMERIC,
            cards_red      NUMERIC,
            touches        NUMERIC,
            tackles        NUMERIC,
            interceptions  NUMERIC,
            blocks         NUMERIC,
            xg             NUMERIC,
            npxg           NUMERIC,
            xg_assist      NUMERIC,
            sca            NUMERIC,
            gca            NUMERIC,
            passes_completed NUMERIC,
            passes         NUMERIC,
            passes_pct     NUMERIC,
            progressive_passes NUMERIC,
            carries        NUMERIC,
            progressive_carries NUMERIC,
            take_ons       NUMERIC,
            take_ons_won   NUMERIC,
            match_report   NUMERIC,
            name_link      NUMERIC,
            assisted_shots NUMERIC,
            crosses_into_penalty_area NUMERIC,
            pass_xa        NUMERIC,
            passes_completed_long    NUMERIC,
            passes_completed_medium  NUMERIC,
            passes_completed_short   NUMERIC,
            passes_into_final_third  NUMERIC,
            passes_into_penalty_area NUMERIC,
            passes_long      NUMERIC,
            passes_medium     NUMERIC,
            passes_pct_long     NUMERIC,
            passes_pct_medium     NUMERIC,
            passes_pct_short     NUMERIC,
            passes_progressive_distance     NUMERIC,
            passes_short     NUMERIC,
            passes_total_distance     NUMERIC,
            corner_kicks     NUMERIC,
            corner_kicks_in     NUMERIC,
            corner_kicks_out     NUMERIC,
            corner_kicks_straight     NUMERIC,
            crosses     NUMERIC,
            passes_blocked     NUMERIC,
            passes_dead     NUMERIC,
            passes_free_kicks     NUMERIC,
            passes_live     NUMERIC,
            passes_offsides     NUMERIC,
            passes_switches     NUMERIC,
            through_balls     NUMERIC,
            throw_ins     NUMERIC,
            gca_defense     NUMERIC,
            gca_fouled     NUMERIC,
            gca_passes_dead     NUMERIC,
            gca_passes_live     NUMERIC,
            gca_shots     NUMERIC,
            gca_take_ons     NUMERIC,
            sca_defense     NUMERIC,
            sca_fouled     NUMERIC,
            sca_passes_dead     NUMERIC,
            sca_passes_live     NUMERIC,
            sca_shots     NUMERIC,
            sca_take_ons     NUMERIC,
            blocked_passes     NUMERIC,
            blocked_shots     NUMERIC,
            challenge_tackles     NUMERIC,
            challenge_tackles_pct     NUMERIC,
            challenges     NUMERIC,
            challenges_lost     NUMERIC,
            clearances     NUMERIC,
            errors     NUMERIC,
            tackles_att_3rd     NUMERIC,
            tackles_def_3rd     NUMERIC,
            tackles_interceptions     NUMERIC,
            tackles_mid_3rd     NUMERIC,
            tackles_won     NUMERIC,
            carries_distance     NUMERIC,
            carries_into_final_third     NUMERIC,
            carries_into_penalty_area     NUMERIC,
            carries_progressive_distance     NUMERIC,
            dispossessed     NUMERIC,
            miscontrols     NUMERIC,
            passes_received     NUMERIC,
            progressive_passes_received     NUMERIC,
            take_ons_tackled     NUMERIC,
            take_ons_tackled_pct     NUMERIC,
            take_ons_won_pct     NUMERIC,
            touches_att_3rd     NUMERIC,
            touches_att_pen_area     NUMERIC,
            touches_def_3rd     NUMERIC,
            touches_def_pen_area     NUMERIC,
            touches_live_ball     NUMERIC,
            touches_mid_3rd     NUMERIC,
            aerials_lost     NUMERIC,
            aerials_won     NUMERIC,
            aerials_won_pct     NUMERIC,
            ball_recoveries     NUMERIC,
            cards_yellow_red     NUMERIC,
            fouled     NUMERIC,
            fouls     NUMERIC,
            offsides     NUMERIC,
            own_goals     NUMERIC,
            pens_conceded     NUMERIC,
            pens_won     NUMERIC,
            scrape_datetime     TIMESTAMP
        );"""))
    # creating our schema  and sending the table to psql
    with engine.connect() as cursor:
        create_staging_table_fbref(cursor)
    fbref.to_sql('fbref', con=engine, if_exists='replace',index=False)

if __name__ == '__main__':
    start=time.perf_counter()
    with ThreadPoolExecutor(max_workers=6) as pool:
        future = pool.submit(main())
    finish=time.perf_counter()
    print(f'Finished in {round(((finish-start)/60),2)} minute(s)')
    #Last run (2020-22): Finished in 759.83 minute(s)
    #Last run (2023): Finished in 141.22 minutes