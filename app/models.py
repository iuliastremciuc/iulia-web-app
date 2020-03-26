from app import db

# class User(db.Model):

#     __tablename__ = "users"

#     id = db.Column(db.Integer, primary_key = True)
#     username = db.Column(db.String(255), nullable = False)

# class Tweet(db.Model):

#     __tablename__ = "tweets"

#     id = db.Column(db.Integer, primary_key = True)
#     user_id = db.Column(db.Integer, nullable = False)
#     tweet = db.Column(db.String(280), nullable = False)

class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    screen_name = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String)
    location = db.Column(db.String)
    followers_count = db.Column(db.Integer)
    latest_tweet_id = db.Column(db.BigInteger)

class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("user.id"))
    full_text = db.Column(db.String(500))
    embedding = db.Column(db.PickleType)

    user = db.relationship("User", backref=db.backref("tweets", lazy=True))