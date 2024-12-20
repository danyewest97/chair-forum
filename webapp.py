from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth
#from flask_oauthlib.contrib.apps import github #import to make requests to GitHub's OAuth
from flask import render_template

import pprint
import os
import pymongo
import sys
from bson.objectid import ObjectId

import random as RANDOM
from time import strftime, localtime

# This code originally from https://github.com/lepture/flask-oauthlib/blob/master/example/github.py
# Edited by P. Conrad for SPIS 2016 to add getting Client Id and Secret from
# environment variables, so that this will work on Heroku.
# Edited by S. Adams for Designing Software for the Web to add comments and remove flash messaging


# This code connects to the database we are using, so that we can access info about users and posts, such as login info
connection_string = os.environ["MONGO_CONNECTION_STRING"]
db_name = os.environ["MONGO_DBNAME"]

client = pymongo.MongoClient(connection_string)
db = client[db_name]
posts = db["Posts"]
admins = db["Admins"]



# Pings to show if you have successfully connected to the MongoDB database
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Now the db variable can be used to access the ChairDB database to get info about users and posts


app = Flask(__name__)

app.debug = False #Change this to False for production
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Remove once done debugging

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)
oauth.init_app(app) #initialize the app to be able to make requests for user information

#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)


#context processors run before templates are rendered and add variable(s) to the template's context
#context processors must return a dictionary 
#this context processor adds the variable logged_in to the conext for all templates
@app.context_processor
def inject_logged_in():
    is_logged_in = 'github_token' in session #this will be true if the token is in the session and false otherwise
    return {"logged_in":is_logged_in}

@app.route('/')
def home():
    return render_template('home.html')

#redirect to GitHub's OAuth page and confirm callback URL
@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='https')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
    session.clear()
    return render_template('message.html', message='You were logged out')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            #pprint.pprint(vars(github['/email']))
            #pprint.pprint(vars(github['api/2/accounts/profile/']))
            message='You were successfully logged in as ' + session['user_data']['login'] + '.'
        except Exception as inst:
            session.clear()
            print(inst)
            message='Unable to login, please try again.  '
    return render_template('message.html', message=message)

# Loads posts page and checks in what order to load the posts. Latest 5, oldest 5, or a random 5.
@app.route('/posts')
def renderPosts():
    is_admin = check_is_admin()
    print(is_admin)
    if "postMode" not in session:
        session["postMode"] = "latest" #sets how posts should be ordered on posts.html page
    count = posts.count_documents({})
    loadedPosts = []
    if session["postMode"] == "latest":
        for i in range(5):
            loadedPosts.append(posts.find()[count - i - 1])
    elif session["postMode"] == "oldest":
        for i in range(5):
            loadedPosts.append(posts.find()[i])
    elif session["postMode"] == "random":
        for i in range(5):
            loadedPosts.append(posts.find()[RANDOM.randint(0,count-1)])
        
    return render_template('posts.html',posts=loadedPosts,is_admin=is_admin)

# Loads a singular post when the user clicks on a post on the posts page
# Also shows replies on that post, and allows the user to reply
@app.route('/post', methods=['GET'])
def renderPost():
    postID = request.args["post-id"]
    for document in posts.find({"_id":ObjectId(postID)}):
        currPost = document
    
    return render_template("single-post.html", post=currPost)


# Changes post mode to latest 5
@app.route('/latest')
def latest():
    session["postMode"] = "latest"
    return redirect("/posts", code=302)

# Changes post mode to oldest 5
@app.route('/oldest')
def oldest():
    session["postMode"] = "oldest"
    return redirect("/posts", code=302)

# Changes post mode to a random 5
@app.route('/random')
def random():
    session["postMode"] = "random"
    return redirect("/posts", code=302)


@app.route('/googleb4c3aeedcc2dd103.html')
def render_google_verification():
    return render_template('googleb4c3aeedcc2dd103.html')

#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session['github_token']


# User creates a new post and it is sent to the database. Then, the user is redirected back to the posts page
@app.route('/create_post',methods=["POST"])
def create_post():
    title = request.form["post_title"]
    msg = request.form["post_body"]
    username = session['user_data']['login']
    uid = session['user_data']['id']
    datetime = strftime("%d/%m/%Y %H:%M:%S", localtime())
    if 'github_token' in session:
        create_new_post(uid,msg,title,username,datetime)
    return redirect("/posts", code=302)


# Nested function for /create_post app route. Takes input and puts input into the database
def create_new_post(uid,msg,title,username,datetime):
    newPost = {"uid":uid,"message":msg,"title":title,"username":username,"datetime":datetime}
    posts.insert_one(newPost)


def check_is_admin():
    try:
        if admins.find({"uid":session['user_data']['id']}):
            admin = True
        else:
            print("BLAH")
            admin = False
    except:
        admin = False
    
    return admin
    
    
    
@app.route('/delete_post',methods=["POST"])
def delete_post():
    posts.delete_one({"_id":ObjectId(request.form["post_id"])})
    return redirect("/posts", code=302)



if __name__ == '__main__':
    app.run()
