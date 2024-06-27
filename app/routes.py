import os
from app import app, db, limiter
import ast
from flask import render_template, abort, request, jsonify, redirect, url_for, send_from_directory
from app.models import *
from flask_login import login_user, login_required, current_user, logout_user
from app.functions import *
import re
from datetime import datetime
from itertools import zip_longest
import hashlib
import random
from http import client
from collections import Counter

# library imports

# Config Variables
SMS_API_KEY = 'Kz0UCJKbjBQssj5pNUd76SGR6Qpi4Mjzguow7kcKL2U8HodrHeuUSy4hrZhl2J2W'

# functions
def verify_password(password, _hashed_password, salt):
    """this function for verify passwords with sha256 hash"""
    if sha256_hash(password, salt) == _hashed_password:
        return True
    else:
        return False

def SMS(phone, sms_code):
    '''this function for SMS sending'''

    # conn = client.HTTPSConnection("api.sms.ir")
    # payload = f"""{{
    #     "mobile": "{phone}",
    #     "templateId": 693544,
    #     "parameters": [
    #             {{
    #                 "name": "Code",
    #                 "value": "{sms_code}"
    #             }}
    #         ]
    # }}"""

    # headers = {
    #     'Content-Type': 'application/json',
    #     'Accept': 'text/plain',
    #     'x-api-key': SMS_API_KEY
    # }

    # conn.request("POST", "/v1/send/verify", payload, headers)
    # res = conn.getresponse()
    # data = res.read()


    print(sms_code)

    return True


def sha256_hash(password, salt):
    """This function generates texts using sha 256 encryption and salts"""

    # sha256 object
    hash_object = hashlib.sha256()
    # encoding the password
    hash_object.update(password.encode())
    hashed_text = hash_object.hexdigest()
    # salt adding
    hashed_text = hashed_text + salt
    return hashed_text


def salt_generator():
    """This function generates a random salt"""
    salt = ""
    chars = (
        "abcdefghijklmnopqrstuvwxyz+_-ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    )
    numbers = "3456789"
    len = int(random.choice(numbers))
    for i in range(len):
        salt += random.choice(chars)
    salt = salt + str(datetime.now())[1]

    return salt


def add_not_for_all(message):
    """this function for sending a notification for all users"""

    # creating a SQLAlchemy environment
    with app.app_context():
        # for in all users
        for u in User.query.all():
            # add a notification for the user
            n = Notification(content=message, user=u)
            # add to this session and commit changes
            db.session.add(n)
            db.session.commit()


def add_notification(user_id, message):
    """this function for sending a notification for a user
    usage: add_notification(user_id: int, notification: str)"""

    # create a SQLAlchemy environment
    with app.app_context():
        # add notification for user
        n = Notification(content=message, user=User.query.get(user_id))
        db.session.add(n)
        db.session.commit()


def seened_notification():
    """this function To change the status of all current user notifications to see"""
    with app.app_context():
        # 'for' in all notifications for current user and change to seen
        for notification in Notification.query.filter_by(user=current_user).all():
            notification.seened = True
            db.session.commit()


def changeScore(score):
    """this function for change current user score
    usage: changeScore(score: int)"""
    with app.app_context():
        u = User.query.get(current_user.id)

        u.gems = u.gems + score
        db.session.commit()


# !
root_url = "127"
# !


# error pages
@app.errorhandler(404)
def page_not_found(error):
    """this function to display 404 error page"""
    if current_user.is_authenticated:
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    else:
        n = 0

    return (
        render_template("errors/404.html", current_user=current_user, not_list=n),
        404,
    )


@app.errorhandler(500)
def server_error(error):
    """this function to display 500 error page"""
    if current_user.is_authenticated:
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    else:
        n = 0

    return (
        render_template("errors/500.html", current_user=current_user, not_list=n),
        500,
    )


@app.errorhandler(403)
def access_denied(error):
    """this function to display 403 error page"""
    if current_user.is_authenticated:
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    else:
        n = 0

    return (
        render_template("errors/403.html", current_user=current_user, not_list=n),
        403,
    )


# index route
@app.route("/")
def index():
    """this function for displaying index page"""

    # RegisteredNow for Show whether the user is currently registered or not
    RegisteredNow = False
    # if user go to here from login or register page...
    if request.args.get("login"):
        # form route is a variable for display referer
        from_route = request.referrer
        # if user go to here from login or register page and not registered
        if request.args.get("login") and not current_user.is_authenticated:
            # go back to login page
            return redirect(url_for("index"))
        # if user go to here from register page and registered now
        if (
            not current_user.registered
            and "/register" in from_route
            and request.args.get("login")
            and request.args.get("login") == "Register"
        ):
            add_notification(current_user.id, "ثبت نام شما را تبریک می گوییم!")
            current_user.registered = True
            RegisteredNow = True
            db.session.commit()
        else:
            # if user only logged in, add a login notification
            add_notification(
                current_user.id, " ورود با آی پی " + request.args.get("login")
            )
            # create a log
            app.logger.info("logged in user: %s" % current_user.username)
            # back to index
            return redirect(url_for("index"))
    # if user's logged in, and not go to here from login/register page
    if current_user.is_authenticated:
        # n is the number of notifications
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())

        # followers is the current user Followers
        followeds = Follow.query.filter_by(follower=current_user.id).all()

        users = []
        posts = []
        # get all follower posts
        for follow_item in followeds:
            users.append(User.query.get(follow_item.followed))
            posts += Post.query.filter_by(
                writer=User.query.get(follow_item.followed)
            ).all()
        # add follower posts to the post list
        posts += Post.query.filter_by(writer=current_user).all()

        # unique the post list
        posts = list(set(posts))
        # sort as the date
        posts.sort(key=lambda x: x.date, reverse=True)
        return render_template(
            "index.html",
            fAge=format_age,
            users=users,
            posts=posts[:50],
            posts_length=len(posts),
            current_user=current_user,
            not_list=n,
            Like=Like,
            pagination=1
        )
    else:
        # if not logged in, display login page
        # create a log
        app.logger.info("login page showed")
        return render_template("login.html")

