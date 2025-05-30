import pandas as pd
import functions
import matplotlib.pyplot as plt
import numpy as np
import argparse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

url_list = {
    "POR" : ["https://fbref.com/en/comps/32/schedule/Primeira-Liga-Scores-and-Fixtures",
             "sched_2024-2025_32_1"], 
    "ITA" : ["https://fbref.com/en/comps/11/schedule/Serie-A-Scores-and-Fixtures",
             "sched_2024-2025_11_1"],
    "ENG" : ["https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures",
             "sched_2024-2025_9_1"],
    "ESP" : ["https://fbref.com/en/comps/12/schedule/La-Liga-Scores-and-Fixtures",
             "sched_2024-2025_12_1"],
    "GER" : ["https://fbref.com/en/comps/20/schedule/Bundesliga-Scores-and-Fixtures",
             "sched_2024-2025_20_1"],
    "NWSL" : ["https://fbref.com/en/comps/182/schedule/NWSL-Scores-and-Fixtures",
              "sched_2025_182_1"]
}

def main(): 
    parser = argparse.ArgumentParser(description="Compare two teams in a league season.")
    parser.add_argument("--country", required=True, help="Country code (e.g., ENG)")
    parser.add_argument("--teamA", required=True, help="Team A name")
    parser.add_argument("--teamB", required=True, help="Team B name")
    args = parser.parse_args()

    ccc = args.country
    teamA = args.teamA
    teamB = args.teamB

    raw = functions.create_dataset(country=ccc, url_list = url_list)
    ## raw = pd.read_csv("./primeira_25.csv", delimiter="\t")
    raw2 = raw[raw['Score'].notnull()].drop(columns = ['Day', 'Date', 'Time', 'Attendance', 'Venue', 'Referee', 'Match Report', 'Notes'])
    games = functions.setup_data(df_input=raw2)
    team_list = pd.unique(games['Home']) 

    functions.common_games(games=games, teamA=teamA, teamB=teamB) ## creates teh results.txt file

    leaders_df = functions.season_leaders(all_teams=team_list,  games=games) ## creates seasonLeaders.txt file and dataframe 
    return leaders_df, team_list, games ## return these to its accessible outside of function 


#######
if __name__ == "__main__":
    leaders_df, team_list, games = main()
########


###    loop through each week after halfway to get leaderboard      ###
num_opponents = int(len(team_list))-1
weekly_leaders = {}
for i in range(num_opponents, num_opponents*2+1):
    df = games[games['Wk'] <= i*1.0]
    lead_board = functions.season_leaders(all_teams=team_list,  games=df)
    lead_board['rank'] = lead_board['score'].rank(method='dense', ascending=False)
    leader = list(lead_board['team'][lead_board['rank']==1])
    weekly_leaders[i] =  leader

print(pd.DataFrame.from_dict(weekly_leaders, orient='index') ) 



############ ------------------------------------------------------------


####  Plot the progress of the top 4 thresholds########################
## functions.get_threshold(games, team_list, 33, 2)

wks = games['Wk'].unique()
thresholds = []
thresholds_2 = []
thresholds_4 = []
for i in wks:
    thresholds.append(functions.get_threshold(games, team_list, i, 1))
    thresholds_2.append(functions.get_threshold(games, team_list, i, 2))
    thresholds_4.append(functions.get_threshold(games, team_list, i, 4))

df_thresholds = pd.DataFrame({
        'wk' : wks,
        'top': thresholds, 
        'top2': thresholds_2,
        'top4': thresholds_4
    })


from matplotlib.ticker import MultipleLocator
m = max(thresholds) ## <- forgot what this does 

plt.style.use('ggplot')
fig = plt.figure(figsize= (8,6), facecolor="lightgreen")
ax = fig.add_axes((.1, .1, .8, .8))
fig.suptitle("leader in red\ntop 2 in blue, top 4 in purple")
ax.stairs(thresholds, linewidth=2, fill=True, alpha = 0.8)
ax.stairs(thresholds_2, linewidth=2, fill=True, alpha = 0.5)
ax.stairs(thresholds_4, linewidth=1, fill=True, alpha = 0.8)

# Set tick intervals to 3
#ax.xaxis.set_major_locator(MultipleLocator(3))
ax.yaxis.set_major_locator(MultipleLocator(3))

plt.show()

############################################################