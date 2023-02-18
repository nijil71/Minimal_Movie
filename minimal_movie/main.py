import requests
from flask import Flask, render_template, request, redirect, url_for,jsonify,make_response
from flask_sqlalchemy import SQLAlchemy
import urllib.parse 


api_key = "98e1a4d4f62b6756e8cc514c113448cb"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///watchlist.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


db = SQLAlchemy(app)
app.app_context().push()

# @app.route('/')
# def home():
#     return render_template('home.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('index'))
#     return render_template('login.html', error=error)
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    image=db.Column(db.String(80),nullable=False)
    description = db.Column(db.Text, nullable=False)
    watchlist = db.relationship("Watchlist", backref="movie", lazy=True)


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_ip = db.Column(db.String(20), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)


@app.route("/watchlist/<int:movie_id>", methods=["POST"])
def add_to_watchlist(movie_id):
    user_ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    watchlist = Watchlist.query.filter_by(user_ip=user_ip, movie_id=movie_id).first()
    if watchlist:
        return redirect(url_for("index"))
    movieid=get_movie_ids()
    tvid=get_tv_ids()
    

    try:
        if movie_id in movieid:
            movie_details=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}").json()
            movie=Movie(id=movie_id,title=movie_details["title"],description=movie_details["overview"],image=movie_details["poster_path"])
            db.session.add(movie)
            db.session.commit()
        elif int(movie_id) in tvid:
            tv_details=requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}?api_key={api_key}").json()
            tv=Movie(id=movie_id,title=tv_details["name"],description=tv_details["overview"],image=tv_details["poster_path"])
            db.session.add(tv)
            db.session.commit()
    except:
        db.session.rollback()
    new_watchlist_item = Watchlist(user_ip=user_ip, movie_id=movie_id)
    db.session.add(new_watchlist_item)
    db.session.commit()
    return redirect(url_for("index"))

    # try:
    #     if not movie:
    #         movie_details=requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}").json()
    #         movie=Movie(id=movie_id,title=movie_details["title"],description=movie_details["overview"],image=movie_details["poster_path"])
    #         db.session.add(movie)
    #         db.session.commit()
    # except:
    #         tv_details=requests.get(f"https://api.themoviedb.org/3/tv/{movie_id}?api_key={api_key}").json()
    #         tv=Movie(id=movie_id,title=tv_details["name"],description=tv_details["overview"],image=tv_details["poster_path"])
    #         db.session.add(tv)
    #         db.session.commit()



@app.route("/watchlist/<int:movie_id>/delete", methods=["POST"])
def delete_from_watchlist(movie_id):
    user_ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    Watchlist.query.filter_by(user_ip=user_ip, movie_id=movie_id).delete()
    db.session.commit()
    return redirect(url_for("watchlist"))



@app.route("/watchlist")
def watchlist():
    user_ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
    watchlist = Watchlist.query.filter_by(user_ip=user_ip).all()
    movies = [
        Movie.query.get(watchlist_item.movie_id) for watchlist_item in watchlist
    ]

    return render_template("watchlist.html", movies=movies)


def get_category_name(category_id):
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['genres']
    for i in result:
        if i['id'] == category_id:
            return i['name']


