from app import app
from flask import render_template, abort, request
from app.models import User
from flask_login import login_user, login_required, current_user


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

        print(len(n))
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
                print(User.query.filter_by(username=usr).first())
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
