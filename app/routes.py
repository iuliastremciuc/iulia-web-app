from flask import render_template, request, make_response
from flask import current_app as app
from .models import db, User, Tweet
from app.services.twitter_service import twitter_api_client
from app.services.basilica_service import basilica_api_client
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_breast_cancer
from app.cancer_classifier import load_model

def store_twitter_user_data(screen_name):
    api = twitter_api_client()
    twitter_user = api.get_user(screen_name)
    print(twitter_user)
    statuses = api.user_timeline(screen_name, tweet_mode="extended", count=50)
    
    db_user = User.query.get(twitter_user.id) or User(id=twitter_user.id)
    db_user.screen_name = twitter_user.screen_name
    db_user.name = twitter_user.name
    db_user.location = twitter_user.location
    db_user.followers_count = twitter_user.followers_count
    db.session.add(db_user)
    db.session.commit()

    print("STATUS COUNT:", len(statuses))
    basilica_api = basilica_api_client()
    all_tweet_texts = [status.full_text for status in statuses]
    embeddings = list(basilica_api.embed_sentences(all_tweet_texts, model="twitter"))
    print("NUMBER OF EMBEDDINGS", len(embeddings))

    # TODO: explore using the zip() function maybe...
    counter = 0
    for status in statuses:
        print(status.full_text)
        print("----")
        
        # Find or create database tweet:
        db_tweet = Tweet.query.get(status.id) or Tweet(id=status.id)
        db_tweet.user_id = status.author.id # or db_user.id
        db_tweet.full_text = status.full_text
        embedding = embeddings[counter]
        print(len(embedding))
        db_tweet.embedding = embedding
        db.session.add(db_tweet)
        counter+=1
    db.session.commit()

    return db_user, statuses

@app.route("/", methods = ['GET'])
def home():
    return render_template('index.html')

@app.route("/new_user", methods = ['GET'])
def new_user():
    return render_template('import_user_form.html')

@app.route("/import_user", methods = ['GET', 'POST'])
def import_user():
    if request.method == 'POST':
        username = request.form['username']
        db_user, statuses = store_twitter_user_data(username)
        return make_response(f"Imported {username} and {username}'s tweets!")


@app.route('/users', methods = ['GET'])
def list_users():
    users = User.query.all()
    return render_template("users.html", users=users)


@app.route("/stats/cancer")
def iris():
    X, y = load_breast_cancer(return_X_y=True)

    clf = load_model()
    return str(clf.predict(X[:2, :]))


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == 'POST':
        print("PREDICT ROUTE...")
        print("FORM DATA:", dict(request.form))
        
        screen_name_a = request.form["screen_name_a"]
        screen_name_b = request.form["screen_name_b"]
        tweet_text = request.form["tweet_text"]
        

        print("-----------------")
        print("FETCHING TWEETS FROM THE DATABASE...")
        # todo: wrap in a try block in case the user's don't exist in the database
        user_a = User.query.filter(User.screen_name == screen_name_a).one()
        user_b = User.query.filter(User.screen_name == screen_name_b).one()
        user_a_tweets = user_a.tweets
        user_b_tweets = user_b.tweets
        
        print("USER A", user_a.screen_name, len(user_a.tweets))
        print("USER B", user_b.screen_name, len(user_b.tweets))

        print("-----------------")
        print("TRAINING THE MODEL...")
        embeddings = []
        labels = []
        for tweet in user_a_tweets:
            labels.append(user_a.screen_name)
            embeddings.append(tweet.embedding)

        for tweet in user_b_tweets:
            labels.append(user_b.screen_name)
            embeddings.append(tweet.embedding)

        #breakpoint()
        # inspect the x and y values to make sure they are the best format for training
        # maybe need to impute?
        classifier = LogisticRegression(random_state=0, solver='lbfgs') # for example
        classifier.fit(embeddings, labels)
        

        print("-----------------")
        print("MAKING A PREDICTION...")
        

        basilica_conn = basilica_api_client()
        example_embedding = basilica_conn.embed_sentence(tweet_text, model="twitter")
        result = classifier.predict([example_embedding])
        
        return render_template("result.html",
            screen_name_a=screen_name_a,
            screen_name_b=screen_name_b,
            tweet_text=tweet_text,
            screen_name_most_likely=result[0]
        )
    else:
        return render_template('predict_tweet.html')
