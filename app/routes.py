from app import app, db
from flask import render_template, abort, request, jsonify
from app.models import User, Message
from flask_login import login_user, login_required, current_user
from app.functions import *


# !
root_url = "http://127.0.0.1:1223"
# !


@app.route("/")
def index():
    if current_user.is_authenticated:
        if (
            len(current_user.notifictions.replace("[", "").replace("]", "").split(","))
            - 1
        ):
            n = current_user.notifictions.replace("[", "").replace("]", "").split(",")
        else:
            n = []

        return render_template("index.html", current_user=current_user, not_list=len(n))
    else:
        return render_template("Login.html")


@app.route("/login")
def login():
    return render_template("login.html")


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
                    return (
                        '{"success":true, "valid": true, "message": "username is valid", "avatar": "%s"}'
                        % avatar
                    )

                else:
                    return '{"success":true, "valid": false, "message": "username is not valid"}'
            elif pwd and usr:
                if User.query.filter_by(username=usr, password=pwd).first():
                    login_user(User.query.filter_by(username=usr, password=pwd).first())
                    return '{"success":true, "valid": true, "message": "password is valid"}'

                else:
                    return '{"success":true, "valid": false, "message": "password is not valid"}'
            else:
                return '{"success":false, "valid": "?", "message": "args not found"}'
    except Exception as e:
        print("#" * 10)
        print(e)
        print("#" * 10)
        return '{"success":false, "valid": "?", "message": "?"}'

    return abort(400)


@app.route("/chat")
@login_required
def chat():
    messages = Message.query.all()
    return render_template(
        "chatroom.html", messages=messages, current_user=current_user
    )


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
            "username": i.writer.username if i.writer.id != current_user.id else None
        }
        messages.append(message)

    return jsonify({"all": messages})


# API
@app.route("/api")
def api() -> 403:
    return abort(403)


@app.route("/api/addMessage", methods=["GET", "POST"])
def addMessage():
    if request.method == "POST":
        data = request.form
        usr_id = data.get("user_id")
        content = data.get("content")
        PIN = data.get("pin")

        referer = request.headers.get("Referer")
        if (
            content
            and usr_id
            and referer
            and root_url in referer
            and encode_md5(PIN) == "ca1c05cca13ed2c33341d47ccd91ba07"
        ):
            mess = Message(writer=User.query.get(usr_id), content=content)
            db.session.add(mess)
            db.session.commit()
            return {"id": mess.id}

    return abort(403)


@app.route("/api/delMessage", methods=["GET", "DELETE"])
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
