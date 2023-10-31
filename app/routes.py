import os
from app import app, db
import ast
from flask import render_template, abort, request, jsonify, redirect, url_for
from app.models import *
from flask_login import login_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.functions import *
import re
from datetime import datetime
from itertools import zip_longest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def text_similarity(text1, text2):
    vectorizer = TfidfVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    csim = cosine_similarity(vectors)
    return csim[0][1]


def format_age(date):
    now = datetime.now()
    print(now)
    print(date)
    ageY = now.year - date.year
    ageM = now.month - date.month
    ageD = now.day - date.day
    ageH = now.hour - date.hour
    ageMI = now.minute - date.minute

    if not ageY and not ageM and not ageD and not ageH and ageMI < 10:
        return "به تازگی"
    elif not ageY and not ageM and not ageD and not ageH:
        return f"{ageMI} دقیقه پیش"
    elif not ageY and not ageM and not ageD:
        return f"{ageH} ساعت پیش"
    elif not ageY and not ageM and ageD == 1:
        return "دیروز"
    elif not ageY and not ageM:
        return f"{ageD} روز پیش"
    elif not ageY and not ageM == 1 and ageD > 2:
        return "ماه قبل"
    elif not ageY:
        if ageD > 2:
            return f"{ageM} ماه و {ageD} روز پیش"
        else:
            return f"{ageM} ماه"
    else:
        return f"{ageY} سال پیش"


def add_notification(user_id, message):
    with app.app_context():
        u = User.query.get(user_id)

        print(u.not_seened_notis)

        my_list = ast.literal_eval(u.not_seened_notis)
        my_list.append(message)
        updated_notis = str(my_list)

        u.not_seened_notis = updated_notis
        db.session.commit()


def seened_notification():
    with app.app_context():
        u = User.query.get(current_user.id)
        NS = eval(u.not_seened_notis)
        S = eval(u.seened_notis)
        u.seened_notis = str(S + NS)

        u.not_seened_notis = "[]"

        db.session.commit()


def addScore(score):
    with app.app_context():
        u = User.query.get(current_user.id)

        u.gems = u.gems + score
        print(f"!!!!!!!!!{u.gems}")
        db.session.commit()


# !
root_url = "http://127.0.0.1:1223"
# !


@app.route("/")
def index():
    if current_user.is_authenticated:
        n = 0
        if current_user.not_seened_notis != '[]':
            n = len(current_user.not_seened_notis.replace("[", "").replace("]", "").split(","))

        falloweds = Fallow.query.filter_by(follower=current_user.id)

        users = []
        posts = []
        for fallow_item in falloweds:
            users.append(User.query.get(fallow_item.followed))
            posts += Post.query.filter_by(
                writer=User.query.get(fallow_item.followed)
                ).all()
        posts += Post.query.filter_by(writer=current_user).all()

        return render_template(
            "index.html",
            fAge=format_age,
            users=users,
            posts=posts,
            current_user=current_user,
            not_list=n,
        )
    else:
        return render_template("Login.html")


@app.route("/@<username>")
@login_required
def user(username):
    return redirect(f"/@{username}/posts")


@app.route("/@<username>/posts")
@login_required
def user_posts(username):
    n = 0
    if current_user.not_seened_notis != '[]':
        n = len(current_user.not_seened_notis.replace("[", "").replace("]", "").split(","))

    user = User.query.filter_by(username=username).first()
    if not user:
        return abort(404)

    if Fallow.query.filter_by(follower=current_user.id, followed=user.id).first():
        fallow = True
    else:
        fallow = False

    return render_template("profile.html", user=user, fallow=fallow, not_list=n)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    else:
        return render_template("register.html")


@app.route("/chat")
@login_required
def chat():
    n = 0
    if current_user.not_seened_notis != '[]':
        n = len(current_user.not_seened_notis.replace("[", "").replace("]", "").split(","))

    messages = Message.query.all()
    return render_template(
        "chatroom.html", messages=messages, current_user=current_user, not_list=n
    )


