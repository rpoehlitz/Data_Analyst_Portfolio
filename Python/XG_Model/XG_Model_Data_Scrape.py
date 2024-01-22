import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta


def get_Att_Def(cleanedDF,TeamName):
    teamAtt = cleanedDF.loc[TeamName]["Attack"]
    teamDeff = cleanedDF.loc[TeamName]["Defense"]

    return teamAtt, teamDeff

def get_fixtures(addDay,fix_URL):
    fixturesDF = pd.read_html("https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures")
    fixturesDF = fixturesDF[0]
    fixturesDF["Date"] = pd.to_datetime(fixturesDF["Date"])
    dayLimit = pd.Timestamp(date.today())+ timedelta(days=addDay)

    fixturesDF = fixturesDF[(fixturesDF["Date"] >= pd.Timestamp(date.today()))&(fixturesDF["Date"] < dayLimit)]
    fixturesDF = fixturesDF.drop(columns=['Attendance', 'Venue','Referee','Notes','Match Report',
                      'xG','xG.1','Day','Score',"Wk",'Time'])
    return fixturesDF


def simulate_match(avg_goals_team1, avg_goals_team2, num_simulations):
    results = {'Team1 Wins': 0, 'Team2 Wins': 0, 'Ties': 0}

    for _ in range(num_simulations):
        goals_team1 = np.random.poisson(avg_goals_team1)
        goals_team2 = np.random.poisson(avg_goals_team2)
        if goals_team1 > goals_team2:
            results['Team1 Wins'] += 1
        elif goals_team1 < goals_team2:
            results['Team2 Wins'] += 1
        else:
            results['Ties'] += 1

    percent_team1_wins = (results['Team1 Wins'] / num_simulations) * 100.0
    percent_team2_wins = (results['Team2 Wins'] / num_simulations) * 100.0
    percent_ties = (results['Ties'] / num_simulations) * 100.0

    return percent_team1_wins, percent_team2_wins, percent_ties


def get_fbrefData(URL):
    df = pd.read_html(URL)
    df = df[0]
    df = df.drop(columns=['Pts', 'Pts/MP','Last 5','Attendance','Top Team Scorer','Goalkeeper','Notes','xGD/90'])
    df['Goals Per Game'] = round(df.GF / df.MP,2)
    df['Goals Against Per Game '] = df.GA / df.MP 
    df['XG/G'] = df.xG / df.MP 
    df['XGA/GA'] = df.xGA / df.MP 
    df.set_index("Squad",inplace= True)
    return df

Link = 'https://fbref.com/en/comps/9/Premier-League-Stats#results2022-202391_home_away'
df = get_fbrefData(Link)


GoalsPerGame_AVG = df['Goals Per Game'].mean()
ConcedePerGame_Avg = df['Goals Against Per Game '].mean()


df["Attack"]= df['XG/G']/GoalsPerGame_AVG
df["Defense"]= df['XGA/GA']/ConcedePerGame_Avg


addDay = 3
fix_Link = "https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures"
fixturesDF = get_fixtures(addDay,fix_Link)


resultsDF = pd.DataFrame(columns = ["Home","Away","Date",
                                    "Home Win %","Away Win %", "Tie %",
                                    "Home Odds","Away Odds", "Tie Odds"])
num_simulations = 1000000
for index, row in fixturesDF.iterrows():
    Team1 = row["Home"]
    Team2 = row["Away"]
    matchDate = row["Date"]
    HomeTeamAtt,HomeTeamDef = get_Att_Def(df,Team1)
    AwayTeamAtt,AwayTeamDef = get_Att_Def(df,Team2)
    HT_avg_GOAL = HomeTeamAtt * AwayTeamDef * GoalsPerGame_AVG
    AT_avg_GOAL = HomeTeamDef * AwayTeamAtt * GoalsPerGame_AVG
    percent_team1_wins, percent_team2_wins, percent_ties = simulate_match(HT_avg_GOAL, AT_avg_GOAL, num_simulations)
    team1_odds = 1 / percent_team1_wins   * 100
    team2_odds = 1 / percent_team2_wins * 100
    tie_odds = 1 / percent_ties * 100
    resultsDF.loc[index] = [Team1, Team2, matchDate, 
                            percent_team1_wins, percent_team2_wins, percent_ties, 
                            team1_odds, team2_odds, tie_odds]
    




print(resultsDF)