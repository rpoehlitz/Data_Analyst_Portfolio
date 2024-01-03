import pandas as pd
from statsbombpy import sb
import seaborn as sns
import matplotlib.pyplot as plt

def fetch_competitions_data():
    return sb.competitions()

def fetch_matches_data(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

def fetch_events_data(match_id):
    events = sb.events(match_id=match_id)
    return events[(events.period.isin([1, 2])) & (events.type == 'Shot')]

def preprocess_events_data(events):
    df = events[['period', 'minute', 'shot_statsbomb_xg', 'team', 'player', 'shot_outcome']]
    df.rename(columns={'shot_statsbomb_xg': 'xG', 'shot_outcome': 'result'}, inplace=True)
    df.sort_values(by='team', inplace=True)
    return df

def separate_teams_data(df):
    hteam = df['team'].iloc[0]
    ateam = df['team'].iloc[-1]

    h_df = df[df['team'] == hteam].copy()
    h_df.sort_values(by='minute', inplace=True)
    h_df["h.cumult"] = h_df['xG'].cumsum()

    a_df = df[df['team'] == ateam].copy()
    a_df.sort_values(by='minute', inplace=True)
    a_df["a.cumult"] = a_df['xG'].cumsum()

    return hteam, ateam, h_df, a_df

def extract_goal_data(team_df):
    goals = team_df[team_df['result'].str.contains("Goal")]
    goal_count = team_df['result'].str.contains("Goal").sum()
    goals["scorechart"] = goals['minute'].astype(str) + "'" + " " + goals["player"]
    total_xG = round(team_df['xG'].sum(), 2).astype(str)
    return goals, goal_count, total_xG

def plot_xG_chart(h_df, a_df, hteam, ateam, h_goal, a_goal, h_total, a_total, h_goal_count, a_goal_count, competition_name, season_name):
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.step(x=a_df['minute'], y=a_df['a.cumult'], where='post', color='#004d98',
            label=ateam + ": " + "(" + a_total + " xG)", linewidth=2)
    ax.step(x=h_df['minute'], y=h_df['h.cumult'], where='post', color='red',
            label=hteam + "(" + h_total + " xG)", linewidth=2)

    plt.scatter(x=a_goal['minute'], y=a_goal['a.cumult'], marker='o', color='#004d98')
    plt.scatter(x=h_goal['minute'], y=h_goal['h.cumult'], marker='o', color='red')

    y_max = max(h_df['h.cumult'].max(), a_df['a.cumult'].max())

    for j, txt in h_goal['scorechart'].items():
        x = h_goal['minute'][j]
        y = h_goal['h.cumult'][j]
    
        x_offset = 15
        y_offset = 15
        
        # Keep label inside the axes
        if y + y_offset > y_max:
            y_offset = -15
            
        
                
        ax.annotate(txt, (x, y), xycoords='data', xytext=(x_offset, y_offset), 
                    textcoords='offset points', 
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", 
                                    color='red')) 

    for i, txt in a_goal['scorechart'].items():
        x = a_goal['minute'][i]
        y = a_goal['a.cumult'][i]
        
        x_offset = 15
        y_offset = 15
        
        # Keep label inside the axes
        if y + y_offset > y_max:
            y_offset = -15
        
        
        
        ax.annotate(txt, (x, y), xycoords='data', xytext=(x_offset, y_offset), 
                    textcoords='offset points', 
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3", 
                                    color='blue'))

    ax.autoscale(enable=True, axis='y')
    plt.xticks([0, 15, 30, 45, 60, 75, 90])
    plt.ylim(0)
    plt.xlim(0)
    plt.grid()

    fig.text(s=hteam + " - " + ateam + " (" + str(h_goal_count) + " - " + str(a_goal_count) + ")",
             x=0.125, y=0.97, fontsize=18, fontweight="bold")
    fig.text(s=f"Final {competition_name} - {season_name}", x=0.125, y=0.92, fontsize=12)

    legend = ax.legend(title='Total Expected Goals(xG)', loc='best', shadow=True)
    legend._legend_box.align = "left"

    plt.ylabel("Expected Goals (xG)", fontsize=12, labelpad=20)
    plt.xlabel("Minutes", fontsize=12, labelpad=20)

    ax.legend()
    plt.show()


