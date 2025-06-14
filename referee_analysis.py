
import pandas as pd
import functions
import matplotlib.pyplot as plt
import numpy as np

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


raw = functions.create_dataset(country="ENG", url_list = url_list)
raw2 = raw[raw['Score'].notnull()].drop(columns = ['Day', 'Date', 'Time', 'Attendance', 'Venue', 'Match Report', 'Notes'])
games = functions.setup_data(df_input=raw2)
team_list = pd.unique(games['Home']) 
ref_list = pd.unique(games['Referee'])

## Score diff 
games['score_diff'] = abs(games['home_score'] - games['away_score'])

# Define game closeness
games['is_close_game'] = games['score_diff'] <= 1

# Group by referee 
ref_stats = games.groupby('Referee').agg(
    total_games=('is_close_game', 'count'),
    close_games=('is_close_game', 'sum')
)

# Calculate percentage of close games
ref_stats['pct_close_games'] = ref_stats['close_games'] / ref_stats['total_games']
ref_stats = ref_stats.sort_values(by='pct_close_games', ascending=False)


# STATISTICS testing 
from scipy.stats import chi2_contingency

# Create contingency table
contingency = pd.crosstab(games['Referee'], games['is_close_game'])

chi2, p, dof, expected = chi2_contingency(contingency)

print(f"Chi-squared Test p-value: {p:.4f}")


# Logit regression with confounder: xG
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Add team strength proxy (xG difference)
games['xg_diff'] = abs(games['xG'] - games['xG.1'])
games['is_close_game'] = games['is_close_game'].astype(int)
games['xg_sum'] = abs(games['xG'] + games['xG.1'])


# Logistic regression: is_close_game ~ referee + xg_diff
model = smf.logit("is_close_game ~ C(Referee) + xg_diff", data=games).fit()
print(model.summary())

# Logistic regression: is_close_game ~  xg_diff
model = smf.logit("is_close_game ~ xg_diff", data=games).fit()
print(model.summary())


##.  ANOVA 
from scipy.stats import f_oneway

# Group score differences by referee
groups = [group['score_diff'].values for name, group in games.groupby('Referee')]

f_stat, p_value = f_oneway(*groups)

print(f"F-statistic: {f_stat:.4f}")
print(f"P-value: {p_value:.4f}")

groups = [group['is_close_game'].astype(int).values for name, group in games.groupby('Referee')]

f_stat, p_value = f_oneway(*groups)

print(f"F-statistic: {f_stat:.4f}")
print(f"P-value: {p_value:.4f}")

### RESULTS show no difference among referees variance 


## Analysis of COVARIANCE: c
# Fit OLS model
model = smf.ols('score_diff ~ C(Referee) + xg_diff', data=games).fit()

# ANCOVA (Type II sum of squares)
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)


## NOW CHECK ON xg_SUM not DIFF 
# Logistic regression: is_close_game ~ referee + xg_sum
model = smf.logit("is_close_game ~ C(Referee) + xg_sum", data=games).fit()
print(model.summary())

# Logistic regression: is_close_game ~  xg_diff
model = smf.logit("is_close_game ~ xg_diff", data=games).fit()
print(model.summary())

## Analysis of COVARIANCE: c
# Fit OLS model
model = smf.ols('score_diff ~ C(Referee) + xg_sum', data=games).fit()

# ANCOVA (Type II sum of squares)
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)


