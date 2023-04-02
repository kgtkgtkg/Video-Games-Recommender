# Import Libraries
# Packages for work.
import requests
import pandas as pd
import numpy as np
import time
import random
import glob
import os
import streamlit as st

from sklearn.metrics.pairwise import cosine_similarity

# Set Page configuration
st.set_page_config(page_title='Video Games Recommender', page_icon='🎮', layout='wide', initial_sidebar_state='expanded')

# Set title of the app
st.title('🎮 Video Games Recommender 🎮')
st.subheader('A video games recommender system powered by User-Based Collaborative Filtering.')
st.write('This is a video games recommender I built for my final project for the Data Analytics Immersive course at General Assembly (Singapore).')
st.write('This is the first workable version. I hope to make improvements and add features to it in the future. 🚀')
st.write('You can find the code for this project and this app on my GitHub repository [here](https://github.com/kgtkgtkg/GA-IndividualCapstone).')
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
    userids_df = pd.read_excel("steamids.xlsx") # Read in the list of saved Steam IDs.
    userids_df["user_steamid"] = userids_df["user_steamid"].astype(str) # Then convert the Steam IDs to string.
    
    api_key = "?key=7364D56DBC085B6B0AB3DAD90F5A5290" # Define my API key.
    userids_list = userids_df["user_steamid"] # Get the list of Steam IDs.
    group_user_data = pd.DataFrame(columns=["appid", "game name", "hours played", "steamid"]) # Create an empty dataframe to store the data from the Steam API.
    
    for eachid in userids_list: # Run the for loop to collect the data from the Steam API.
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/{api_key}&steamid={eachid}&include_appinfo=true&include_played_free_games=true"
        user_games_request = requests.get(url)
        user_games_json = user_games_request.json()
        try:
            user_games_all = user_games_json["response"]["games"]
            user_games_df = pd.DataFrame(user_games_all)
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

st.info('Massive thanks to everyone who helped me on this project. I love DAI-001. 🍻')

# Display Table of Recommended Games
def ub_recommender(steamid, n=5):
    if len(steamid) != 17:
        st.error('Please enter a valid 17-digit Steam ID.') # Check if the user has entered a valid Steam ID.
        st.stop()
    else:
        # Read in the list of saved Steam IDs.
        userids_df = pd.read_excel("steamids.xlsx")
        userids_df["user_steamid"] = userids_df["user_steamid"].astype(str)
        
        if steamid not in userids_df['user_steamid'].tolist(): # If the user is a new user, then add the user's Steam ID to the list of saved Steam IDs.
            userids_df = userids_df.append({'user_steamid': steamid}, ignore_index=True)
        else:
            pass
        userids_df.to_excel("steamids.xlsx",index=False) # Then save the new list of Steam IDs

        group_user_data = load_data() # Bring in the cache data into the function environment.
        
        if steamid in userids_df['user_steamid'].tolist(): # If the user is not a new user, then we will need to remove the user's own games from the dataset. In a sense we are refreshing the user's data.
            group_user_data = group_user_data[group_user_data["steamid"] != steamid]
        else:
            pass
            
        # The next step is to get the data of the new user, then add it to the group's dataset that is cached.
        
        # This is my personal API key.
        api_key = "?key=7364D56DBC085B6B0AB3DAD90F5A5290"

        # The following will collect the new user account data from the Steam API.
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/{api_key}&steamid={steamid}&include_appinfo=true&include_played_free_games=true"
        user_games_request = requests.get(url)
        user_games_json = user_games_request.json()
        try:
            user_games_all = user_games_json["response"]["games"]
            user_games_df = pd.DataFrame(user_games_all)
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

        # Construct the user-by-game matrix.
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

        # Normalize the user-by-game matrix. We are normalizing the hours played so that skewing is controlled and preferences are smoothen. Reminder that we are using user playtimes as a proxy for user preference.
        ubg_norm = np.log(ubg_df.astype(float))

        # Shift the normalized scale to all positive. If there are any negative values after normalizing, add the absolute value of the smallest value to all values in the matrix.
        ubg_norm += abs(ubg_norm.min().min())

        # Creating a user-by-game sparse matrix by filling in null values with 0. This is required because Cosine Similarities cannot handle null values.
        ubg_norm_fill0 = ubg_norm.fillna(0)

        # With Cosine Similarities, find the user-to-user similarity scores.
        sim_matrix1 = cosine_similarity(ubg_norm_fill0)
        # Organise the user-to-user similarity scores into a matrix. This is the user-to-user similarity matrix.
        utu_simscores = pd.DataFrame(sim_matrix1, columns=ubg_norm_fill0.index, index=ubg_norm_fill0.index)

        # With both the user-to-user similarity matrix (utu_simscores) and user-by-game sparse matrix (ubg_norm_fill0), we can now recommend games to the user.
        # Get the user's similarity scores with other users in the group, and drop his own similarity score to himself.
        user_sim = utu_simscores[steamid].drop(steamid)
        # Weigh the user's similarity scores with other users in the group.
        user_weights = user_sim.values/np.sum(user_sim.values)

        # Transpose the user-by-game sparse matrix so that we can get the games that the user has not played.
        gbu_norm_fill0 = ubg_norm_fill0.T
        # Get the games that the user has not played.
        unplayedgames = gbu_norm_fill0[gbu_norm_fill0[steamid] == 0]
        # Drop the user column showing his playtimes (preferences) of the unplayed games. The user would not have any playtime for these games, since they are unplayed.
        unplayedgames = unplayedgames.drop(columns=[steamid])

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