@app.route("/page/<num_>")
@login_required
def posts_pagination(num_: int):
    num = int(num_)
    # n is the number of notifications
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # followers is the current user Followers
    followeds = Follow.query.filter_by(follower=current_user.id).all()

    users = []
    posts = []
    # get all follower posts
    for follow_item in followeds:
        users.append(User.query.get(follow_item.followed))
        posts += Post.query.filter_by(
            writer=User.query.get(follow_item.followed)
        ).all()
    # add follower posts to the post list
    posts += Post.query.filter_by(writer=current_user).all()

    # unique the post list
    posts = list(set(posts))
    # sort as the date
    posts.sort(key=lambda x: x.date, reverse=True)
    return render_template(
        "index.html",
        fAge=format_age,
        users=users,
        posts=posts[num*50:num*50 + 50],
        posts_length=len(posts),
        current_user=current_user,
        not_list=n,
        Like=Like,
        pagination=num
    )


@app.route("/@<username>")
@login_required
def user(username):
    """this is a function for go to the user posts"""
    return redirect(f"/@{username}/posts")


@app.route("/post/<id>")
@login_required
def post(id):
    p = Post.query.get_or_404(int(id))
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    content = p.id
    
    
    comments = sorted(p.comments, key=lambda x: x.date, reverse=True)

    return render_template('post.html', comments=comments, current_user=current_user, post=p, not_list=n, content=content, fAge=format_age, Like=Like)



@app.route("/@<username>/posts")
@login_required
def user_posts(username):
    """this is a function for display user posts"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # get user
    user = User.query.filter_by(username=username.lower()).first()
    if not user:
        return abort(404)

    # get posts
    posts = []
    posts += Post.query.filter_by(writer=user).all()

    # if user followed
    if Follow.query.filter_by(follower=current_user.id, followed=user.id).first():
        follow = True
    else:
        follow = False

    # create a log
    app.logger.info("user showed")
    posts = sorted(posts, key=lambda x: x.date, reverse=True)
    return render_template(
        "profile.html",
        user=user,
        follow=follow,
        Follow=Follow,
        follows=len(Follow.query.filter_by(followed=user.id).all()),
        not_list=n,
        posts=posts,
        fAge=format_age,
        Like=Like,
    )


@app.route("/@<username>/comments")
@login_required
def user_comments(username):
    """this is a function for display user comments"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # get user
    user = User.query.filter_by(username=username.lower()).first()
    if not user:
        return abort(404)

    # get comments
    comments = []
    comments += Comment.query.filter_by(user=user).all()

    # if user followed
    if Follow.query.filter_by(follower=current_user.id, followed=user.id).first():
        follow = True
    else:
        follow = False

    # create a log
    app.logger.info("user showed")
    comments = sorted(comments, key=lambda x: x.date, reverse=True)
    return render_template(
        "profile_cmt.html",
        user=user,
        follow=follow,
        Follow=Follow,
        follows=len(Follow.query.filter_by(followed=user.id).all()),
        not_list=n,
        comments=comments,
        Post=Post,
        fAge=format_age,
        Like=Like,
    )


@app.route("/me", methods=["GET", "POST"])
@login_required
def me():
    """this is a function for display profile settings page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # create a log
    app.logger.info("settings page")
    return render_template("me.html", current_user=current_user, not_list=n)


@app.route("/search", methods=["GET"])
@login_required
def search():
    """this is a function for display search page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    hashtags = HashTag.query.all()

    # Extract the text of each hashtag and count occurrences
    hashtag_texts = [hashtag.text for hashtag in hashtags]
    hashtag_counter = Counter(hashtag_texts)

    # Convert the Counter to a list of tuples and sort by count in descending order
    sorted_hashtags = sorted(hashtag_counter.items(), key=lambda x: x[1], reverse=True)

    # Display the sorted hashtags
    hashtags = [text for text, count in sorted_hashtags]

    # if not a search value
    if not request.args.get("q"):
        # create a log
        app.logger.info("search showed")

        return render_template(
            "search.html",
            hashtags=hashtags,
            current_user=current_user,
            not_list=n,
            search=False,
            search_value="",
        )
    else:
        result = set()
        list_result = list()

        # search in all posts
        for post in Post.query.all():
            # search_score in app/functions
            score = (
                search_score(
                    eval(post.tags), post.content, request.args.get("q")
                )
                * 10
            )
            if score > 2:
                list_result.append([post, score])

        # sort results
        list_result.sort(key=lambda x: x[1], reverse=True)
        list_result = list_result[:50]

        for post in list_result:
            result.add(post[0])

        # create a log
        app.logger.info("searching")

        if len(request.args.get("q")) < 3:
            result = []

        return render_template(
            "search.html",
            hashtags=hashtags,
            current_user=current_user,
            not_list=n,
            search=True,
            result=list(result),
            fAge=format_age,
            Like=Like,
            search_value=request.args.get("q"),
        )