def main():
    # Fetching competitions data
    comps = fetch_competitions_data()

    # Displaying unique competitions to the user
    unique_comps = comps[['competition_id', 'competition_name']].drop_duplicates()
    print("Available Competitions:")
    for idx, (comp_id, comp_name) in enumerate(unique_comps.values, start=1):
        print(f"{idx}. {comp_name}")

    # Asking the user to select a competition
    comp_choice = int(input("Enter the number corresponding to your chosen competition: "))
    
    if 1 <= comp_choice <= len(unique_comps):
        selected_competition_id = unique_comps.iloc[comp_choice - 1]['competition_id']
    else:
        print("Invalid competition choice. Exiting.")
        return

    # Fetching available seasons for the selected competition
    seasons = comps[comps["competition_id"] == selected_competition_id]
    print(f"Available Seasons for {unique_comps.iloc[comp_choice - 1]['competition_name']}:")
    for idx, season in enumerate(seasons['season_name'].unique(), start=1):
        print(f"{idx}. {season}")

    # Asking the user to select a season
    season_choice = int(input("Enter the number corresponding to your chosen season: "))
    selected_season = seasons.iloc[season_choice - 1]

    # Fetching matches data for the selected competition and season
    matches = fetch_matches_data(competition_id=selected_competition_id, season_id=selected_season["season_id"])

    # Displaying available filters for matches
    print("Available Filters:")
    print("1. Filter by date range")
    print("2. Filter by teams")
    filter_choice = int(input("Enter the number corresponding to your chosen filter option (or 0 to skip filtering): "))

    if filter_choice == 1:
        # Filter by date range
        min_date = matches['match_date'].min().strftime('%Y-%m-%d')
        max_date = matches['match_date'].max().strftime('%Y-%m-%d')

        print(f"Date Range: {min_date} to {max_date}")
        start_date = pd.to_datetime(input(f"Enter the start date (YYYY-MM-DD, default {min_date}): ") or min_date, errors='coerce')
        end_date = pd.to_datetime(input(f"Enter the end date (YYYY-MM-DD, default {max_date}): ") or max_date, errors='coerce')

        matches = matches[(matches['match_date'] >= start_date) & (matches['match_date'] <= end_date)]
    elif filter_choice == 2:
        # Filter by teams
        unique_teams = pd.concat([matches['home_team'], matches['away_team']]).unique()
        print("Available Teams:")
        for idx, team in enumerate(unique_teams, start=1):
            print(f"{idx}. {team}")

        team_choice = int(input("Enter the number corresponding to your chosen team: "))
        selected_team = unique_teams[team_choice - 1]

        matches = matches[(matches['home_team'] == selected_team) | (matches['away_team'] == selected_team)]

    # Displaying available matches after filtering
    print(f"Available Matches for {unique_comps.iloc[comp_choice - 1]['competition_name']} - {selected_season['season_name']}:")
    for idx, (match_id, home_team, away_team, match_date) in enumerate(matches[['match_id', 'home_team', 'away_team', 'match_date']].values, start=1):
        match_date_str = pd.to_datetime(match_date).strftime('%Y-%m-%d')
        print(f"{idx}. {home_team} vs {away_team} ({match_date_str})")

    # Asking the user to select a match
    match_choice = int(input("Enter the number corresponding to your chosen match: "))
    selected_match = matches.iloc[match_choice - 1]

    # Fetching events data for the selected match
    events = fetch_events_data(match_id=selected_match['match_id'])

    # Preprocessing events data
    df = preprocess_events_data(events)

    # Separating data for home and away teams
    hteam, ateam, h_df, a_df = separate_teams_data(df)

    # Extracting goal events and counts
    h_goal, h_goal_count, h_total = extract_goal_data(h_df)
    a_goal, a_goal_count, a_total = extract_goal_data(a_df)

    # Plotting
    plot_xG_chart(h_df, a_df, hteam, ateam, h_goal, a_goal, h_total, a_total, h_goal_count, a_goal_count, unique_comps.iloc[comp_choice - 1]["competition_name"], selected_season["season_name"])

if __name__ == "__main__":
    main()