def get_images(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'/images?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['backdrops']
    return result


def get_network_url(network_id):
    url = 'https://api.themoviedb.org/3/network/' + \
        str(network_id)+'?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['homepage']
    return result


def get_movie_runtime(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['runtime']
    # convert runtime to hours and minutes
    hours = result // 60
    minutes = result % 60
    return f'{hours}h {minutes}m'


def get_trending():
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    return result


def get_popular_movies():
    url = 'https://api.themoviedb.org/3/movie/popular?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    return results

    



def get_popular_tv():
    url = 'https://api.themoviedb.org/3/tv/popular?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    return results

def get_popular_tv_ids():
    url = 'https://api.themoviedb.org/3/tv/popular?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    tv_ids = []
    for i in results:
        tv_ids.append(i['id'])
    return tv_ids

def get_new_releases():
    url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    return results

def get_new_releases_movie_ids():
    url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    movie_ids = []
    for i in results:
        movie_ids.append(i['id'])
    return movie_ids

def get_new_releases_tv_ids():
    url = 'https://api.themoviedb.org/3/tv/on_the_air?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    tv_ids = []
    for i in results:
        tv_ids.append(i['id'])
    return tv_ids


def get_youtube_video(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'/videos?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    for i in result:
        if i['site'] == 'YouTube':
            youtube_video = i['key']
            url = 'https://www.youtube.com/watch?v='+youtube_video
            return url


def embeded_youtube(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'/videos?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    youtube_video_key = result[-1]['key']
    # you_url = f'https://www.youtube.com/embed/{youtube_video_key}?autoplay=1&mute=1'
    you_url = f'https://www.youtube.com/watch?v={youtube_video_key}'
    return you_url


def get_movie_ids():
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    mov = []
    # if the result is a movie, get the movie id
    for i in result:
        if i['media_type'] == 'movie':
            mov.append(i['id'])
    return mov


def get_popular_movie_ids():
    url = 'https://api.themoviedb.org/3/movie/popular?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    movie = []
    for i in results:
        movie.append(i['id'])
    return movie

def get_popular_tv_ids():
    url = 'https://api.themoviedb.org/3/tv/popular?api_key=' + \
        api_key
    response = requests.get(url)
    data = response.json()
    results = data['results']
    tv = []
    for i in results:
        tv.append(i['id'])
    return tv

def get_tv_ids():
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    tv = []
    # if the result is a tv show, get the tv show id
    for i in result:
        if i['media_type'] == 'tv':
            tv.append(i['id'])
    return tv


@app.route('/')
def index():
    trending = get_trending()
    popular = get_popular_movies()
    popular_tv = get_popular_tv()
    new_releases = get_new_releases()
    # get all trending movie ids
    movie_ids = [movie['id'] for movie in trending]
    # get youtube video for each movie
    # youtube_videos = [get_youtube_video(
    #     movie_id) for movie_id in movie_ids]

    # # add youtube video to trending movie
    # for i in range(len(trending)):
    #     #     trending[i]['youtube_video'] = youtube_videos[i]
    # except:
    #     pass
    

    return render_template('index.html', trending=trending, popular=popular, popular_tv=popular_tv, new_releases=new_releases)
    

# get search results of both movies and tv shows

@app.route('/results', methods=['GET', 'POST'])
def results():
    # get search results of both movies and tv shows
    if request.method == 'POST':
        search = request.form['movie_name']
        url = 'https://api.themoviedb.org/3/search/multi?api_key='+api_key+'&query='+search
        response = requests.get(url)
        r = response.json()
        result = r['results']
        for i in result:
            if i['media_type'] == 'movie':
                i['media_type'] = 'Movie'

            elif i['media_type'] == 'tv':
                i['media_type'] = 'TV Show'

        return render_template('search_results.html', result=result)

    # if request.method == 'POST':
    #     search = request.form['movie_name']
    #     url = 'https://api.themoviedb.org/3/search/movie?api_key='+api_key+'&query='+search
    #     response = requests.get(url)
    #     r = response.json()
    #     result = r['results']
    #     for i in result:
    #         genre = i['genre_ids']
    #         genre_name = [get_category_name(category_id)
    #                       for category_id in genre]
    #         i['genre_name'] = genre_name

    #     return render_template('search_results.html', result=result)


# get tv and movie details
@app.route('/details/<movie_id>')
def details(movie_id):
    movieid = get_movie_ids()
    tv_id = get_tv_ids()
    try:
        if int(movie_id) in movieid:
            url = 'https://api.themoviedb.org/3/movie/' + \
                str(movie_id)+'?api_key='+api_key
            print(url)
            response = requests.get(url)
            data = response.json()
            name = data['title']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']

            year = data['release_date'].split('-')[0]
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]

            runtime = get_movie_runtime(movie_id)

            return render_template('details.html', name=name, poster=poster, year=year, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, trailer=trailer, runtime=runtime)
        elif int(movie_id) in tv_id:
            url = 'https://api.themoviedb.org/3/tv/' + \
                str(movie_id)+'?api_key='+api_key
            response = requests.get(url)
            data = response.json()
            name = data['name']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']
            # year = data['release_date']
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]
            episodes = data['number_of_episodes']
            network = data['networks']
            nietwork_id = [i['id'] for i in network]
            for i in nietwork_id:
                network_link = get_network_url(i)
            return render_template('details.html', name=name, poster=poster, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, episodes=episodes, network=network, network_link=network_link, trailer=trailer)

    except Exception as e:
        print(e)
        return render_template('index.html')

@app.route('/popular_details/<movie_id>')
def popular_details(movie_id):
    movieid = get_popular_movie_ids()
    tv_id = get_popular_tv_ids()
    try:
        if int(movie_id) in movieid:
            url = 'https://api.themoviedb.org/3/movie/' + \
                str(movie_id)+'?api_key='+api_key
            print(url)
            response = requests.get(url)
            data = response.json()
            name = data['title']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']

            year = data['release_date'].split('-')[0]
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]

            runtime = get_movie_runtime(movie_id)

            return render_template('details.html', name=name, poster=poster, year=year, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, trailer=trailer, runtime=runtime)
        elif int(movie_id) in tv_id:
            url = 'https://api.themoviedb.org/3/tv/' + \
                str(movie_id)+'?api_key='+api_key
            response = requests.get(url)
            data = response.json()
            name = data['name']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']
            # year = data['release_date']
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]
            episodes = data['number_of_episodes']
            network = data['networks']
            nietwork_id = [i['id'] for i in network]
            for i in nietwork_id:
                network_link = get_network_url(i)
            return render_template('details.html', name=name, poster=poster, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, episodes=episodes, network=network, network_link=network_link, trailer=trailer)

    except Exception as e:
        print(e)
        return render_template('index.html')
