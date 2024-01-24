# app.py

from flask import Flask, request, render_template
import requests
import pandas as pd

app = Flask(__name__)

movies = pd.read_pickle('Model/movie_list.pkl')
similarity = pd.read_pickle('Model/similarity.pkl')

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/recommendation", methods=['GET', 'POST'])
def recommendation():
    movie_list = movies['title'].values
    status = False
    selected_movie = ''
    recommended_movies_name = []
    recommended_movies_poster = []

    if request.method == "POST":
        try:
            if 'movies' in request.form:
                selected_movie = request.form['movies']
                recommended_movies_name, recommended_movies_poster = recommend(selected_movie)
                status = True

        except Exception as e:
            error = {'error': e}
            return render_template("recommendation.html", error=error, movie_list=movie_list, status=status)

    return render_template("recommendation.html", movie_list=movie_list, status=status, selected_movie=selected_movie,
                           recommended_movies_name=recommended_movies_name, recommended_movies_poster=recommended_movies_poster)

if __name__ == "__main__":
    app.run(debug=True)
