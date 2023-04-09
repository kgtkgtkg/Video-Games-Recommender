# Video Games Recommender (Steam Games)
## Introduction <br>
**Background & Problem Statement** <br>
Video games have been a popular form of entertainment for many years. It is a large and competitive industry worth billions, with a constantly evolving market. There are a wide variety of games being released every year, and it is expected that it would continue to grow. <br>

With a massive collection of games that includes everything from AAA blockbusters to small indie titles, how can businesses effectively distribute their games to customers that would be more likely to buy them? <br>

Put differently, users may also be interested in playing new games, but only similar to the ones they are currently playing, or what other similar users are playing. Furthermore, the average consumer has a limited budget and time to play. Could we find a way to recommend them games accurately? <br>

**Goals & Scope** <br>
One way is to observe the game preferences of customers. The idea is: If games are recommended to customers based on their preferences, then they are more likely to make a purchase. <br>

To do that, we can develop a model that predicts the preferences of customers on the games they have not played, and then recommend those games to them.

This project will focus on PC video games. We will analyze the users on the Steam Games platform (Steam).

The main goal here is to recommended games to customers based on their preferences. We will analyze the historical behaviours of users to predict their preferences.

**Methodology** <br>
The proposed model for this project would be an unsupervised machine learning predictive model. This model predicts the preferences of a user towards unplayed games based on: <br>
1. The preferences of all users in the group towards each game **(playtimes)** <br>
2. The similarity (of preferences) across all users in the group **(similarity scores)** <br>

Throughout the analysis, playtime will be the proxy for user preference. Cosine Similarity will be used to calculate the similarity scores between users and between games. <br>

The technique applied is Collaborative Filtering, with 2 variations: <br>
1. User-Based Collaborative Filtering (Predict User A’s preference for an unplayed game based on the preferences of similar users.) <br>
2. Item-Based (Game-Based) Collaborative Filtering (Predict User A’s preference for an unplayed game based on how similar it is to User A’s played games.) <br>

For clarity, each of the variations will still predict game preferences, the difference is in how it predicts. The predictions would then allow for user-specific video game recommendations. <br>

## **Application Summary** <br>
**1. Data Collection** <br>
*steamids.xlsx* - A list of users and their account IDs (Steam ID) was manually compiled. The IDs were mainly extracted from the friends list of my own Steam account. <br>

*data/raw_dataset.xlsx* - The account data then was extracted via the Steamworks API, with reference to the compiled list of account IDs. An initial 53 users and their account data were compiled to form the raw dataset. <br>

Full commentary and details of the data collection can be found in the file 1.DataCollection.ipynb. <br>

**2. Data Exploration & Cleaning** <br>
Preliminary data exploration showed that the quality of the data from the Steamworks API was good. Only minimal data cleaning was needed, and these were mainly for labelling purposes, which had little impact on the formulation of the recommender. <br> 

Outliers were also handled (trimmed) in anticipation of handling complications during the modelling. The final dataset included a total of 36 users (36 accounts). <br>

Full commentary and details of the data exploration and cleaning can be found in the file 2.DataExploration&Cleaning.ipynb. <br>

**3. Data Pre-processing** <br>
This section involves preparing the necessary dataset for the building of the model. This includes building the user-by-item matrix, normalizing user playtimes and scaling the dataset to control for skewness, and shifting the normalized scale to simplify interpretations.

Full commentary and details of the data exploration and cleaning can be found in the file 3.PreProcessing.ipynb. <br>

**4.1 User-Based Recommender** <br>
This function recommends games based on user-based collaborative filtering. <br>
Please refer to the file 4.1.UserBasedRecommender.ipynb for full commentary and details. <br>

**4.2 Game-Based Recommender** <br>
This function recommends games based on item-based collaborative filtering. <br>
Please refer to the file 4.2.GameBasedRecommender.ipynb for full commentary and details. <br>

**5. Recommender App** <br>
This is a deployment of the User-Based Recommender on Streamlit. Please visit this [link](https://kgtkgtkg-video-games-re-5-userbasedrecommender-streamlit-a9z9zu.streamlit.app/) to view the app. <br>
Please refer to the file 5.UserBasedRecommender-Streamlit.py for the app script. <br>

## **Conclusion, Limitations, and Further Work** <br>
Evidenced by the outputs of the recommenders, the application of the methodology was successful. However, there are several limitations to this project. <br>

**1. Model Evaluation** <br>
Evaluation of the recommender was not conducted to review its performance and accuracy. <br>

Further work can be done on this by including techniques and metrics to evaluate the model. Alternatively, feedback can be gathered from users to verify if they agree with the recommended games, or if they found the recommender useful. <br>

**2. Data Sparsity and Variety** <br>
Collaborative Filtering thrives on data volume and variety. We can make more accurate recommendations with more data, but more importantly, the data must have a good balance between similarity and differences among users of the group. For example, a user cannot be exactly the same with all other users in the group, otherwise there would be no new recommendation to be made. But a user also cannot be so different such that no similarity can be found with other users. In the real world, it is unlikely that two users are exactly the same or entirely different. But as long as there are differences in users, data sparsity will exist. <br>

One technique that can be explored further to address data sparsity is Matrix Factorization. <br>

**3. Cold-Start Problem** <br>
Collaborative Filtering is reliant on learning the similarities between users or items of a group. But for new users or new games with little to no historical data, it would not be able to learn much about them. They therefore cannot participate in the filtering. From a business perspective, recommending a game becomes tricky. Without revealed preferences, we may not be able to effectively recommend games that a user would prefer. <br>

One workaround to this is to construct a Content-Based Filter, and integrate it into this recommender. This would give the new users some level of participation. However, given that Steam Games already has a search function for games on their platform, the impact of such an addition would be limited. <br>

**4. "Wisdom of the crowd"** <br>
The game recommendations are only as good as the data within the group. With Collaborative Filtering, you are likely to be recommended a game you would prefer, but you are limited to the games that other users in the group have played, and limited even further to the games of users who are most similar to you. From a business perspective, while the goal is to continually recommend games that users would purchase, the group must have played sufficient games to keep recommending to each other. <br>

**5. Other** <br>
It should be noted that in the deployment script, I included all 53 users from the steamids.xlsx. Ultimately, the successful extraction of user account data via the Steamworks API is dependent on the account privacy settings of the user. Over time, if a user changes their privacy settings, then we will get varying datasets. <br>

Also, I have included additional features on the deployment script to account for a growing list of Steam IDs on the recommender app. This is so that each time the app is used, it adds the input Steam ID to the list, thus growing the dataset and strengthening the recommender. However, given that this was a course project, I will not be maintaining an online database or online file to collect and save the Steam IDs. <br>

## **Closing Note** <br>
This project was done as part the Data Analytics Immersive course with General Assembly (Singapore). The course culminated with an individual capstone project, and as part of my learning, I wanted to do something related to my favourite pastime. <br>

Please feel free to reach out to me if you have feedback or suggestions on how I can improve. <br> 
You can connect with me here on GitHub, [LinkedIn](https://www.linkedin.com/in/tankaiguan/), or [Steam](https://steamcommunity.com/profiles/76561198010430483/).

## **Files and Folders** <br>
data - Datasets saved and used at different stages of the application. <br>
matrices - Matrices constructed for the recommender. <br>
recommenderresults - Outputs from the recommender functions. <br>
UserEDA.twbx - A Tableau packaged workbook containing some basic visualizations on the datasets. The visualizations on this workbook is from data of all 53 user accounts as of 01 April 2023.
