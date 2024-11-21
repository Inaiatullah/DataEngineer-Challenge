import pandas as pd

# Initialising the dataframes from the csv files.
results = pd.read_csv('results.csv')
goalscorers = pd.read_csv('goalscorers.csv')
shootouts = pd.read_csv('shootouts.csv')

# QUESTION 1 - Create a query that calculates the average number of goals per game between 1900 and 2000.#
def average_goals_per_game(results, startyear, endyear):
    # Extracting the year from the date column
    results['year'] = pd.to_datetime(results['date']).dt.year

    # Filter games between 1900 and 2000
    filtered_results = results[(results['year'] >= startyear) & (results['year'] <= endyear)]

    # Create a copy to avoid modifying the original dataframe slice
    filtered_results = filtered_results.copy()
    # Calculate total goals per game (total goals = home score + away score)
    filtered_results['total_goals'] = filtered_results['home_score'] + filtered_results['away_score']

    # Calculate the average number of goals per game
    avg_goals = filtered_results['total_goals'].mean()

    print(f"Q1 - Average number of goals per game (1900–2000): {avg_goals:.2f}")

# QUESTION 2 - Create a query that counts the number of shootouts wins by country and arrange in alphabetical order.#
def shootouts_per_country(shootouts):
    shootout_wins_by_country = shootouts['winner'].value_counts().sort_index()
    print("\nQ2 - Shootout Wins by Country:")
    print(shootout_wins_by_country)

# QUESTION 3 - Create a reliable key that allows the joining together of goal scorers, results, and shootouts.#
def create_composite_keys(results, goalscorers, shootouts):
    # Creating a match_id column which will act as our composite key to be able to join all 3 datasets
    results['match_id'] = results['home_team'] + "_" + results['away_team'] + "_" + pd.to_datetime(results['date']).astype(str)
    goalscorers['match_id'] = goalscorers['home_team'] + "_" + goalscorers['away_team'] + "_" + pd.to_datetime(goalscorers['date']).astype(str)
    shootouts['match_id'] = shootouts['home_team'] + "_" + shootouts['away_team'] + "_" + pd.to_datetime(shootouts['date']).astype(str)
    print("\nQ3 - generated composite key for all three datasets.")

    # QUESTION 4 - Create a query that identifies which teams have won a penalty shootout after a 1-1 draw.#
    draw_1_1_results = results[(results['home_score'] == 1) & (results['away_score'] == 1)]
    draw_1_1_results_with_shootouts = pd.merge(draw_1_1_results, shootouts, on="match_id", how="inner")
    shootout_winners_after_1_1 = draw_1_1_results_with_shootouts['winner'].value_counts()
    print("\nQ4 - Teams that won a penalty shootout after a 1-1 draw:")
    print(shootout_winners_after_1_1)

# QUESTION 5 - Create a query that identifies the top goal scorer by tournament, and what percentage that equates to for all goals scored in the tournament.#
def top_goal_scorer_per_tournament(goalscorers, results):
    # merging the goal scorers and the match results
    merged = pd.merge(goalscorers, results, on="match_id", how="inner")
    # goals are identified by a row having a scorer
    goals = merged[merged['scorer'].notnull()]

    # count the total goals scored per tournament
    total_goals_per_tournament = goals.groupby('tournament').size().reset_index(name='total_goals')

    # count the goals scored by each player in each tournament
    scorer_goals = goals.groupby(['tournament', 'scorer']).size().reset_index(name='goals_scored')

    # sort and identify the top scorer in each tournament
    top_scorer = scorer_goals.loc[scorer_goals.groupby('tournament')['goals_scored'].idxmax()]

    # merge with total goals per tournament to calculate the percentage
    top_scorer_with_total = pd.merge(top_scorer, total_goals_per_tournament, on='tournament')

    # calculate the percentage of goals scored by the top scorer
    top_scorer_with_total['goal_percentage'] = (top_scorer_with_total['goals_scored'] / top_scorer_with_total['total_goals']) * 100

    # clean up the dataframe to be displayed
    top_goal_scorer_by_tournament = top_scorer_with_total[['tournament', 'scorer', 'goals_scored', 'total_goals', 'goal_percentage']]

    print("\nQ5 - Top goal scorers by tournament and their contribution percentage:")
    print(top_goal_scorer_by_tournament)


# QUESTION 6 - Create an additional column that flags records with data quality issues.#
def flag_data_quality_issues(results, goalscorers, shootouts):
    # create a function to validate data/check for any quality issues
    def flag_data_quality(df):
        # checking for any null values or duplicate rows.
        return df.isnull().any(axis=1) | df.duplicated()
    # check each dataframe witht eh 
    results['data_quality_flag'] = flag_data_quality(results)
    goalscorers['data_quality_flag'] = flag_data_quality(goalscorers)
    shootouts['data_quality_flag'] = flag_data_quality(shootouts)
    print("\nQ6 - Data quality flags added to datasets.")


# QUESTION 7 - Resolve the identified quality issues.#
def resolve_data_quality_issues(results, goalscorers, shootouts):
    # We can solve the problem of duplicate rows in each dataframe by deleting any subsequent copies (keeping the first instance of a row)
    results.drop_duplicates(subset=None, keep='first', inplace=True)
    goalscorers.drop_duplicates(subset=None, keep='first', inplace=True)
    shootouts.drop_duplicates(subset=None, keep='first', inplace=True)
    # We can replace null values with a set string indicating that they were not recorded.
    goalscorers.fillna("Not Recorded", inplace=True)
    # There are many methods we can use to fill null values for quantative fields such as mean, median etc. However the method we choose 
    # depends on the data/column we are working with as one method may be more sensible.
    print("\nQ7 - Resolved data quality issues.")

if __name__ == "__main__":
    average_goals_per_game(results, 1900, 2000)
    shootouts_per_country(shootouts)
    create_composite_keys(results, goalscorers, shootouts)
    top_goal_scorer_per_tournament(goalscorers, results)
    flag_data_quality_issues(results, goalscorers, shootouts)
    resolve_data_quality_issues(results, goalscorers, shootouts)