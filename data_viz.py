import pandas as pd
import webscraping_functions as ws
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from datetime import datetime, timedelta
# get articles - from twitter extract and from daily extract
articles = pd.read_pickle("C:\\Users\\France.DESKTOP-62OTKJ5\\PycharmProjects\\morpheus_analytics\\total_articles.pkl")
articles2 = pd.read_pickle("C:\\Users\\France.DESKTOP-62OTKJ5\\PycharmProjects\\morpheus_analytics\\extract_articles_twitter_coindesk.pkl")
articles = pd.concat([articles,articles2],ignore_index=True)
articles = articles.dropna(subset=['body'],axis=0).reset_index()


# get all entities already extracted
entities = pd.read_pickle("C:\\Users\\France.DESKTOP-62OTKJ5\\Documents\\Upwork\\morpheusanalytics\\data\\entities_articles.pkl")

locations  = entities.loc[entities.entity_type=='2']


# compute new features (date, week) and extract domain from url
articles['article_day'] = articles.article_date.dt.date
articles['article_week'] = articles.article_date.dt.week
articles["article_week_first_day"] = articles['article_day'] - articles.article_date.dt.weekday* timedelta(days=1)
articles = articles.loc[articles.article_date.dt.year >=2020]
articles = articles.loc[articles.article_week.between(12,20)]
articles['domain'] = articles.url.apply(ws.extract_domain)

articles_week  = articles.groupby(['article_week_first_day','domain']).agg({'url':'count'}).reset_index()
articles_week.columns = ['Week','Website','Articles published']

# first plot: articles per week and domain
fig1 = px.bar(articles_week,x='Week',y='Articles published',color='Website',barmode='group')
fig1.update_layout(title='Articles per week',xaxis_title='Date',yaxis_title='Articles')

# list of words to see in plot per keyword
words_to_follow = ['defi','makerdao','ripple','blockchain','crypto','bitcoin','ethereum']

# all cleaned words in articles
words = pd.read_pickle("C:\\Users\\France.DESKTOP-62OTKJ5\\PycharmProjects\\morpheus_analytics\\words_in_articles.pkl")
words['article_week'] = words.article_date.dt.week
words["article_week_first_day"] = words.article_date.dt.date - words.article_date.dt.weekday* timedelta(days=1)

words_csv = words.article_words.value_counts()

words_csv.to_csv('words.csv')

filter_words = words.loc[words.article_words.isin(words_to_follow) & words.article_week.between(12,20)]
words_count = filter_words.groupby(['article_week_first_day','article_words']).agg({'url': 'count'}).reset_index()
words_count.columns = ['Week','Keyword','Frequency']
# second plot:
fig2 = px.line(words_count,x='Week',y='Frequency',color='Keyword')
fig2.update_traces(hovertemplate= '<b> Week of %{x} </b> <br> Word appears %{y} times in articles')
fig2.update_layout(title='Keywords trends',xaxis_title='Date',yaxis_title='Frequency')

entities = pd.read_pickle("C:\\Users\\France.DESKTOP-62OTKJ5\\PycharmProjects\\morpheus_analytics\\entities_articles.pkl")
locations = entities.loc[entities.entity_type==2]
locations = locations.loc[locations.entity_wikipedia_article !='']
locations_to_follow = ['United_States','China','Europe','United_Kingdom','Australia']
locations['article_week'] = locations.article_date.dt.week
locations["article_week_first_day"] = locations.article_date.dt.date - locations.article_date.dt.weekday* timedelta(days=1)
filter_locations = locations.loc[locations.entity_wikipedia_article.isin(locations_to_follow) & locations.article_week.between(12,20)]
locations_count = filter_locations.groupby(['article_week_first_day','entity_wikipedia_article']).agg({'url': 'count'}).reset_index()
locations_count.columns = ['Week','Country','Frequency']
fig3 = px.line(locations_count,x='Week',y='Frequency',color='Country')
fig3.update_layout(title='Geographical trends',xaxis_title='Date',yaxis_title='Frequency')
fig3.update_traces(hovertemplate= '<b> Week of %{x} </b> <br> Country appears %{y} times in articles')


fig = [fig2,fig3]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1('Trends in articles'),
    dcc.Graph(figure=fig1),
    html.Div(children=[
        html.Div(dcc.Graph(figure=fig3),style={'display':'inline-block','width':'50%'}),
        html.Div(dcc.Graph(figure=fig2),style={'display':'inline-block','width':'50%'})],
        style = {'width': '100%','display':'inline-block'}
    )

])

if __name__ == '__main__':
    app.run_server(debug=True)