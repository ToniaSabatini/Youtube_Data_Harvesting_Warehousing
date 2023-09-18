# Import necessary libraries
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector as sql
import pymongo
from googleapiclient.discovery import build
from PIL import Image

# SETTING PAGE CONFIGURATIONS
# Set the title, icon, layout, and menu items for the Streamlit app
icon = Image.open("D:\Project\Youtube-logo.png")
st.set_page_config(page_title="Youtube Data Harvesting and Warehousing | By Tonia Sabatini",
                   page_icon=icon,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """# This app is created by *Tonia Sabatini!*"""})

# CREATING OPTION MENU
# Create an option menu in the Streamlit sidebar for navigation
with st.sidebar:
    selected = option_menu(None, ["Home", "Extract & Transform", "View"],
                           icons=["house-door-fill", "tools", "card-text"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "0px",
                                                "--hover-color": "#ff0000"},
                                   "icon": {"font-size": "20px"},
                                   "container": {"max-width": "5000px"},
                                   "nav-link-selected": {"background-color": "#ff0000"}})

# Bridging a connection with MongoDB Atlas and Creating a new database (youtube_data)
# Establish a connection with MongoDB Atlas and select the database
client = pymongo.MongoClient("mongodb+srv://Tonia:SabatiniA@cluster0.2b07pq3.mongodb.net/?retryWrites=true&w=majority")
db = client.Youtube_Data_Toni

# CONNECTING WITH MYSQL DATABASE
# Connect to the MySQL database
mydb = sql.connect(host="127.0.0.1",
                   user="root",
                   password="8888888888883",
                   database="youtube",
                   port="3306"
                   )
mycursor = mydb.cursor(buffered=True)

# BUILDING CONNECTION WITH YOUTUBE API
api_key = "8888888888888888888888888888888888888888888"  
youtube = build('youtube', 'v3', developerKey=api_key)

# FUNCTION TO GET CHANNEL DETAILS
def get_channel_details(channel_id):
    ch_data = []
    response = youtube.channels().list(part='snippet,contentDetails,statistics',
                                       id=channel_id).execute()

    for i in range(len(response['items'])):
        data = dict(Channel_id=channel_id[i],
                    Channel_name=response['items'][i]['snippet']['title'],
                    Playlist_id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
                    Subscribers=response['items'][i]['statistics']['subscriberCount'],
                    Views=response['items'][i]['statistics']['viewCount'],
                    Total_videos=response['items'][i]['statistics']['videoCount'],
                    Description=response['items'][i]['snippet']['description'],
                    Country=response['items'][i]['snippet'].get('country')
                    )
        ch_data.append(data)
    return ch_data


# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None

    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()

        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids


# FUNCTION TO GET VIDEO DETAILS
def get_video_details(v_ids):
    video_stats = []

    for i in range(0, len(v_ids), 50):
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(v_ids[i:i + 50])).execute()
        for video in response['items']:
            video_details = dict(Channel_name=video['snippet']['channelTitle'],
                                 Channel_id=video['snippet']['channelId'],
                                 Video_id=video['id'],
                                 Title=video['snippet']['title'],
                                 Tags=video['snippet'].get('tags'),
                                 Thumbnail=video['snippet']['thumbnails']['default']['url'],
                                 Description=video['snippet']['description'],
                                 Published_date=video['snippet']['publishedAt'],
                                 Duration=video['contentDetails']['duration'],
                                 View_count=video['statistics']['viewCount'],
                                 Like_count=video['statistics'].get('likeCount'),
                                 Comments=video['statistics'].get('commentCount'),
                                 Favorite_count=video['statistics']['favoriteCount'],
                                 Definition=video['contentDetails']['definition'],
                                 Caption_status=video['contentDetails']['caption']
                                 )
            video_stats.append(video_details)
    return video_stats


