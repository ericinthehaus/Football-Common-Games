import pandas as pd
import os
import numpy as np
import requests 
from bs4 import BeautifulSoup
from io import StringIO
os.getcwd()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

################  Create the dataset from the FBref.com #####################################
def create_dataset(country = None, url_list = list()):
    
    if country is None: 
        return print("Enter a country: POR, ITA")
    elif country not in url_list.keys():
        return print("Enter a country we have in the list")
    else:  
        fbref_url = url_list[country][0]

    print(fbref_url)
    response = requests.get(fbref_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    # Find the table by ID
    table = soup.find("table", id=url_list[country][1])

    try: 
        df = pd.read_html(StringIO(str(table)))[0] 
        print("Table found!")
    except:
        print("Table not found.")

    return df[df['Score'].notnull()].reindex()


##############################################################################################

def setup_data(df_input):
    # split the Results column 
    df = df_input
    df[['home_score', 'away_score']] = df['Score'].str.split(r'\s*[-–—]\s*', expand=True).astype('int64')

    # create winner and loser columns to match with bottom section 
    conditions = [
        (df['home_score'] - df['away_score'] < 0),
        (df['home_score'] - df['away_score'] > 0),
        (df['home_score'] - df['away_score'] == 0)
        ]
    values = ['away', 'home', 'tie']
    result_home_points = [0, 1, 0.5]
    result_away_points = [1, 0, 0.5]

    # set new column to be either {home, away, tie}
    df['loc_winner'] = np.select(conditions, values, default="tie") 
    df['result_home_points'] = np.select(conditions, result_home_points)
    df['result_away_points'] = np.select(conditions, result_away_points)
    return df


# =======================================================
# -------------- Function with DataFrame ----------------
# =======================================================


def common_games(games, teamA, teamB): 
    homewinsA = games[(games['Home'] == teamA) & (games['loc_winner'] == 'home')]['Away']
    awaywinsA = games[(games['Away'] == teamA) & (games['loc_winner'] == 'away')]['Home']
    winsA = list(homewinsA) + list(awaywinsA)
    homelossesA = games[(games['Home'] == teamA) & (games['loc_winner'] == 'away')]['Away']   
    awaylossesA = games[(games['Away'] == teamA) & (games['loc_winner'] == 'home')]['Home'] 
    lossesA = list(homelossesA) + list(awaylossesA)    
    hometiesA = games[(games['Home'] == teamA) & (games['loc_winner'] == 'tie')]['Away']   
    awaytiesA = games[(games['Away'] == teamA) & (games['loc_winner'] == 'tie')]['Home'] 
    tiesA = list(hometiesA) + list(awaytiesA) 
    homewinsB = games[(games['Home'] == teamB) & (games['loc_winner'] == 'home')]['Away']
    awaywinsB = games[(games['Away'] == teamB) & (games['loc_winner'] == 'away')]['Home']
    winsB = list(homewinsB) + list(awaywinsB)
    homelossesB = games[(games['Home'] == teamB) & (games['loc_winner'] == 'away')]['Away']   
    awaylossesB = games[(games['Away'] == teamB) & (games['loc_winner'] == 'home')]['Home'] 
    lossesB = list(homelossesB) + list(awaylossesB)    
    hometiesB = games[(games['Home'] == teamB) & (games['loc_winner'] == 'tie')]['Away']   
    awaytiesB = games[(games['Away'] == teamB) & (games['loc_winner'] == 'tie')]['Home'] 
    tiesB = list(hometiesB) + list(awaytiesB)  

    teamA_games = list(winsA) + list(lossesA) + list(tiesA)
    teamB_games = list(winsB) + list(lossesB) + list(tiesB)

    df = pd.DataFrame({
        'opponent' : pd.Series(list(set(teamA_games).union(teamB_games)))
    })

    for x in range(0, len(df)):
        df.loc[x, "num_A"] = teamA_games.count(df['opponent'].iloc[x])
        df.loc[x, "num_B"] = teamB_games.count(df['opponent'].iloc[x])
        
        # A wins, losses, ties:
        df.loc[x, "A..."] = "|"
        df.loc[x, "wins_A"] = list(winsA).count(df['opponent'].iloc[x])
        df.loc[x, "losses_A"] = list(lossesA).count(df['opponent'].iloc[x])
        df.loc[x, "ties_A"] = list(tiesA).count(df['opponent'].iloc[x])

        # B wins, losses, ties
        df.loc[x, "B..."] = "|"
        df.loc[x, "wins_B"] = list(winsB).count(df['opponent'].iloc[x])
        df.loc[x, "losses_B"] = list(lossesB).count(df['opponent'].iloc[x])
        df.loc[x, "ties_B"] = list(tiesB).count(df['opponent'].iloc[x])

    min_games_played = 2
    df = df[(df["num_A"] >= min_games_played) & (df["num_B"] >= min_games_played)] 
    df['|'] = "|"
    df['adv'] = np.select([(df['wins_A']*3 + df['ties_A'] - df['wins_B']*3 - df['ties_B'] > 0),
                           (df['wins_A']*3 + df['ties_A'] - df['wins_B']*3 - df['ties_B'] < 0),
                           (df['wins_A']*3 + df['ties_A'] - df['wins_B']*3 - df['ties_B'] == 0)], 
                           [f"{teamA}", f"{teamB}", "even" ])
    

    h2h = ""
    if teamB in set(tiesA) and teamA in set(tiesB): 
        h2h = f"These two teams tied each other. Times: {tiesA.count(teamB)}"
    if teamB in set(winsA):
        h2h = h2h + f"\n{teamA} beat {teamB}. Times: {winsA.count(teamB)}"
    if teamA in set(winsB):
        h2h = h2h + f"\n{teamB} beat {teamA}. Times: {winsB.count(teamA)}"
    if teamB not in set(teamA_games) and teamA not in set(teamB_games): 
        h2h = ("they did NOT play this year.")

    xh2h = "\n---HEAD TO HEAD--- \n"

    # avoid error if these teams did not play each other: 
    if len(df) == 0: 
        f = open("results.txt", "w")
        f.write(str(f"{teamA} versus {teamB} \n"))
        f.write("These teams did not have common games\n")
        f.write(xh2h)
        f.write(h2h)
        f.close 
        return 

    # continue here if they did have common games
    win_percentage_A = (sum(df['wins_A']) + sum(df['ties_A']) / 2) / sum(df['num_A'])
    win_percentage_B = (sum(df['wins_B']) + sum(df['ties_B']) / 2) / sum(df['num_B'])
    x1 = str(f"{teamA} ({round(win_percentage_A, 2)}) versus {teamB} ({round(win_percentage_B, 2)}) \n")
    
    x2 = str(f"Both teams played against: minimum games played = {min_games_played} \n {df.sort_values(['num_A', 'num_B'])} \n \n")

    x3_a = str(f"Out of {sum(df['num_A'])} games, wins for {teamA} = {sum(df['wins_A'])} \n")
    x3_b = str(f"Out of {sum(df['num_B'])} games, wins for {teamB} = {sum(df['wins_B'])} \n")

    dff4 = list(df[(df["wins_A"] == df["num_A"]) & (df["wins_B"] == df["num_B"])]['opponent'])
    x4 = str(f"\n Both teams beat out:\n {dff4} \n")

    dff5 = list(df[(df["losses_A"] == df["num_A"]) & (df["losses_B"] == df["num_B"])]['opponent'])
    x5 = str(f"Both teams lost out to:\n {dff5} \n")

    dff6 = list(df[(df["ties_A"] > 0) & (df["ties_B"] > 0)]['opponent'])
    x6 = str(f"Both teams tied against:\n {dff6} \n")
    
    f = open("results.txt", "w")
    f.write(x1)
    f.write(x2)
    f.write(x3_a)
    f.write(x3_b)
    f.write(x4)
    f.write(x5)
    f.write(x6)
    f.write(xh2h)
    f.write(h2h)

    f.close()


###  Have fun here: 
## common_games(games=games, teamA=teamA, teamB=teamB)

def get_decision(games, teamA, teamB): 
    homewinsA = games[(games['Home'] == teamA) & (games['loc_winner'] == 'home')]['Away']
    awaywinsA = games[(games['Away'] == teamA) & (games['loc_winner'] == 'away')]['Home']
    winsA = list(homewinsA) + list(awaywinsA)
    homelossesA = games[(games['Home'] == teamA) & (games['loc_winner'] == 'away')]['Away']   
    awaylossesA = games[(games['Away'] == teamA) & (games['loc_winner'] == 'home')]['Home'] 
    lossesA = list(homelossesA) + list(awaylossesA)    
    hometiesA = games[(games['Home'] == teamA) & (games['loc_winner'] == 'tie')]['Away']   
    awaytiesA = games[(games['Away'] == teamA) & (games['loc_winner'] == 'tie')]['Home'] 
    tiesA = list(hometiesA) + list(awaytiesA) 
    homewinsB = games[(games['Home'] == teamB) & (games['loc_winner'] == 'home')]['Away']
    awaywinsB = games[(games['Away'] == teamB) & (games['loc_winner'] == 'away')]['Home']
    winsB = list(homewinsB) + list(awaywinsB)
    homelossesB = games[(games['Home'] == teamB) & (games['loc_winner'] == 'away')]['Away']   
    awaylossesB = games[(games['Away'] == teamB) & (games['loc_winner'] == 'home')]['Home'] 
    lossesB = list(homelossesB) + list(awaylossesB)    
    hometiesB = games[(games['Home'] == teamB) & (games['loc_winner'] == 'tie')]['Away']   
    awaytiesB = games[(games['Away'] == teamB) & (games['loc_winner'] == 'tie')]['Home'] 
    tiesB = list(hometiesB) + list(awaytiesB)  

    teamA_games = list(winsA) + list(lossesA) + list(tiesA)
    teamB_games = list(winsB) + list(lossesB) + list(tiesB)

    df = pd.DataFrame({
        'opponent' : pd.Series(list(set(teamA_games).union(teamB_games)))
    })

    for x in range(0, len(df)): 
        df.loc[x, "num_A"] = teamA_games.count(df['opponent'].iloc[x])
        df.loc[x, "num_B"] = teamB_games.count(df['opponent'].iloc[x])
        # wins:
        df.loc[x, "wins_A"] = list(winsA).count(df['opponent'].iloc[x])
        df.loc[x, "wins_B"] = list(winsB).count(df['opponent'].iloc[x])
        #losses:
        df.loc[x, "losses_A"] = list(lossesA).count(df['opponent'].iloc[x])
        df.loc[x, "losses_B"] = list(lossesB).count(df['opponent'].iloc[x])
        #losses:
        df.loc[x, "ties_A"] = list(tiesA).count(df['opponent'].iloc[x])
        df.loc[x, "ties_B"] = list(tiesB).count(df['opponent'].iloc[x])

    
    df = df[(df["num_A"] >= 2) & (df["num_B"] >= 2)]

    # avoid error if these teams did not play each other: 
    if len(df) < 2: 
        return 0 

    # continue here if they did have common games
    dff1 = [(sum(df['wins_A']) + sum(df['ties_A']) / 2) / sum(df['num_A']), (sum(df['wins_B']) + sum(df['ties_B']) / 2) / sum(df['num_B'])]
    x1 =  dff1[0] - dff1[1]

    if x1 > 0:
        return 1
    if x1 < 0:
        return -1
    else: 
        return 0

    
## SEASON LEADERS --------------------------------------------

def season_leaders(all_teams, games):
    df_total_decisions = pd.DataFrame({'team': all_teams})
    df_total_decisions['score'] = 0 

    for teamA in df_total_decisions['team']: 
        decisions = []

        for teamB in all_teams:
            dec = get_decision(games, teamA, teamB)
            decisions.append(dec)

        total = sum(decisions)

        df_total_decisions.loc[df_total_decisions['team'] == teamA, 'score'] = total  

    g = open("seasonLeaders.txt", "w")
    g.write("Season Leaders:\n")
    g.write(str(df_total_decisions.sort_values(by= 'score', ascending=False, ignore_index=True)))
    g.close()
    return df_total_decisions

# The end 

# -------------------------------------------------------------------------------------------------
## ---------------------  Figure out the importance of each game -----------------------------------
# -------------------------------------------------------------------------------------------------

wk = 2

def get_threshold(games, team_list, week, rank):
    games_df = games[games['Wk'] <= week]
    pts_array = []

    rank = rank 

    for x in range(0, len(team_list)):
        t = team_list[x]
        homewins = games_df[(games_df['Home'] == t) & (games_df['loc_winner'] == 'home')]['Away']
        awaywins = games_df[(games_df['Away'] == t) & (games_df['loc_winner'] == 'away')]['Home']
        wins = list(awaywins) + list(homewins)
        hometies = games_df[(games_df['Home'] == t) & (games_df['loc_winner'] == 'tie')]['Away']   
        awayties = games_df[(games_df['Away'] == t) & (games_df['loc_winner'] == 'tie')]['Home'] 
        ties = list(hometies) + list(awayties)  
        pts = 3*len(wins) + len(ties)
        pts_array.append(pts)

    df = pd.DataFrame({
        'team' : team_list,
        'pts'  : pts_array
    })

    df['rank'] = df['pts'].rank(method='first', ascending=False)

    z = int(df['pts'][df['rank'] == rank].iloc[0])

    return z

# done 

