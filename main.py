from flask import Flask, jsonify, request
import csv
from flask_cors import CORS

n = 0

from csv import reader

all_articles = []

with open('articles.csv', encoding="utf8") as f:
    csvreader = reader(f)
    data = list(csvreader)
    all_articles = data[1:]

liked_articles = []
not_liked_articles = []

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("articles.csv")
df.dropna()

count = CountVectorizer(stop_words="english")
count_matrix = count.fit_transform(df["title"].values.astype('U'))

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
indices = pd.Series(df.index, index=df['title'])

def get_recommendation(title, cosine_sim):
    idx=indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x:x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    #print(df['title'].iloc[movie_indices])
    return (df['title'].iloc[movie_indices])

output = df[["url", "title", "text", "lang", "total_events"]].head(20).values.tolist()

app = Flask(__name__)
CORS(app)

@app.route("/get-article")
def get_article():
    article_data = {
        "url": all_articles[n][11],
        "title": all_articles[n][12],
        "text": all_articles[n][13],
        "lang": all_articles[n][14],
        "total_events": all_articles[n][15]
    }
    print(all_articles[0][12])
    return jsonify({
        "data": article_data,
        "status": "success"
    })

@app.route("/liked-article", methods=["POST"])
def liked_article():
    article = all_articles[0]
    liked_articles.append(article)
    global n
    n = n + 1
    if n == 3047:
        n = 0
    return jsonify({
        "status": "success"
    }), 201
    

@app.route("/unliked-article", methods=["POST"])
def unliked_article():
    article = all_articles[0]
    not_liked_articles.append(article)
    global n
    n = n + 1
    if n == 3047:
        n = 0
    return jsonify({
        "status": "success"
    }), 201

@app.route("/popular-articles")
def popular_articles():
    article_data = []
    for article in output:
        dat = {
            "url": article[0],
            "title": article[1],
            "text": article[2],
            "lang": article[3],
            "total_events": article[4]
        }
        article_data.append(dat)
    return jsonify({
        "data": article_data,
        "status": "success"
    }), 200

@app.route("/recommended-articles")
def recommended_articles():
    all_recommended = []
    for liked_article in liked_articles:    
        output = get_recommendation(liked_article[13], cosine_sim2)
        for data in output:
            all_recommended.append(data)
    all_recommended.sort()
    import itertools as it
    all_recommended = list(all_recommended for all_recommended,_ in it.groupby(all_recommended))
    article_data = []
    for recommended in all_recommended:
        dat = {
            "url": recommended[0],
            "title": recommended[1],    
            "text": recommended[2],
            "lang": recommended[3],
            "total_events": recommended[4]
        }
        article_data.append(dat)
    return jsonify({
        "data": article_data,
        "status": "success"
    }), 200

if __name__ == "__main__":
    app.run()