@app.route("/add")
@login_required
def newpost():
    n = 0
    if current_user.not_seened_notis != '[]':
        n = len(current_user.not_seened_notis.replace("[", "").replace("]", "").split(","))

    return render_template("add.html", current_user=current_user, not_list=n)


@app.route("/chatContent")
@login_required
def chatContent():
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
    n = 0
    if current_user.not_seened_notis != '[]':
        n = len(current_user.not_seened_notis.replace("[", "").replace("]", "").split(","))

    _users = []
    users = []

    for user in User.query.filter_by(gender=current_user.gender).all():
        print(float(text_similarity(current_user.bio, user.bio)))
        if float(text_similarity(current_user.bio, user.bio)) > 0.4:
            if user != current_user:
                _users.append([user, int(text_similarity(current_user.bio, user.bio))])

    _users = sorted(_users, key=lambda x: x[1])

    for user in _users:
        users.append(user[0])
    del _users

    return render_template(
        "explore.html", current_user=current_user, users=users, Fallow=Fallow, not_list=n
    )


@app.route("/messages")
@login_required
def messages():
    NSN = eval(current_user.not_seened_notis)
    NSN.reverse()
    SN = eval(current_user.seened_notis)
    SN.reverse()

    return render_template(
        "messages.html",
        current_user=current_user,
        NSN=NSN,
        SN=SN,
        not_list = 0
    )


# API
@app.route("/api")
def api() -> 403:
    return abort(403)


@app.route("/api/addMessage", methods=["GET", "POST"])
@login_required
def addMessage():
    if request.method == "POST":
        data = request.form
        content = data.get("content")
        PIN = data.get("pin")

        referer = request.headers.get("Referer")
        if (
            content
            and referer
            and root_url in referer
            and encode_md5(PIN) == "ca1c05cca13ed2c33341d47ccd91ba07"
        ):
            mess = Message(writer=User.query.get(current_user.id), content=content)
            db.session.add(mess)
            db.session.commit()
            return jsonify({"id": mess.id, "date": str(mess.date)})

    return abort(403)


@app.route("/api/delMessage", methods=["GET", "DELETE"])
@login_required
def delMessage():
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
            mess = Message.query.get_or_404(mess_id)
            if mess.writer.id == current_user.id:
                db.session.delete(mess)
                db.session.commit()
                return {"success": 1}

    return abort(403)


@app.route("/api/userValid", methods=["POST", "GET"])
def user_valid():
    try:
        if request.method == "POST":
            data = request.form
            usr = data.get("username")
            pwd = data.get("password")
            usr = usr.lower()

            if usr and not pwd:
                if User.query.filter_by(username=usr).first():
                    avatar = User.query.filter_by(username=usr).first().avatar
                    return jsonify(
                        {
                            "success": True,
                            "valid": True,
                            "message": "username is valid",
                            "avatar": avatar,
                        }
                    )

                else:
                    return jsonify(
                        {
                            "success": True,
                            "valid": False,
                            "message": "username is not valid",
                        }
                    )
            elif pwd and usr:
                user = User.query.filter_by(username=usr, password=pwd).first()
                if user:
                    login_user(user)
                    ip = 0
                    add_notification(user.id, f"وورد از دستگاه با آی پی {ip}")

                    return jsonify(
                        {"success": True, "valid": True, "message": "password is valid"}
                    )

                else:
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

    return abort(400)


@app.route("/api/add", methods=["POST", "GET"])
@login_required
def addPost():
    if request.method == "POST":
        data = request.form
        img = data.get("image")
        content = data.get("content")

        referer = request.headers.get("Referer")
        if (
            content
            and referer
            and root_url in referer
        ):
            content = re.sub(r'(https://.*\s)', r'<a target="_blank" href="\1">\1</a>', content)
            content = re.sub(r'(www\..*\s)', r'<a target="_blank" href="\1">\1</a>', content)
            print(content)
            pos = Post(writer=User.query.get(current_user.id), img=img, content=content)
            db.session.add(pos)
            db.session.commit()
            addScore(5)
            return jsonify({"success": True})

    return abort(403)