@app.route('/popular_tv_details/<movie_id>')
def popular_tv_details(movie_id):
    tv_id = get_popular_tv_ids()
    try:

        if int(movie_id) in tv_id:
            url = 'https://api.themoviedb.org/3/tv/' + \
                str(movie_id)+'?api_key='+api_key
            response = requests.get(url)
            data = response.json()
            name = data['name']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']
            # year = data['release_date']
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]
            episodes = data['number_of_episodes']
            network = data['networks']
            nietwork_id = [i['id'] for i in network]
            for i in nietwork_id:
                network_link = get_network_url(i)
            return render_template('details.html', name=name, poster=poster, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, episodes=episodes, network=network, network_link=network_link, trailer=trailer)

    except Exception as e:
        print(e)
        return render_template('index.html')
        

@app.route('/new_details/<movie_id>')
def new_details(movie_id):
    movieid = get_new_releases_movie_ids()
    tv_id = get_new_releases_tv_ids()
    try:
        if int(movie_id) in movieid:
            url = 'https://api.themoviedb.org/3/movie/' + \
                str(movie_id)+'?api_key='+api_key
            print(url)
            response = requests.get(url)
            data = response.json()
            name = data['title']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']

            year = data['release_date'].split('-')[0]
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]

            runtime = get_movie_runtime(movie_id)

            return render_template('details.html', name=name, poster=poster, year=year, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, trailer=trailer, runtime=runtime)
        elif int(movie_id) in tv_id:
            url = 'https://api.themoviedb.org/3/tv/' + \
                str(movie_id)+'?api_key='+api_key
            response = requests.get(url)
            data = response.json()
            name = data['name']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']
            # year = data['release_date']
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]
            episodes = data['number_of_episodes']
            network = data['networks']
            nietwork_id = [i['id'] for i in network]
            for i in nietwork_id:
                network_link = get_network_url(i)
            return render_template('details.html', name=name, poster=poster, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, episodes=episodes, network=network, network_link=network_link, trailer=trailer)

    except Exception as e:
        print(e)
        return render_template('index.html')
    
@app.route('/results/movie/<movie_id>')
def moviescreen(movie_id):
    movie_id = movie_id
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'?api_key='+api_key
    response = requests.get(url)
    data = response.json()
    poster = data['poster_path']
    image_url = 'https://image.tmdb.org/t/p/w500{}'.format(poster)
    movie_name = data['title']
    year = data['release_date'].split('-')[0]
    overview = data['overview']
    rating = data['vote_average']
    vote_count = data['vote_count']
    try:
        trailer = embeded_youtube(movie_id)
    except:
        # dont show trailer if there is no trailer
        trailer = None
    category = data['genres']
    category_name = [i['name'] for i in category]

    runtime = get_movie_runtime(movie_id)

    return render_template('movie_details.html', movie_name=movie_name, category_name=category_name, image_url=image_url, year=year, overview=overview, rating=rating, vote_count=vote_count, runtime=runtime, trailer=trailer)


@app.route('/results/tv/<movie_id>')
def tvscreen(movie_id):
    movie_id = movie_id
    url = 'https://api.themoviedb.org/3/tv/' + \
        str(movie_id)+'?api_key='+api_key
    response = requests.get(url)
    data = response.json()
    poster = data['poster_path']
    image_url = 'https://image.tmdb.org/t/p/w500{}'.format(poster)
    movie_name = data['name']
    # year = data['release_date']
    overview = data['overview']
    rating = data['vote_average']
    vote_count = data['vote_count']
    try:
        trailer = embeded_youtube(movie_id)
    except:
        # dont show trailer if there is no trailer
        trailer = None
    category = data['genres']
    category_name = [i['name'] for i in category]
    episodes = data['number_of_episodes']
    network = data['networks']
    nietwork_id = [i['id'] for i in network]
    for i in nietwork_id:
        network_link = get_network_url(i)

    return render_template('tv_details.html', movie_name=movie_name, category_name=category_name, image_url=image_url, overview=overview, rating=rating, vote_count=vote_count, episodes=episodes, trailer=trailer, network=network, network_link=network_link)

@app.route("/search-movies")
def search_movies():
    query = request.args.get("q")
    url = 'https://api.themoviedb.org/3/search/movie?api_key='+api_key+'&query='+query
    response = requests.get(url)
    data = response.json()['results']
    return jsonify([{ "title": result["title"] } for result in data if result["title"].startswith(query)])



    

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
