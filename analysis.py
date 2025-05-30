from sklearn.linear_model import LinearRegression
import pandas as pd
import functions
import matplotlib.pyplot as plt

raw = pd.read_csv("./primeira_25.tsv", delimiter="\t")
raw2 = raw[raw['Score'].notnull()].drop(columns = ['Day', 'Date', 'Time', 'Attendance', 'Venue', 'Referee', 'Match Report', 'Notes'])
games = functions.setup_data(df_input=raw2)
team_list = pd.unique(games['Home']) 

############## REGRESSION -------------------------
regres = LinearRegression()

regres.fit(games['xG'].values.reshape(-1,1), games['home_score'].values)
pred_away_score = regres.predict(games['xG.1'].values.reshape(-1,1))
pred_home_score = games['xG'].values.reshape(-1,1)

plt.scatter(games['xG'].values.reshape(-1,1), 
            games['home_score'].values,
            color = "green" )
plt.plot(games['xG'].values.reshape(-1,1),
         pred_home_score,
         color = "black")
plt.plot(games['xG'].values.reshape(-1,1),
         pred_home_score,
         color = "black")
plt.show()