@app.route("/api/delete", methods=["GET", "DELETE"])
@login_required
def delPost():
    if request.method == "DELETE":
        data = request.form
        id = data.get("id")
        referer = request.headers.get("Referer")
        if (
            id
            and referer
            and root_url in referer
        ):
            pos = Post.query.get_or_404(id)
            if pos.writer.id == current_user.id:
                db.session.delete(pos)
                db.session.commit()
                addScore(-5)
                return {"success": 1}
    return abort(403)


@app.route("/api/uploadavatar", methods=["POST"])
def upload():
    if "file" in request.files:
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False})
        filename = str(
            str(datetime.now()).replace(":", ".") + "." + file.filename.split(".")[-1]
        )
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], "avatars/" + filename))
        if current_user.is_authenticated:
            u = User.query.get(current_user.id)
            try:
                os.remove(
                    os.path.join(
                        app.static_folder,
                        "pictures\\avatars\\" + u.avatar.split("/")[-1],
                    )
                    .replace("%20", " ")
                    .replace("%20", " ")
                )
            except Exception as e:
                print(e)
            u.avatar = url_for("static", filename="pictures/avatars/" + filename)
            db.session.commit()
        return jsonify(
            {
                "success": True,
                "url": url_for("static", filename="pictures/avatars/" + filename),
            }
        )

    return jsonify({"success": False})


@app.route("/api/adduser", methods=["PUT"])
def addUser():
    try:
        if request.method == "PUT":
            data = request.form
            usr = data.get("username")
            pwd = data.get("password")
            gender = data.get("gender")
            city = data.get("city")
            bio = data.get("bio")
            country = data.get("country")
            avatar = data.get("avatar")
            usr = usr.lower()

            if not User.query.filter_by(username=usr).first():
                u = User(
                    username=usr,
                    avatar=avatar,
                    password=pwd,
                    gender=gender,
                    city=city,
                    country=country,
                    bio=bio,
                )
                db.session.add(u)
                db.session.commit()
                return jsonify(
                    {
                        "success": True,
                        "valid": True,
                    }
                )

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

    return abort(400)


@app.route("/api/addfallow", methods=["PUT"])
def fallow():
    if "id" in request.form:
        id = request.form["id"]
        username = User.query.get(current_user.id).username
        add_notification(
            id, f"<a href=\"/@{username}\">{username}</a> شما را دنبال میکند"
        )
        f = Fallow(follower=current_user.id, followed=id)
        db.session.add(f)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/delfallow", methods=["DELETE"])
def not_fallow():
    if "id" in request.form:
        id = request.form["id"]
        f = Fallow.query.filter_by(follower=current_user.id, followed=id).first()
        db.session.delete(f)
        db.session.commit()
        username = User.query.get(current_user.id).username
        add_notification(
            id, f"<a href=\"/@{username}\">{username}</a> دیگر شما را دنبال نمیکند"
        )

        return jsonify({"success": True})
    return jsonify({"success": False})


@app.route("/api/edit", methods=["POST"])
def edit():
    data = request.form
    usr = data.get("username")
    pwd = data.get("password")

    if usr:
        u = User.query.filter_by(username=current_user.username).first()
        u.username = usr

        db.session.commit()
        return jsonify({"success": True})
    elif pwd:
        u = User.query.filter_by(username=current_user.username).first()
        u.password = pwd

        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"success": False})


@app.route("/api/seen")
def seen():
    seened_notification()

    return jsonify({"success": True})


@app.route("/api/image", methods=["POST"])
def upload_image():
    if "file" in request.files:
        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False})
        filename = str(
            str(datetime.now()).replace(":", ".") + "." + file.filename.split(".")[-1]
        )
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], "posts/" + filename))
        return jsonify(
            {
                "success": True,
                "url": url_for("static", filename="pictures/posts/" + filename),
            }
        )

    return jsonify({"success": False})

