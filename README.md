# FPL-Data-Analysis

Code to scrape, merge and analyse Fantasy Premier League (FPL) data

## Description

Fantasy Premier League (FPL) is a game played by millions of football fans globally. Players of the game choose real-life premier league goalkeepers, defenders, midfielders and forwards and are awarded points according to the performances, for example a goal scored by a defender is 6 points and an assist is worth 3 points. Each player has a cost which can change over time.

In order to choose the best FPL team, it would be useful to scrape and join data from different sources.

There are 3 steps to this process:
1. Scrape and join data from th FPL website
2. Scrape additional data from FBREF
3. From a mini-league,  Get standings and picks from all other teams, analyse the player data (FPL & FBREF joined) to inform decision making

##### Set up
1. Clone the repository to your lcoal machine
2. Install the reuired python packages with pip:
```
pip install pandas bs4 selenium webdriver_manager sqlalchemy psycopg2
```
3. Set up your PostgreSQL database and update the connection details in the script (replace placeholders in the CJDH_local_settings.py file).
4. Run the 3 scripts/notebooks in order


#### FPL-API-Scrape-Player-Data:
This script performs Extract, Transform, and Load (ETL) operations on Fantasy Premier League (FPL) data. The script fetches data from the FPL API, transforms it into a structured format, and loads it into a PostgreSQL database. The data includes player statistics, team information, fixture details, and player gameweek statistics.


<details>
<summary><strong>SDetails</strong></summary>

##### Script Details

The script fetches data, creates staging tables for the following tables in postgreSQL:

| Tables         | Description                                       |
| -------------  | -------------                                     |
| player         | Season summary info for each player               |
| teams          | Info for each team                                |
| fixtures       | Info for each match in the 2023/24 season         |
| player_details | Gameweek info for each player for every gameweek  |

##### Results

The script generates a CSV file named playergw_updated.csv containing joined data from the player gameweek table and player details data. This file can be found in the data directory.

</details>

#### FBREF-OOP-Web-Scrape
This script is designed to scrape football player statistics from the FBREF website for any chosen year and/or combination of stat types. It uses Selenium to automate web interactions and BeautifulSoup to parse HTML content. The data is then processed, cleaned, and stored in a PostgreSQL database for further analysis.

<details>
<summary><strong>Details</strong></summary>

##### Script Details
The script consists of several classes:
* Web_Scraper: Handles the web scraping process using Selenium and provides methods to fetch HTML content.
* League: Parses the HTML content to extract player data and column names.
* Player: Processes player data, fetches additional stats, and organizes the data for each player.
* main: Brings together all functions, scrapes data for multiple seasons, and stores the data in a PostgreSQL database.

</details>

#### FPL-League-Analysis:
This repository contains Python code for analyzing Fantasy Premier League data, fetching data from the FPL API, processing and transforming the data, and performing various analyses to gain insights into player performance, team composition, and more.

<details>
<summary><strong>Details</strong></summary>

##### Script Details
The code performs the following tasks:
* Fetches league standings data from the FPL API.
* Collects member IDs and player names from the league data.
* Determines the maximum gameweek available for each member.
* Retrieves member's picks data for each gameweek.
* Loads data into a PostgreSQL database.
* Performs analysis to provide insights on team composition, player selections, and more.

##### Results

The code generates CSV files containing gameweek-level analysis and member picks data:
* DIVX_gameweek_updated.csv: Gameweek-level analysis with formation, captain selection, and more.
* DIVX_picks_updated.csv: Member's picks data for each gameweek.
* The notebook takes approx. 5 minutes to run for a league with 17 members

</details>


## Packages used
* pandas
* numpy
* json
* requests
* webdriver_manager
* bs4
* sqlalchemy
* psycopg2
* threading
* concurrent.futures


## Contributing
Contributions to this project are welcome. Feel free to submit pull requests for improvements, bug fixes, or new features.

## Acknowledgment

Links
* https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19