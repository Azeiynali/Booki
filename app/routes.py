from app import app, db
from flask import render_template, abort, request, jsonify, redirect, url_for
from app.models import *
from flask_login import login_user, login_required, current_user
from app.functions import *
import re
from itertools import zip_longest


def format_age(date):
    now = datetime.now()
    ageY = now.year - date.year
    ageM = now.month - date.month
    ageD = now.day - date.day
    ageH = now.hour - date.hour

    if not ageY and not ageM and not ageD and ageH < 1:
        return "به تازگی"
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

def addScore(score):
    with app.app_context():
        u = User.query.get(current_user.id)


        u.coins = u.coins + score
        print(f"$$######{u.coins}")
        db.session.commit()

# !
root_url = "http://127.0.0.1:1223"
# !


@app.route("/")
def index():
    if current_user.is_authenticated:
        if (
            len(current_user.notifications.replace("[", "").replace("]", "").split(","))
            - 1
        ):
            n = current_user.notifications.replace("[", "").replace("]", "").split(",")
        else:
            n = []

        posts = Post.query.all()
        users = User.query.all()

        return render_template(
            "index.html",
            fAge=format_age,
            users=users,
            posts=posts,
            current_user=current_user,
            not_list=len(n),
        )
    else:
        return render_template("Login.html")


@app.route("/")
def register():
    if current_user.is_authenticated:
      return redirect(url_for("index"))
    else:
        return render_template("register.html")


@app.route("/@<username>")
@login_required
def user(username):

    return redirect(f"/@{username}/posts")

@app.route("/@<username>/posts")
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return abort(404)

    return render_template("profile.html", user=user, fallows=Fallow)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/chat")
@login_required
def chat():
    messages = Message.query.all()
    return render_template(
        "chatroom.html", messages=messages, current_user=current_user
    )


@app.route("/new/post")
@login_required
def newpost():
    messages = Message.query.all()
    return render_template("newpost.html", current_user=current_user)


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
                if User.query.filter_by(username=usr, password=pwd).first():
                    login_user(User.query.filter_by(username=usr, password=pwd).first())
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


@app.route("/api/addPost", methods=["POST", "GET"])
def addPost():
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
            content = re.sub('"', '\\"', content)
            content = re.sub('<a .*href="\\"\/(.*)\\"">.*<\/a>', "\1", content)
            content = re.sub('<a .*href=\\"\/(.*)\\">.*<\/a>', "\1", content)
            print(content)
            pos = Post(writer=User.query.get(current_user.id), content=content)
            db.session.add(pos)
            db.session.commit()
            addScore(5)
            return jsonify({"succcess": True})

    return abort(403)


@app.route("/api/delPost", methods=["GET", "DELETE"])
@login_required
def delPost():
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
            pos = Post.query.get_or_404(mess_id)
            if pos.writer.id == current_user.id:
                db.session.delete(pos)
                db.session.commit()
                addScore(-5)
                return {"success": 1}
    return abort(403)

