# Import Libraries
# Packages for work.
import requests
import pandas as pd
import numpy as np
import time
import streamlit as st

from sklearn.metrics.pairwise import cosine_similarity

# Set Page configuration
st.set_page_config(page_title='Video Games Recommender', page_icon='🎮', layout='wide', initial_sidebar_state='expanded')

# Set title of the app
st.title('🎮 Video Games Recommender 🎮')
st.subheader('A video games recommender system powered by User-Based Collaborative Filtering.')
st.write('This is a video games recommender I built for my final project for the Data Analytics Immersive course at General Assembly (Singapore).')
st.write('You can find the code for this project and this app on my GitHub repository [here](https://github.com/kgtkgtkg/Video-Games-Recommender). Please feel free to reach out to me if you have feedback or suggestions on how I can improve! 🙏🚀')
st.info('The recommender may take a few minutes to load the first time you use it. Please be patient! 😊')
st.warning('NOTE: Please ensure that you have set your Steam account privacy settings to public before using the recommender.')

# Set input widgets
st.sidebar.warning('NOTE: Please ensure that you have set your Steam account privacy settings to public.')
userinput = st.sidebar.text_input(label='Please enter your 17-digit unique Steam ID:', max_chars=17)


# Start of Hide index column. This is to hide the index column of the table of recommended games in the syntax below.
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
# End of hide index column syntax

## Caching user account data in the list for 7 days.
@st.cache_data(ttl = 60*60*24*7)
def load_data():
    steam_ids = pd.read_excel("steamids.xlsx") # Read in the list of saved Steam IDs.
    steam_ids["user_steamid"] = steam_ids["user_steamid"].astype(str) # Then convert the Steam IDs to string.
    
    api_key = "7364D56DBC085B6B0AB3DAD90F5A5290" # Define my API key. # Feel free to use mine, but note that you can change it to your own.
    steamids = steam_ids["user_steamid"].tolist() # Get the list of Steam IDs.
    group_user_data = pd.DataFrame(columns=["appid", "game name", "hours played", "steamid"]) # Create an empty dataframe to store the data from the Steam API.
    
    for eachid in steamids: # Run the for loop to collect the data from the Steam API.
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={eachid}&include_appinfo=true&include_played_free_games=true"
        user_data_request = requests.get(url)
        user_data_json = user_data_request.json()
        
        try:
            user_games_data = user_data_json["response"]["games"]
            user_games_df = pd.DataFrame(user_games_data)
            games_and_playtimes = user_games_df[["appid", "name", "playtime_forever"]]
            games_and_playtimes["playtime_forever"] = games_and_playtimes["playtime_forever"]/60
            games_and_playtimes.rename(columns={"name": "game name", "playtime_forever": "hours played"}, inplace=True)
            games_and_playtimes["steamid"] = str(eachid)

            # Append the data of each user to the group_user_data dataframe.
            group_user_data = group_user_data.append(games_and_playtimes)
        except:
            print(f"No games found for user {eachid}")
        time.sleep(5)
            
    return group_user_data


