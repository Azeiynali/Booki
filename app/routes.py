import os
from app import app, db, limiter
import ast
from flask import render_template, abort, request, jsonify, redirect, url_for
from app.models import *
from flask_login import login_user, login_required, current_user, logout_user
from app.functions import *
import re
from datetime import datetime
from itertools import zip_longest

# library imports


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
    if current_user.is_authenticated:
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    else:
        n = 0

    return render_template('errors/404.html', current_user=current_user, not_list=n), 404

@app.errorhandler(500)
def page_not_found(error):
    if current_user.is_authenticated:
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    else:
        n = 0

    return render_template('errors/500.html', current_user=current_user, not_list=n), 500

@app.errorhandler(403)
def page_not_found(error):
    if current_user.is_authenticated:
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())
    else:
        n = 0

    return render_template('errors/403.html', current_user=current_user, not_list=n), 403

#


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
            app.logger.info('logged in user: %s' % current_user.username)
            # back to index
            return redirect(url_for("index"))
    # if user's logged in, and not go to here from login/register page
    if current_user.is_authenticated:
        # n is the number of notifications
        n = len(Notification.query.filter_by(user=current_user, seened=False).all())

        # falloweds is the current user Followers
        falloweds = Fallow.query.filter_by(follower=current_user.id)

        users = []
        posts = []
        # get all follower posts
        for fallow_item in falloweds:
            users.append(User.query.get(fallow_item.followed))
            posts += Post.query.filter_by(
                writer=User.query.get(fallow_item.followed)
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
            posts=posts,
            current_user=current_user,
            not_list=n,
            Like=Like,
            first=RegisteredNow,
        )
    else:
        # if not logged in, display login page
        # create a log
        app.logger.info("login page showed")
        return render_template("login.html")


@app.route("/@<username>")
@login_required
def user(username):
    """this is a function for go to the user posts"""
    return redirect(f"/@{username}/posts")