@app.route("/login")
def login():
    """this is a function for display login page"""
    return redirect(url_for("index"))


@app.route("/2FA", methods=['POST'])
def login_with_2FA():
    """this is a function for display 2FA login page"""

    username = request.form.get('username')
    password = request.form.get('password')

    print(username)
    print(password)

    return render_template('2FA.html', username=username, password=password)


@app.route("/recovery")
def recovery():
    """this is a function to display recovery acount page"""
    if not current_user.is_authenticated:
        return render_template("recovery.html")
    else:
        return redirect(url_for("index"))

@app.route("/chpassword", methods=["POST"])
@login_required
def change_password():
    """this is a function to display recovery acount page"""
    password = request.form.get('password')

    code = generate_code(6, only_numbers=True)

    while Code.query.filter_by(code=code).first():
        code = generate_code(6, only_numbers=True)

    c = Code(phone=current_user.phone, code=code)
    db.session.add(c)
    db.session.commit()
    
    SMS(current_user.phone, code)

    return render_template("chpassword.html", password=password)

@app.route("/phone_recovery")
def phone_recovery():
    """this is a function to display recovery acount page"""
    if not current_user.is_authenticated:
        return render_template("phone_recovering.html")
    else:
        return redirect(url_for("index"))


@app.route("/register")
def register():
    """this is a function for display register page"""
    if current_user.is_authenticated:
        # create a log
        app.logger.info("register with logged in user")
        return redirect(url_for("index"))
    else:
        # create a log
        app.logger.warning("register page showed!")
        return render_template("register.html")


@app.route("/chat")
@login_required
def chat():
    """this is a function for display chat page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    

    # get all messages
    messages = list(Message.query.filter_by(writer=current_user).all())
    data = []

    for message in messages:
        user = User.query.get(message.to_id)
        last = sorted(list(Message.query.filter_by(writer=current_user, to_id=user.id).all()) + list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date)
        last = last[-1]
        
        sa = sorted(list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date, reverse=True)
        if sa:
            sa = sa[0].sa
        else:
            sa = False

        _is = False
        for data_ in data:
            if data_['username'] == user.username:
                _is = True
                break

        if not _is:
            data.append({'username': user.username, 'avatar': user.avatar, 'name': user.name, 'last': last, 'sa': sa, 'in': False})
    
    messages = list(Message.query.filter_by(to_id=current_user.id).all())

    for message in messages:
        user = message.writer
        last = sorted(list(Message.query.filter_by(writer=current_user, to_id=user.id).all()) + list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date)
        last = last[-1]
        
        sa = sorted(list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date, reverse=True)
        if sa:
            sa = sa[0].sa
        else:
            sa = False
        
        _is = False
        for data_ in data:
            if data_['username'] == user.username:
                _is = True
                break

        if not _is:
            data.append({'username': user.username, 'avatar': user.avatar, 'name': user.name, 'last': last, 'sa': sa, 'in': False})

    return render_template(
        "chatroom.html", current_user=current_user, not_list=n, mess_data=data, in_chat=False
    )

@app.route("/chat/<username>")
@login_required
def chat_with(username):
    """this is a function for display chat page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    this_user = User.query.filter_by(username=username).first()

    # change seen state
    for message in Message.query.filter_by(writer=this_user, to_id=current_user.id, sa=False).all():
        message.sa = True

    if not this_user:
        return abort(404)


    db.session.commit()

    # get all messages
        # get all messages
    messages = list(Message.query.filter_by(writer=current_user).all())
    data = []

    for message in messages:
        user = User.query.get(message.to_id)
        last = sorted(list(Message.query.filter_by(writer=current_user, to_id=user.id).all()) + list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date)
        last = last[-1]

        sa = sorted(list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date, reverse=True)
        if sa:
            sa = sa[0].sa
        else:
            sa = False

        _is = False
        for data_ in data:
            if data_['username'] == user.username:
                _is = True
                break

        if not _is:
            data.append({'username': user.username, 'avatar': user.avatar, 'name': user.name, 'last': last, 'sa': sa, 'in': False})
    
    messages = list(Message.query.filter_by(to_id=current_user.id).all())

    for message in messages:
        user = message.writer
        last = sorted(list(Message.query.filter_by(writer=current_user, to_id=user.id).all()) + list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date)
        last = last[-1]

        sa = sorted(list(Message.query.filter_by(writer=user, to_id=current_user.id).all()), key=lambda x: x.date, reverse=True)
        if sa:
            sa = sa[0].sa
        else:
            sa = False
        
        _is = False
        for data_ in data:
            if data_['username'] == user.username:
                _is = True
                break

        if not _is:
            data.append({'username': user.username, 'avatar': user.avatar, 'name': user.name, 'last': last, 'sa': sa, 'in': False})


    _is = False
    for data_ in data:
        if data_['username'] == this_user.username:
            data_['in'] = True
            _is = True
            break
    
    if not _is:
        data.append({'username': this_user.username, 'avatar': this_user.avatar, 'name': this_user.name, 'last': '', 'sa': True, 'in': True})

    messages = sorted(list(Message.query.filter_by(writer=current_user, to_id=this_user.id).all() + Message.query.filter_by(writer=this_user, to_id=current_user.id).all()), key=lambda x: x.date)

    return render_template(
        "chatroom.html", messages=messages, current_user=current_user, not_list=n, mess_data=data,
        in_chat=True, user=this_user
    )


