# FPL-Data-Analysis

Code to scrape, merge and analyse Fantasy Premier League (FPL) data

## Description

Fantasy Premier League (FPL) is a game played by millions of football fans globally. Players of the game choose real-life premier league goalkeepers, defenders, midfielders and forwards and are awarded points according to the performances, for example a goal scored by a defender is 6 points and an assist is worth 3 points. Each player has a cost which can change over time.

In order to choose the best FPL team, it would be useful to scrape and join data from different sources.

There are 3 steps to this process:
1. Scrape and join data from th FPL website
2. Scrape additional data from FBREF
3. From a mini-league,  Get standings and picks from all other teams, analyse the player data (FPL & FBREF joined) to inform decision making


### FPL-API-Scrape-Player-Data:
> Use FPL API to scrape 2023 data, join together in postgreSQL tables:

| Tables         | Description                                       |
| -------------  | -------------                                     |
| player         | Season summary info for each player               |
| teams          | Info for each team                                |
| fixtures       | Info for each match in the 2023/24 season         |
| player_details | Gameweek info for each player for every gameweek  |

### FBREF-OOP-Web-Scrape
> Get FBREF data for 2020-2023 (Run in parallel)
> Join with FPL API data

### FPL-League-Analysis:
> Analyse data from any FPL mini-league given the league code

## Packages used
> json
> requests
> pandas
> numpy
> sqlalchemy
> psycopg2

## Acknowledgment

Links
* https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19