# Display Table of Recommended Games
def ub_recommender(steamid, n=5):
    if len(steamid) != 17:
        st.error('Please enter a valid 17-digit Steam ID.') # Check if the user has entered a valid Steam ID.
        st.stop()
    else:
        # Read in the list of saved Steam IDs.
        steam_ids = pd.read_excel("steamids.xlsx") # Read in the list of saved Steam IDs.
        steam_ids["user_steamid"] = steam_ids["user_steamid"].astype(str)
        
        if steamid not in steam_ids['user_steamid'].tolist(): # If the user is a new user, then add the user's Steam ID to the list of saved Steam IDs.
            steam_ids = steam_ids.append({'user_steamid': steamid}, ignore_index=True)
        else:
            pass
        steam_ids.to_excel("steamids.xlsx",index=False) # Then save the new list of Steam IDs.

        group_user_data = load_data() # Bring in the cache data into the function environment.
        
        if steamid in steam_ids['user_steamid'].tolist(): # If the user is already in the list, then we will need to remove the user's own games from the dataset. In a sense we are refreshing the user's data.
            group_user_data = group_user_data[group_user_data["steamid"] != steamid]
        else:
            pass
            
        # The next step is to get the data of the new user, then add it to the group's dataset that is cached.
        
        # This is my personal API key.
        api_key = "7364D56DBC085B6B0AB3DAD90F5A5290"

        # The following will collect the new user account data from the Steam API.
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={api_key}&steamid={steamid}&include_appinfo=true&include_played_free_games=true"
        user_data_request = requests.get(url)
        user_data_json = user_data_request.json()
        try:
            user_games_data = user_data_json["response"]["games"]
            user_games_df = pd.DataFrame(user_games_data)
            new_user_data = user_games_df[["appid", "name", "playtime_forever"]]
            new_user_data["playtime_forever"] = new_user_data["playtime_forever"]/60
            new_user_data.rename(columns={"name": "game name", "playtime_forever": "hours played"}, inplace=True)
            new_user_data["steamid"] = str(steamid)

            # Append the data of each user to the group_user_data dataframe.
            group_user_data = group_user_data.append(new_user_data)
        except:
            print(f"No games found for user {steamid}")
        
        # Once all the data is collected, keep only rows where each user has played the game. ie. hours played > 0.
        group_user_data2 = group_user_data[group_user_data["hours played"]>0]

        # Pre-processing 1. Construct the user-by-game matrix.
        # Construct the empty user-by-game matrix first.
        ubg_df = pd.DataFrame(index=group_user_data2["steamid"].unique(), columns=group_user_data2["game name"].unique())
        
        # For each row in the dataset group_user_data,
        for each_row in range(len(group_user_data2)):
            # take the Steam ID of that row,
            user = group_user_data2.iloc[each_row]['steamid']
            # and the Game Name of that row,
            game = group_user_data2.iloc[each_row]['game name']
            # and input the Hours Played of that row into the user-by-game matrix with the corresponding Steam ID row, and Game Name column.
            ubg_df.loc[user, game] = group_user_data2.iloc[each_row]['hours played']

        # Pre-processing 2. Applying scaling onto the user-by-game matrix.
        ubg_logged = np.log(ubg_df.astype(float))

        # Shift the normalized scale to all positive.
        ubg_logged += abs(ubg_logged.min().min())

        # Pre-processing 3. Creating a user-by-game sparse matrix. This is because Cosine Similarity cannot handle NaN values.
        ubg_logged0 = ubg_logged.fillna(0)

        # With Cosine Similarities, find the user-to-user similarity scores.
        sim_scores = cosine_similarity(ubg_logged0)
        # Organise the user-to-user similarity scores into a matrix.
        utu_simscores = pd.DataFrame(sim_scores, columns=ubg_logged0.index, index=ubg_logged0.index)

        # Recommend games to the user using both the user-by-game matrix (ubg_logged0) and user-to-user similarity matrix (utu_simscores).
        
        
        # Step 1. Get the user's similarity scores with all other users in the group, and drop his own similarity score to himself.
        user_sim = utu_simscores[steamid].drop(steamid)
        
        # Step 2. Weigh the user's similarity scores with other users in the group.
        user_weights = user_sim.values/np.sum(user_sim.values)

        # Step3: Get all unplayed games of the user
        gbu_logged0 = ubg_logged0.T
        unplayedgames = gbu_logged0[gbu_logged0[steamid] == 0]
        # Drop the user column showing his playtimes (preferences) of the unplayed games. The user would not have any playtime for these games, since they are unplayed.
        unplayedgames = unplayedgames.drop(columns=[steamid])

        # Step 4. Predict playtimes based on the aggregated (weighted) similarity across all users.
        # Multiply the unplayed games matrix with the user's similarity scores to get the user's predicted playtimes of the unplayed games.
        unplayedgames_weighted = np.dot(unplayedgames.values, user_weights)
        unplayedgames_predictedplaytimes = pd.DataFrame(unplayedgames_weighted, index=unplayedgames.index, columns=['Predicted Preference Score'])  # Organise the predicted playtimes of the unplayed games into a matrix.
        # Sort the predicted playtimes of the unplayed games in descending order, and get the top n games.
        recommended_topn = unplayedgames_predictedplaytimes.sort_values(by="Predicted Preference Score", ascending=False).head(n)
            
        return recommended_topn

if st.sidebar.button('Recommend Me Games'):
    recommended_topn = ub_recommender(userinput)
    st.write('The top 5 recommended games for you are:')
    st.table(recommended_topn.index)