@app.route("/logout")
@login_required
def logout():
    """this function to logout"""
    logout_user()

    # create a log
    app.logger.info("user logged out")
    return redirect(url_for("index"))


@app.route("/add")
@login_required
# @limiter.limit("5 per minute")
def newpost():
    """this is a function for display add new post page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    return render_template("add.html", current_user=current_user, not_list=n)


@app.route("/chatContent")
@login_required
def chatContent():
    """this function for display all messages for reload the chat page"""
    referer = request.headers.get("Referer")
    referer = re.sub('%2F', r'\/', referer)
    
    username = referer.split('/')[-1]
    user = User.query.filter_by(username=username).first()

    if user:
        # change seen state
        for message in Message.query.filter_by(writer=user, to_id=current_user.id, sa=False).all():
            message.sa = True

        db.session.commit()

        classMessages = Message.query.filter_by(writer=current_user, to_id=user.id).all()
        if user != current_user:
            classMessages += Message.query.filter_by(writer=user, to_id=current_user.id).all()
        messages = []

        for i in classMessages:
            message = {
                "content": i.content,
                "id": i.id,
                "type": "right" if i.writer.id == current_user.id else "left",
                "hour": i.hour,
                "date": i.date
            }
            messages.append(message)

        messages = sorted(list(messages), key=lambda x: x['date'])

        return jsonify({"all": messages})
    else:
        return ""


@app.route("/explore")
@login_required
def explore():
    """this function for display explore page
    in explore page, All users are displayed based on the similarity of their bio to the current user
    """
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    users = []
    if current_user.bio:
        _users = []

        # add users and similarity of their bio to the current user to the users list
        for user in User.query.all():
            _users.append(
                [user, float(text_similarity(current_user.bio, user.bio)) > 0.4]
            )

        # sort users
        _users = sorted(_users, key=lambda x: x[1], reverse=True)

        for user in _users:
            users.append(user[0])
        del _users
    else:
        users = User.query.all()

    return render_template(
        "explore.html",
        current_user=current_user,
        users=users,
        Follow=Follow,
        not_list=n,
        explore=True
    )

@app.route("/@<username>/followers")
@login_required
def followers(username):
    """this function for display a user followers page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    users = []
    user = User.query.filter_by(username=username).first()
    if not user:
        return abort(404)
    
    for follow in Follow.query.filter_by(followed=user.id):
        user_id = follow.follower
        users.append(User.query.get(user_id))

    return render_template(
        "explore.html",
        current_user=current_user,
        users=users,
        Follow=Follow,
        not_list=n,
        explore=False,
        title=" دنبال کنندگان " + username
    )

@app.route("/@<username>/followings")
@login_required
def followings(username):
    """this function for display a user followers page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    users = []
    user = User.query.filter_by(username=username).first()
    if not user:
        return abort(404)        
    
    for follow in Follow.query.filter_by(follower=user.id):
        user_id = follow.followed
        users.append(User.query.get(user_id))

    return render_template(
        "explore.html",
        current_user=current_user,
        users=users,
        Follow=Follow,
        not_list=n,
        explore=False,
        title="دنبال شوندگان" + username
    )

@app.route("/notifications")
@login_required
def messages():
    """this function for display all notifications"""
    notifications = Notification.query.filter_by(user=current_user).all()

    notifications.sort(key=lambda x: x.date, reverse=True)

    return render_template(
        "messages.html",
        current_user=current_user,
        notifications=notifications,
        fAge=format_age,
        not_list=0,
    )


@app.route("/recodes")
@login_required
def recodes():
    """this function to display recovery code keys page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    return render_template("recodes.html", not_list=n)