@app.route("/@<username>/posts")
@login_required
def user_posts(username):
    """this is a function for display user posts"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # get user
    user = User.query.filter_by(username=username).first()
    if not user:
        return abort(404)

    # get posts
    posts = []
    posts += Post.query.filter_by(writer=user).all()

    # if user followed
    if Fallow.query.filter_by(follower=current_user.id, followed=user.id).first():
        fallow = True
    else:
        fallow = False

    # create a log
    app.logger.info("user showed")
    return render_template(
        "profile.html",
        user=user,
        fallow=fallow,
        fallows=len(Fallow.query.filter_by(followed=user.id).all()),
        not_list=n,
        posts=posts,
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


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """this is a function for display search page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # if not a search value
    if not request.form.get("search_value"):
        # create a log
        app.logger.info("search showed")
        return render_template(
            "search.html",
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
            score = search_score(post.tags, post.content, request.form.get("search_value")) * 10
            if score > 2:
                list_result.append([post, score])

        # sort results
        list_result.sort(key=lambda x: x[1], reverse=True)
        list_result = list_result[:50]

        for post in list_result:
            result.add(post[0])

        # create a log
        app.logger.info("searching")
        return render_template(
            "search.html",
            current_user=current_user,
            not_list=n,
            search=True,
            result=list(result),
            fAge=format_age,
            Like=Like,
            search_value=request.form.get("search_value"),
        )


@app.route("/login")
# @limiter.limit("5 per minute")
def login():
    """this is a function for display login page"""
    return redirect(url_for("index"))


@app.route("/register")
# @limiter.limit("5 per minute")
def register():
    """this is a function for display register page"""
    if current_user.is_authenticated:
        # create a log
        app.logger.info("register with logged in user")
        return redirect(url_for("index"))
    else:
        # create a log
        app.logger.warning("user showed")
        return render_template("register.html")


@app.route("/chat")
@login_required
def chat():
    """this is a function for display chat page"""
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    # get all messages
    messages = Message.query.all()
    return render_template(
        "chatroom.html", messages=messages, current_user=current_user, not_list=n
    )


@app.route("/logout")
@login_required
def logout():
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
# @limiter.limit("5 per minute")
def chatContent():
    """this function for display all messages for reload the chat page"""
    classMessages = Message.query.all()
    messages = []

    for i in classMessages:
        message = {
            "content": i.content,
            "id": i.id,
            "type": "right" if i.writer.id == current_user.id else "left",
            "avatar": i.writer.avatar if i.writer.id != current_user.id else None,
            "username": i.writer.username if i.writer.id != current_user.id else None,
        }
        messages.append(message)

    return jsonify({"all": messages})


@app.route("/explore")
@login_required
def explore():
    """this function for display explore page
    in explore page, All users are displayed based on the similarity of their bio to the current user
    """
    n = len(Notification.query.filter_by(user=current_user, seened=False).all())

    _users = []
    users = []

    # add users and similarity of their bio to the current user to the users list
    for user in User.query.all():
        _users.append([user, float(text_similarity(current_user.bio, user.bio)) > 0.4])

    # sort users
    _users = sorted(_users, key=lambda x: x[1], reverse=True)

    for user in _users:
        users.append(user[0])
    del _users

    return render_template(
        "explore.html",
        current_user=current_user,
        users=users,
        Fallow=Fallow,
        not_list=n,
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


# APIs
# --------------------------------


@app.route("/api/addMessage", methods=["GET", "POST"])
@login_required
def addMessage():
    """this api for add a message from the chat page"""
    if request.method == "POST":
        data = request.form
        content = data.get("content")
        # pin is a pin for add messages
        PIN = data.get("pin")

        # get referer for security
        referer = request.headers.get("Referer")
        if (
            content
            and referer
            and root_url in referer
            and encode_md5(PIN) == "ca1c05cca13ed2c33341d47ccd91ba07"
        ):
            # add message
            mess = Message(writer=User.query.get(current_user.id), content=content)
            db.session.add(mess)
            db.session.commit()
            # create a log
            app.logger.info("a message added")
            return jsonify({"id": mess.id, "date": str(mess.date)})

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
            # lower the username
            usr = usr.lower()

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
                user = User.query.filter_by(username=usr, password=pwd).first()
                if user:
                    # login user
                    login_user(user)

                    # create a log
                    app.logger.warning("password validation")
                    return jsonify(
                        {"success": True, "valid": True, "message": "password is valid"}
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
        return jsonify({"success": False, "valid": "?", "message": "?"})

        return abort(404)


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

        # getting the Referer
        referer = request.headers.get("Referer")
        if content and referer and root_url in referer:
            # TODO: add $ in the regex
            # change url(s) to "a" tag
            content = re.sub(
                r"([www\.|https:\/\/].*\..*?)([\s|\.|،|\,|$])",
                r'<a target="_blank" href="https:\/\/\1">\1</a>\2',
                content,
            )

            # find content keywords
            tags = find_keywords(content)

            hashtags = re.findall(r"#([\w|آ-ی]*)", content)
            if hashtags:
                tags += hashtags

            # creating the post
            pos = Post(
                writer=User.query.get(current_user.id),
                img=img,
                content=content,
                tags=tags,
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
                # delete the post
                db.session.delete(pos)
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
# @limiter.limit("2 per minute")
def addUser():
    # this api for adding users
    try:
        if request.method == "PUT":
            # getting user data
            data = request.form
            usr = data.get("username")
            pwd = data.get("password")
            gender = data.get("gender")
            city = data.get("city")
            country = data.get("country")
            email = data.get("country")
            avatar = data.get("avatar")

            bio = re.sub(r"\n", "<br />", data.get("bio"))
            bio = re.sub(r"\"", "\\\"", bio)

            tags =  '، '.join(find_keywords(bio))
            usr = usr.lower()

            # if username is not exists
            if not User.query.filter_by(username=usr).first():
                u = User(
                    username=usr,
                    avatar=avatar,
                    password=pwd,
                    tags=tags,
                    gender=gender,
                    city=city,
                    country=country,
                    bio=bio,
                )
                db.session.add(u)
                db.session.commit()

                f = Fallow(follower=u.id, followed=1)
                db.session.add(f)
                db.session.commit()
                # create a log
                app.logger.warning("a user added")
                return jsonify({"success": True})
            else:
                return jsonify(
                    {
                        "success": True,
                        "valid": False,
                        "message": "username is valid",
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
        return jsonify({"success": False, "valid": "?", "message": "?"})

    return abort(404)


@app.route("/api/addfallow", methods=["PUT"])
def fallow():
    """this API for adding a follower to the current user"""
    if "id" in request.form:
        # getting id
        id = request.form["id"]
        username = User.query.get(current_user.id).username

        # adding fallow notification
        add_notification(
            id, f'<a href="/@{username}">{username}</a> شما را دنبال میکند'
        )
        f = Fallow(follower=current_user.id, followed=id)
        db.session.add(f)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/delfallow", methods=["DELETE"])
def not_fallow():
    """this API for unfollow a follower"""
    if "id" in request.form:
        id = request.form["id"]
        # delete follower
        f = Fallow.query.filter_by(follower=current_user.id, followed=id).first()
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
def edit():
    """this API for edit a user"""
    data = request.form
    usr = data.get("username")
    bio = data.get("bio")
    pwd = data.get("password")

    bio = re.sub(r"\n", "<br />", data.get("bio"))
    bio = re.sub(r"\"", "\\\"", bio)
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
    # changing the password
    elif pwd:
        u = User.query.filter_by(username=current_user.username).first()
        u.password = pwd

        db.session.commit()
        # create a log
        app.logger.warning("password changing")
        return jsonify({"success": True})
    elif bio:
        u = User.query.filter_by(username=current_user.username).first()
        u.bio = bio

        db.session.commit()
        return jsonify({"success": True})

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

    return jsonify({"success": False})


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
    return abort(404)


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

    return jsonify({"success": False})
