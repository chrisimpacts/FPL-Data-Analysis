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
<summary><strong>Details</strong></summary>

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

A summary of the insight provided is where transfer suggestions are made, maximising the difference between the expected gain of bringing in a new player relative to the other members of my mini-league (expected points * 1-ownership rate) minus the expected loss of taking out a player relative to the other members of my mini-league (expected points * ownership rate). In GW1 this table looked like this:

| web_name    | element | element_type | now_cost | multiplier | multiplier_myteam | own_rate | ep_next | expected_gain | expected_loss_on_transfer | affordable_suggested_transfer | suggested_transfer_gain |
|-------------|---------|--------------|----------|------------|-------------------|----------|---------|---------------|---------------------------|-------------------------------|------------------------|
| Chilwell    | 195     | 2            | 56       | 4.0        | 1                 | 0.2500   | 2.6     | 1.95000       | 0.65000                   | [Rúben, 0.0, 3.1, 3.1, 2.45] | 2.45                   |
| Watkins     | 60      | 4            | 80       | 3.0        | 1                 | 0.1875   | 2.6     | 2.11250       | 0.48750                   | [Darwin, 0.062, 2.9, 2.72, 2.23] | 2.23                   |
| B.Fernandes | 373     | 3            | 85       | 5.0        | 1                 | 0.3125   | 3.4     | 2.33750       | 1.06250                   | [Ødegaard, 0.062, 3.4, 3.19, 2.12] | 2.12                   |
| Martinelli  | 12      | 3            | 80       | 6.0        | 1                 | 0.3750   | 3.3     | 2.06250       | 1.23750                   | [Havertz, 0.062, 3.1, 2.91, 1.67] | 1.67                   |
| Onana       | 597     | 1            | 50       | 7.0        | 1                 | 0.4375   | 3.7     | 2.08125       | 1.61875                   | [Ramsdale, 0.125, 3.7, 3.24, 1.62] | 1.62                   |
| Rashford    | 396     | 3            | 90       | 8.0        | 1                 | 0.5000   | 3.5     | 1.75000       | 1.75000                   | [Ødegaard, 0.062, 3.4, 3.19, 1.44] | 1.44                   |
| Estupiñan   | 131     | 2            | 51       | 10.0       | 1                 | 0.6250   | 2.4     | 0.90000       | 1.50000                   | [Walker, 0.0, 2.8, 2.8, 1.3] | 1.30                   |
| Gabriel     | 5       | 2            | 50       | 9.0        | 1                 | 0.5625   | 2.8     | 1.22500       | 1.57500                   | [Walker, 0.0, 2.8, 2.8, 1.22] | 1.22                   |
| Beyer       | 160     | 2            | 40       | 0.0        | 0                 | 0.0000   | 0.0     | 0.00000       | 0.00000                   | [Chambers, 0.0, 1.0, 1.0, 1.0] | 1.00                   |
| Turner      | 28      | 1            | 40       | 0.0        | 0                 | 0.0000   | 1.5     | 0.00000       | 0.00000                   | [Areola, 0.0, 1.0, 1.0, 1.0] | 1.00                   |
| Mubama      | 538     | 4            | 45       | 0.0        | 0                 | 0.0000   | 1.0     | 0.00000       | 0.00000                   | [Archer, 0.0, 1.0, 1.0, 1.0] | 1.00                   |
| Mitoma      | 143     | 3            | 65       | 12.0       | 1                 | 0.7500   | 2.3     | 0.57500       | 1.72500                   | [Gibbs-White, 0.0, 2.7, 2.7, 0.98] | 0.98                   |
| Baldock     | 473     | 2            | 40       | 1.0        | 0                 | 0.0625   | 0.5     | -0.03125      | 0.03125                   | [Chambers, 0.0, 1.0, 1.0, 0.97] | 0.97                   |
| Saka        | 19      | 3            | 86       | 12.0       | 1                 | 0.7500   | 3.4     | 0.85000       | 2.55000                   | [Ødegaard, 0.062, 3.4, 3.19, 0.64] | 0.64                   |
| Haaland     | 355     | 4            | 140      | 26.0       | 2                 | 1.6250   | 4.5     | 1.68750       | 7.31250                   | [nan, nan, nan, nan, nan] | NaN                    |

From this table I can tell that the highest gain in expected points would be in transferring out Ben Chilwell for Ruben Dias

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