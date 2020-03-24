from app import db

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), nullable = False)

class Tweet(db.Model):

    __tablename__ = "tweets"

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable = False)
    tweet = db.Column(db.String(280), nullable = False)