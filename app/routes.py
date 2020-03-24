from flask import render_template, request, make_response
from flask import current_app as app
from .models import db, User, Tweet

@app.route("/", methods = ['GET'])
def home():
    return render_template('index.html')

@app.route("/new_user", methods = ['GET'])
def new_user():
    return render_template('create_user_form.html')

@app.route('/create_user', methods = ['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']

        username_exists = User.query.filter(User.username==username).first()
        if username_exists:
            return make_response(f"Username {username} already exists!")
         
        new_username = User(username=username)
        db.session.add(new_username)
        db.session.commit()
        return make_response(f"Username {username} Successfully Created!")

@app.route('/users', methods = ['GET'])
def list_users():
    users = User.query.all()
    return render_template("users.html", users=users)

@app.route('/new_tweet', methods = ['GET'])
def new_tweet():
    return render_template('create_tweet_form.html')

@app.route('/create_tweet', methods = ['GET', 'POST'])
def create_tweet():
    if request.method == 'POST':
        user_id = request.form['user_id']
        tweet = request.form['tweet']

        new_tweet = Tweet(user_id=user_id, tweet=tweet)
        db.session.add(new_tweet)
        db.session.commit()
        return make_response(f"Tweet created!")



