# Import Libraries
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from PIL import Image

st.set_page_config(layout="wide")

# Title
st.markdown("<h1>⚽ NFL Football Stats Explorer ⚽</h1>",
            unsafe_allow_html=True)

col1, col2 = st.beta_columns(2)


# Data source : https://www.pro-football-reference.com/

# Features Meaning
data = {
    'Data': ['Player', 'Tm', 'Pos', 'G', 'GS', 'Att', 'Yds', 'TD', '1D', 'Lng', 'Y/A', 'Y/G', 'Fmb'],
    'Description': ['Player Name', 'Team', 'Position of Player in Team', 'Games Played', 'Game Started as an Offensive or Defensive Player', 'Rushing Attempts', 'Rushing Yards Gained', 'Rushing Touchdowns', 'First Down Rushing', 'Longest Rushing Attempt', 'Rushing Yards Per Attempt', 'Rushing Yards Per Game', 'Number of Times Fumbled both Lost and Recovered by Own Team']
}

desciption = pd.DataFrame(data)

# Sidebar
st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(2015, 2021))))


@st.cache  # Web scraping of NFL Player Stats
def load_data(year):
    url = "https://www.pro-football-reference.com/years/" + \
        str(year) + "/rushing.htm"
    html = pd.read_html(url, header=1)
    df = html[0]
    # Deletes repeating Headers
    raw = df.drop(df[df['Age'] == 'Age'].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)  # Rank Column
    return playerstats


playerstats = load_data(selected_year)

# Sidebar - Team selection
sorted_unique_team = sorted(playerstats['Tm'].unique())
selected_team = st.sidebar.multiselect(
    'Team', sorted_unique_team, sorted_unique_team)

# Sidebar - Position selection
unique_pos = ['RB', 'QB', 'WR', 'FB', 'TE']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

# Filtering Data
df_selected_team = playerstats[(playerstats['Tm'].isin(
    selected_team)) & (playerstats['Pos'].isin(selected_pos))]

# Data Representation (Rows and Columns)
col1.subheader('Display Player Stats of Selected Team(s)')
col1.write('Data Dimension : ' + str(df_selected_team.shape[0]) + ' Rows and ' + str(
    df_selected_team.shape[1]) + ' Columns.')
col1.dataframe(df_selected_team)

col2.subheader('Data Description')
col2.write('Description of Each Feature')
col2.write(desciption)


def filedownload(df):  # Download NFL Player Stats Data
    csv = df.to_csv(index=False)
    # Strings - Bytes Conversion
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="NFL Player Stats.csv">Download CSV File</a>'
    return href


col2.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Heatmap
if col1.button('Intercorrelation Heatmap'):
    col1.header('Intercorrelation Matrix Heatmap')
    df_selected_team.to_csv('NFL'+str(selected_year)+'.csv', index=False)
    df = pd.read_csv('NFL'+str(selected_year)+'.csv')

    corr = df.corr()
    mask = np.zeros_like(corr)
    mask[np.triu_indices_from(mask)] = True
    with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(7, 5))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
    col1.pyplot(f)