@app.route("/security")
@login_required
def security():
    """this function to display security page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    return render_template("security.html", not_list=n)


# APIs
# --------------------------------


@app.route("/api/addMessage", methods=["GET", "POST"])
@login_required
def addMessage():
    """this api for add a message from the chat page"""
    if request.method == "POST":
        data = request.form
        content = data.get("content")
        to_id = int(data.get("to_id"))
        # pin is a pin for add messages
        PIN = data.get("pin")

        print(content)

        # get referer for security
        referer = request.headers.get("Referer")
        if (
            content
            and referer
            and root_url in referer
            and encode_md5(PIN) == "ca1c05cca13ed2c33341d47ccd91ba07"
            and to_id
        ):
            sa = False
            if current_user == User.query.get(to_id):
                sa = True
            # add message
            mess = Message(writer=User.query.get(current_user.id), content=content, to_id=to_id, sa=sa)
            db.session.add(mess)
            db.session.commit()
            # create a log
            app.logger.info("a message added")
            return jsonify({"id": mess.id, "hour": str(mess.hour)})

    return abort(403)


@app.route("/api/delMessage", methods=["GET", "DELETE"])
@login_required
def delMessage():
    """this api for delete messages"""
    if request.method == "DELETE":
        data = request.form
        mess_id = data.get("id")
        PIN = data.get("pin")
        referer = request.headers.get("Referer")

        if (
            mess_id
            and referer
            and root_url in referer
            and encode_md5(PIN) == "ca1c05cca13ed2c33341d47ccd91ba07"
        ):
            # delete the message or abort 404
            mess = Message.query.get_or_404(mess_id)
            if mess.writer.id == current_user.id:
                db.session.delete(mess)
                db.session.commit()

                # create a log
                app.logger.info("a message deleted")
                return {"success": 1}

    return abort(403)


@app.route("/api/userValid", methods=["POST", "GET"])
# @limiter.limit("5 per minute")
def user_valid():
    """this function for check and login the users"""
    try:
        if request.method == "POST":
            data = request.form
            usr = data.get("username")
            pwd = data.get("password")
            code = data.get("code")
            # lower the username
            usr = usr.lower()

            referer = request.headers.get("Referer")

            # if to check the existence of the user
            if usr and not pwd:
                # if user is already exists
                if User.query.filter_by(username=usr).first():
                    # get avatar
                    avatar = User.query.filter_by(username=usr).first().avatar
                    # send: user is exists and send avatar
                    # create a log
                    app.logger.warning("username validation")
                    return jsonify(
                        {
                            "success": True,
                            "valid": True,
                            "message": "username is valid",
                            "avatar": avatar,
                        }
                    )

                else:
                    # create a log
                    app.logger.warning("username Validation")
                    return jsonify(
                        {
                            "success": True,
                            "valid": False,
                            "message": "username is not valid",
                        }
                    )
            # if to register the user
            elif pwd and usr:
                # getting user
                user = User.query.filter_by(username=usr).first()
                print(usr)
                if user:
                    if verify_password(pwd, user.password, user.salt):
                        # login user
                        if not current_user.is_authenticated:
                            if not user._2FA:
                                login_user(user)
                            elif code:
                                c = Code.query.filter_by(code=code).first()
                                if c:
                                    days = (datetime.now() - c.date).days
                                    seconds = (datetime.now() - c.date).seconds

                                    if days == 0 and seconds <= 1000:
                                        login_user(user)

                                        db.session.delete(c)
                                        db.session.commit()
                                        return jsonify(
                                                {
                                                    "success": True,
                                                    "valid": True,
                                                    "message": "code is valid",
                                                }
                                            )
                        elif "me" in referer:
                            pass
                        else:
                            return abort(400)
                        # create a log
                        app.logger.warning("password validation")
                        return jsonify(
                            {
                                "success": True,
                                "valid": True,
                                "message": "password is valid",
                            }
                        )

                    else:
                        # create a log
                        app.logger.warning("password validation")
                        return jsonify(
                            {
                                "success": True,
                                "valid": False,
                                "message": "password is not valid",
                            }
                        )
            else:
                return jsonify(
                    {"success": False, "valid": "?", "message": "args not found"}
                )
    except Exception as e:
        print("#" * 10)
        print(e)
        print("#" * 10)

    return abort(400)


@app.route("/api/add", methods=["POST", "GET"])
@login_required
# @limiter.limit("5 per minute")
def addPost():
    """this function for add a post"""
    if request.method == "POST":
        data = request.form
        # getting the image and content
        img = data.get("image")
        content = data.get("content")
        group = data.get("group")

        print(content)

        # getting the Referer
        referer = request.headers.get("Referer")
        if content and referer and root_url in referer:
            # change url(s) to "a" tag
            content = re.sub(
                r"(https:\/\/|www\.|http:\/\/)(.*)(\..*)(\s|$)",
                r'<a target="_blank" href="https://\2\3">\2\3 </a>',
                content,
            )

            # find content keywords
            try:
                tags = find_keywords(content)
            except:
                tags = []

            # hash tags
            hashtags = re.findall(r"#([\w|آ-ی]+)", content)

            for hashtag in hashtags:
                h = HashTag(text=hashtag)
                db.session.add(h)
            db.session.commit()

            content =  re.sub(r"#([\w|آ-ی]+)", r'<a href="/search?q=%23\1">#\1</a>', content)
            content =  re.sub(r'@(\w+)', r'<a href="@\1">\1@</a>', content)

            while '\n' in content:
                content = content.replace('\n', '<br />')

            if hashtags:
                tags += hashtags

            # unique the list
            tags = list(set(tags))
            _tags = []
            for tag in tags:
                if '<' not in tag and '>' not in tag and tag != 'br':
                    _tags.append(tag)

            tags = _tags.copy()

            # creating the post
            pos = Post(
                writer=User.query.get(current_user.id),
                img=img,
                content=content,
                tags=str(tags),
                group=group,
                description=content[:50],
            )
            # adding post
            db.session.add(pos)
            db.session.commit()

            # add 5 scores
            changeScore(5)

            # create a log
            app.logger.info("post adding")
            return jsonify({"success": True})

    return abort(403)


@app.route("/api/delete", methods=["GET", "DELETE"])
@login_required
def delPost():
    """this function for delete a post"""
    if request.method == "DELETE":
        data = request.form
        # getting id
        id = data.get("id")
        referer = request.headers.get("Referer")
        if id and referer and root_url in referer:
            # select the post
            pos = Post.query.get_or_404(id)
            # هf the author of the post was the current user
            if pos.writer.id == current_user.id:
                # delete post likes
                likes = Like.query.filter_by(liked=pos.id).all()
                for like in likes:
                    db.session.delete(like)
                
                # delete post comments
                comments = Comment.query.filter_by(post=pos).all()
                for comment in comments:
                    db.session.delete(comment)

                # delete the post
                db.session.delete(pos)

                # commit
                db.session.commit()

                # Subtract 5 Scores
                changeScore(-5)

                # create a log
                app.logger.warning("post deletion")
                return {"success": 1}
    return abort(403)


@app.route("/api/uploadavatar", methods=["POST"])
# @limiter.limit("5 per minute")
def upload():
    """this function for upload avatars"""
    if "file" in request.files:
        # get file
        file = request.files["file"]

        # if file is empty
        if file.filename == "":
            return jsonify({"success": False})

        # change file name
        filename = str(
            str(datetime.now()).replace(":", ".") + "." + file.filename.split(".")[-1]
        )

        # saving file to Avatar Folder
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], "avatars/" + filename))

        # if user logged in
        if current_user.is_authenticated:
            u = User.query.get(current_user.id)
            try:
                # remove the older user avatar
                os.remove(
                    os.path.join(
                        app.static_folder,
                        "pictures\\avatars\\" + u.avatar.split("/")[-1],
                    )
                    .replace("%20", " ")
                    .replace("%20", " ")
                )
            except Exception as e:
                print("#" * 10)
                print(e)
                print("#" * 10)

            # change the user avatar
            u.avatar = url_for("static", filename="pictures/avatars/" + filename)
            db.session.commit()
        # create a log
        app.logger.info("avatar uploading")
        return jsonify(
            {
                "success": True,
                "url": url_for("static", filename="pictures/avatars/" + filename),
            }
        )

    return jsonify({"success": False})


@app.route("/api/adduser", methods=["PUT"])
# @limiter.limit("1 per hours")
def addUser():
    """this api for adding users"""
    # try:
    if request.method == "PUT":
        # getting user data
        data = request.form
        usr = str(data.get("username"))
        pwd = str(data.get("password"))
        gender = str(data.get("gender"))
        city = str(data.get("city"))
        country = str(data.get("country"))
        avatar = str(data.get("avatar"))
        bio = str(data.get("bio"))
        phone = str(data.get("phone"))
        code = str(data.get("code"))
        name = str(data.get("name"))

        salt = salt_generator()

        if bio:
            bio = re.sub(r"\n", "<br />", data.get("bio"))
            bio = re.sub(r"\"", '\\"', bio)

        if bio:
            tags = "، ".join(find_keywords(bio))
        else:
            tags = ""
        usr = usr.lower()

        # if username is not exists
        if not User.query.filter_by(username=usr).first():
            c = Code.query.filter_by(code=code, phone=phone).first()
            if c:
                u = User(
                    name=name,
                    username=usr,
                    avatar=avatar,
                    password=sha256_hash(pwd, salt),
                    tags=tags,
                    gender=gender,
                    city=city,
                    salt=salt,
                    country=country,
                    bio=bio,
                    phone=phone
                )
                db.session.add(u)
                db.session.delete(c)

                check_u = User.query.filter_by(username=usr).first()

                f = Follow(follower=check_u.id, followed=1)
                db.session.add(f)
                db.session.commit()

                
                # create a log
                app.logger.warning("a user added")
                return jsonify({"success": True})
        return jsonify(
            {
                "success": True,
                "valid": False,
                "message": "username is valid",
            }
        )
    else:
        return jsonify({"success": False, "valid": "?", "message": "args not found"})
    # except Exception as e:
    #     print("#" * 10)
    #     print(e)
    #     print("#" * 10)
    #     return abort(500)

    return abort(400)


@app.route("/api/addfollow", methods=["PUT"])
def follow():
    """this API for adding a follower to the current user"""
    if "id" in request.form:
        # getting id
        id = request.form["id"]
        username = current_user.username

        # adding follow notification
        add_notification(
            id, f'<a href="/@{username}">{username}</a> شما را دنبال میکند'
        )
        f = Follow(follower=current_user.id, followed=id)
        db.session.add(f)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/delfollow", methods=["DELETE"])
def not_follow():
    """this API for unfollow a follower"""
    if "id" in request.form:
        id = int(request.form["id"])
        if id != 1:
            # delete follower
            f = Follow.query.filter_by(follower=current_user.id, followed=id).first()
            db.session.delete(f)
            db.session.commit()
            username = User.query.get(current_user.id).username
            # add unfollow notification
            add_notification(
                id, f'<a href="/@{username}">{username}</a> دیگر شما را دنبال نمیکند'
            )

            return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/edit", methods=["POST"])
# @limiter.limit("4 per minute")
@login_required
def edit():
    """this API for edit a user"""
    data = request.form
    usr = data.get("username")
    bio = data.get("bio")
    cnty = data.get("country")
    city = data.get("city")
    avtr = data.get("avatar")
    name = data.get("name")

    if bio:
        bio = re.sub(r"\n", "<br />", str(data.get("bio")))
        bio = re.sub(r"\"", '\\"', str(bio))

        tags = "، ".join(find_keywords(bio))
    else:
        tags = ""
    usr = data.get("username")

    # changing the username
    if usr:
        usr.lower()
        u = User.query.filter_by(username=current_user.username).first()
        u.username = usr

        db.session.commit()
        # create a log
        app.logger.info("username changing")
        return jsonify({"success": True})
    elif name:
        u = User.query.filter_by(username=current_user.username).first()
        u.name = name
        db.session.commit()
        
        # create a log
        app.logger.info("name changing")
        return jsonify({"success": True})

    elif bio:
        u = User.query.filter_by(username=current_user.username).first()
        u.bio = bio
        u.tags = tags

        db.session.commit()
        return jsonify({"success": True})
    elif cnty:
        current_user.country = cnty
        db.session.commit()

        return jsonify({"success": True, "message": "country changed"})
    elif city:
        current_user.city = city
        db.session.commit()

        return jsonify({"success": True, "message": "city changed"})
    elif avtr:
        current_user.avatar = avtr
        db.session.commit()

        return jsonify({"success": True, "message": "avatar changed"})

    return jsonify({"success": False})


@app.route("/api/seen")
def seen():
    """this API for change the status of all current user notifications to see"""
    seened_notification()

    return jsonify({"success": True})


@app.route("/api/image", methods=["POST"])
def upload_image():
    """this API to upload a new image"""
    if "file" in request.files:
        # get file
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False})
        filename = str(
            str(datetime.now()).replace(":", ".") + "." + file.filename.split(".")[-1]
        )
        # saving the file
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], "posts/" + filename))
        # create a log
        app.logger.info("image uploading")
        return jsonify(
            {
                "success": True,
                "url": url_for("static", filename="pictures/posts/" + filename),
            }
        )

    return jsonify({"success": False})


@app.route("/api/like", methods=["POST"])
@login_required
def like():
    """this API for liking a post"""
    try:
        data = request.form
        if data:
            if not Like.query.filter_by(
                liker=current_user.id, liked=data.get("postId")
            ).all():
                l = Like(liker=current_user.id, liked=data.get("postId"))
                db.session.add(l)
                db.session.commit()

                # create a log
                app.logger.info("a post liked")
                return jsonify({"success": True})
    except Exception as e:
        print("#" * 10)
        print(e)
        print("#" * 10)

    return abort(500)


@app.route("/api/recovery", methods=["post"])
# @limiter.limit("3 per minute")
def recovery_codes_api():
    """this API to create, delete and validation the keys"""
    id = request.form.get("id")
    name = request.form.get("name")
    code = request.form.get("code")
    # create
    if name:
        while True:
            # generate code
            g_code = generate_code(30)
            # if code is unique
            if not RecoveryCode.query.filter_by(code=sha256_hash(g_code, "")).first():
                break
        # create code
        rc = RecoveryCode(name=name, user=current_user, code=sha256_hash(g_code, ""))
        db.session.add(rc)
        db.session.commit()

        return jsonify({"success": True, "code": g_code, "id": rc.id})
    # delete
    elif id:
        # get object
        rc = RecoveryCode.query.get_or_404(id)
        if rc:
            # delete
            db.session.delete(rc)
            db.session.commit()

        return jsonify({"success": True})
    # validation
    elif code:
        # get key
        rc = RecoveryCode.query.filter_by(code=sha256_hash(code, "")).first()
        # if key
        if rc:
            # login
            login_user(rc.user)

            return jsonify({"success": True, "valid": True})
        else:
            return jsonify({"success": True, "valid": False})

        return jsonify({"success": True})

    return abort(400)


@app.route("/api/notifdelete", methods=["POST"])
@login_required
def delete_notification():
    """this API for delete a notification"""
    id = request.form.get("id")
    if request.method == "POST" and id:
        n = Notification.query.get(id)
        if n.user == current_user:
            db.session.delete(n)
            db.session.commit()

        return jsonify({"success": True})
    return abort(400)


@app.route("/api/unlike", methods=["POST"])
@login_required
def unlike():
    """this function for unlike a post"""
    try:
        data = request.form
        if data:
            # get the like
            l = Like.query.filter_by(
                liker=current_user.id, liked=data.get("postId")
            ).first()
            # delete the like
            db.session.delete(l)
            db.session.commit()

            return jsonify({"success": True})
    except Exception as e:
        print("#" * 10)
        print(e)
        print("#" * 10)

    return abort(500)


@app.route("/api/comment/add", methods=["POST"])
@login_required
def add_comment():
    data = request.form
    content = data.get('content')
    post = Post.query.get_or_404(int(data.get('id')))

    cm = Comment(post=post, content=content, user=current_user)
    db.session.add(cm)
    db.session.commit()

    return jsonify({"success": True})

@app.route("/api/comment/del", methods=["POST"])
@login_required
def delete_comment():
    data = request.form
    id = data.get('id')

    cm = Comment.query.get(id)
    if cm.user == current_user:
        db.session.delete(cm)
        db.session.commit()

        return jsonify({"success": True})
    else: 
        return abort(403)


@app.route('/api/register/phone', methods=['POST'])
# @limiter.limit("6 per hours")
def phone_validating():
    data = request.form
    phone = data.get('phone')
    code = data.get('code')

    if phone and not code:
        if User.query.filter_by(phone=phone).first():
            return jsonify({'success': True, 'valid': False})

        code = generate_code(6, only_numbers=True)

        while Code.query.filter_by(code=code).first():
            code = generate_code(6, only_numbers=True)

        c = Code(phone=phone, code=code)
        db.session.add(c)
        db.session.commit()
        
        sms_sended = SMS(phone, code)
        return jsonify({'success': True, 'valid': True})

    elif phone and code:
        c = Code.query.filter_by(phone=phone, code=code).first()

        if c:
            days = (datetime.now() - c.date).days
            seconds = (datetime.now() - c.date).seconds

            if days == 0 and seconds <= 1000:
                return jsonify({'success': True, 'valid': True}) 

        return jsonify({'success': True, 'valid': False})

    return abort(400)

@app.route("/api/recovery/phone", methods=["POST"])
# @limiter.limit("3 per minute")
def phone_recovery_codes_api():
    """this API to acount recovering with phone"""

    phone = request.form.get("phone")
    code = request.form.get("code")

    print('-'*20)
    print(phone)
    print('-'*20)
    print(code)
    print('-'*20)

    if phone and not code:
        if User.query.filter_by(phone=phone).first():
            code = generate_code(6, only_numbers=True)

            while Code.query.filter_by(code=code).first():
                code = generate_code(6, only_numbers=True)

            c = Code(phone=phone, code=code)
            db.session.add(c)
            db.session.commit()

            SMS(phone, code)

            return jsonify({'success': True, 'valid': True})
        return jsonify({'success': True, 'valid': False})

    elif phone and code:
        c = Code.query.filter_by(phone=phone, code=code).first()

        if c:
            days = (datetime.now() - c.date).days
            seconds = (datetime.now() - c.date).seconds

            if days == 0 and seconds <= 1000:
                u = User.query.filter_by(phone=phone).first()
                login_user(u)

                db.session.delete(c)
                db.session.commit()
                return jsonify({'success': True, 'valid': True})
        return jsonify({'success': True, 'valid': False})

    return abort(400)

@app.route('/api/chp', methods=['POST'])
# @limiter.limit("3 per hours")
def change_password_code_validation():
    code = request.form.get('code')
    pwd = request.form.get('password')

    if code:
        c = Code.query.filter_by(phone=current_user.phone, code=code).first()

        if c:
            days = (datetime.now() - c.date).days
            seconds = (datetime.now() - c.date).seconds

            if days == 0 and seconds <= 1000:
                # changing the password
                u = User.query.filter_by(username=current_user.username).first()
                u.password = sha256_hash(pwd, u.salt)

                db.session.commit()
                # create a log
                app.logger.warning("password changing")

                return jsonify({'success': True, 'valid': True})

        return jsonify({'success': True, 'valid': False})

    return abort(400)

@app.route('/api/2FA', methods=['POST'])
# @limiter.limit("3 per hours")
def _2FA_Factor_Auth():
    username = request.form.get('username').lower()
    user = User.query.filter_by(username=username).first()
    phone = user.phone

    if user and user._2FA:
            code = generate_code(6, only_numbers=True)

            while Code.query.filter_by(code=code).first():
                code = generate_code(6, only_numbers=True)

            c = Code(phone=phone, code=code)
            db.session.add(c)
            db.session.commit()

            SMS(phone, code)

            return jsonify({'_2FA': True})
    elif user:
        return jsonify({'_2FA': False})

    return abort(400)

@app.route('/api/2FA-state')
@login_required
def _2FA_State():
    try:
        current_user._2FA = not current_user._2FA
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})





@app.route('/api/dontSaMessage')
@login_required
def is_dont_sa_messages():
    message = Message.query.filter_by(to_id=current_user.id, sa=False).all()

    return jsonify({'if': bool(message)})







# ------ robots.txt file ------
@app.route('/robots.txt')
def robots_txt():
    return send_from_directory('static', 'robots.txt')