# FUNCTION TO GET COMMENT DETAILS
def get_comments_details(v_id):
    comment_data = []
    try:
        next_page_token = None
        while True:
            response = youtube.commentThreads().list(part="snippet,replies",
                                                     videoId=v_id,
                                                     maxResults=100,
                                                     pageToken=next_page_token).execute()
            for cmt in response['items']:
                data = dict(Comment_id=cmt['id'],
                            Video_id=cmt['snippet']['videoId'],
                            Comment_text=cmt['snippet']['topLevelComment']['snippet']['textDisplay'],
                            Comment_author=cmt['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                            Comment_posted_date=cmt['snippet']['topLevelComment']['snippet']['publishedAt'],
                            Like_count=cmt['snippet']['topLevelComment']['snippet']['likeCount'],
                            Reply_count=cmt['snippet']['totalReplyCount']
                            )
                comment_data.append(data)
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                break
    except:
        pass
    return comment_data


# FUNCTION TO GET CHANNEL NAMES FROM MONGODB
def channel_names():
    ch_name = []
    for i in db.channel_details.find():
        ch_name.append(i['Channel_name'])
    return ch_name


# HOME PAGE
if selected == "Home":
    # Title Image
    # Set CSS style for the entire page
    page_style = """
    <style>
        body {
            font-family: Times New Roman ,sans-serif; /* Specify the desired font-family */
            font-size: 14px; /* Adjust the font size as needed */
            line-height: 1.5; /* Adjust the line height for readability */
        }
    </style>
    """

    # Apply the CSS style to the page
    st.write(page_style, unsafe_allow_html=True)

    # Title with black text and red underline
    st.markdown(
        "<h1 style='color: black; text-decoration: underline red;'>YouTube Data Harvesting and Warehousing</h1>",
        unsafe_allow_html=True)

    st.markdown("## :red[Domain] : Social Media-YouTube")
    st.markdown("## :red[Skills take away] : Python scripting, Data Collection,MongoDB, Streamlit, API integration, Data Managment using MongoDB (Atlas) and SQL")
    st.markdown(
        "## :red[Overview] : This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information on a YouTube channel, stores it in a MongoDB database, migrates it to a SQL data warehouse, and enables users to search for channel details and join tables to view data in the Streamlit app.")

# EXTRACT AND TRANSFORM PAGE
if selected == "Extract & Transform":
    tab1, tab2 = st.tabs(["$\huge 📝EXTRACT $", "$\huge 🚀TRANSFORM $"])

    # EXTRACT TAB
    with tab1:
        st.markdown("#    ")
        st.write("### Enter YouTube Channel_ID below :")
        ch_id = st.text_input(
            "Hint : Goto channel's home page > Right click > View page source > Find channel_id").split(',')

        if ch_id and st.button("Extract Data"):
            ch_details = get_channel_details(ch_id)
            st.write(f'#### Extracted data from :green["{ch_details[0]["Channel_name"]}"] channel')
            st.table(ch_details)

        if st.button("Upload to MongoDB"):
            with st.spinner('Please Wait for it...'):
                ch_details = get_channel_details(ch_id)
                v_ids = get_channel_videos(ch_id)
                vid_details = get_video_details(v_ids)


                def comments():
                    com_d = []
                    for i in v_ids:
                        com_d += get_comments_details(i)
                    return com_d


                comm_details = comments()
                collections1 = db.channel_details
                collections1.insert_many(ch_details)

                collections2 = db.video_details
                collections2.insert_many(vid_details)

                collections3 = db.comments_details
                collections3.insert_many(comm_details)
                st.success("Upload to MongoDB successful !!")

    # TRANSFORM TAB
    with tab2:
        st.markdown("#   ")
        st.markdown("### Select a channel to begin Transformation to SQL")
        ch_names = channel_names()
        user_inp = st.selectbox("Select channel", options=ch_names)

    # Functions for inserting data into SQL tables
    def insert_into_channels():
        collections = db.channel_details
        query = """INSERT INTO channels VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"""

        for i in collections.find({"channel_name": user_inp}, {'_id': 0}):
            mycursor.execute(query, tuple(i.values()))
        mydb.commit()


    def insert_into_videos():
        collections1 = db.video_details
        query1 = """INSERT INTO videos VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

        for i in collections1.find({"channel_name": user_inp}, {'_id': 0}):
            values = [str(val).replace("'", "''").replace('"', '""') if isinstance(val, str) else val for val in
                      i.values()]
            mycursor.execute(query1, tuple(values))
            mydb.commit()


    def insert_into_comments():
        collections1 = db.video_details
        collections2 = db.comments_details
        query2 = """INSERT INTO comments VALUES(%s,%s,%s,%s,%s,%s,%s)"""

        for vid in collections1.find({"channel_name": user_inp}, {'_id': 0}):
            for i in collections2.find({'Video_id': vid['Video_id']}, {'_id': 0}):
                mycursor.execute(query2, tuple(i.values()))
                mydb.commit()

    if st.button("Submit"):
        try:
            insert_into_videos()
            insert_into_channels()
            insert_into_comments()
            st.success("Transformation to MySQL Successful !!")
        except:
            st.error("Channel details already transformed !!")

# VIEW PAGE
if selected == "View":

    st.write("## :red[Select any question to get Insights]")
    questions = st.selectbox('Questions',
                             ['1. What are the names of all the videos and their corresponding channels?',
                              '2. Which channels have the most number of videos, and how many videos do they have?',
                              '3. What are the top 10 most viewed videos and their respective channels?',
                              '4. How many comments were made on each video, and what are their corresponding video names?',
                              '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                              '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                              '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                              '8. What are the names of all the channels that have published videos in the year 2022?',
                              '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                              '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])

    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT Video_name AS Video_name, channel_name AS Channel_Name
                            FROM videos
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, total_videos AS Total_Videos
                            FROM channels
                            ORDER BY total_videos DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        # st.bar_chart(df,x= mycursor.column_names[0],y= mycursor.column_names[1])
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, Video_name AS Video_Title, View_count AS Views 
                            FROM videos
                            ORDER BY views DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT a.video_id AS Video_id, Video_name AS Video_Title, b.Total_Comments
                            FROM videos AS a
                            LEFT JOIN (SELECT video_id,COUNT(comment_id) AS Total_Comments
                            FROM comments GROUP BY video_id) AS b
                            ON a.video_id = b.video_id
                            ORDER BY b.Total_Comments DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,Video_name AS Title,Like_count AS Like_Count 
                            FROM videos
                            ORDER BY Like_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most liked videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[2],
                     y=mycursor.column_names[1],
                     orientation='h',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT Video_name AS Title, Like_count AS Like_count
                            FROM videos
                            ORDER BY Like_count DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name, channel_views AS Views
                            FROM channels
                            ORDER BY views DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Channels vs Views :]")
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT channel_name AS Channel_Name
                            FROM videos
                            WHERE published_date LIKE '2022%'
                            GROUP BY channel_name
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
        st.write(df)

    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT channel_name AS Channel_Name,
                            AVG(duration)/60 AS "Average_Video_Duration (mins)"
                            FROM videos
                            GROUP BY channel_name
                            ORDER BY AVG(duration)/60 DESC""")
        df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)

        df['Average_Video_Duration (mins)'] = df['Average_Video_Duration (mins)'].apply(
            lambda x: f'{int(x):02}:{int((x % 1) * 60):02}:{int(((x % 1) * 60) % 1 * 60):02}')

        st.write(df)
        st.write("### :green[Avg video duration for channels :]")
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
        st.plotly_chart(fig, use_container_width=True)

    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
         mycursor.execute("""SELECT Video_id AS Video_ID, Comment_count AS Comments
                                FROM comments
                                ORDER BY Comment_count DESC
                                LIMIT 10""")
         df = pd.DataFrame(mycursor.fetchall(), columns=mycursor.column_names)
         st.write(df)
         st.write("### :green[Videos with most comments :]")
         fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                     )
         st.plotly_chart(fig, use_container_width=True)



