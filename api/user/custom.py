import logging
from datetime import datetime
from connexion import NoContent
from passlib.hash import pbkdf2_sha256
from flask import session, request, current_app
from db import User, utils, Submission
import smtplib
from email import message
from itsdangerous import TimestampSigner, URLSafeTimedSerializer

ts = URLSafeTimedSerializer("SUPES_SECRET87").signer("SUPES_SECRET87")
from pony.flask import db_session



@db_session
def validate(key):
    return utils.get_user(request, db_session).to_dict(exclude='pwd')

@db_session
def login(body):
    logging.info(request)
    q = None
    user = body
    # print(body)
    if 'email' in user:
        q = User.get(email=user['email'])
        logging.info(q)
    elif 'username' in user:
        q = User.get(username=user['username'])
    else:
        return {'msg': 'Incorrect keys provided'}, 500
    if q:
        if pbkdf2_sha256.verify(user["pwd"], q.pwd):
            return q.to_dict(exclude='pwd'), 200
        else:
            abort(401)
    else:
        return {'msg': 'User not found'}, 404


def logout():
    session["user"] = None
    del session["user"]
    return 200

@db_session
def auth(body):
    user = body
    # TODO create oauth token here and add to table. Just send api key for now
    q = db_session.query(User).filter(User.email == user["email"]).one_or_none()
    if q:
        if pbkdf2_sha256.verify(user["pwd"], q.pwd):
            session["user"] = q.dump()
            return q.dump(), 200
        else:
            return NoContent, 401
    else:
        return NoContent, 404

@db_session
def reset(email):
    conf = current_app.config
    user = utils.get_user(request, db_session)
    # TODO handle domain
    if user:
        tk = ts.sign(user.id)
        reset = "{}/reset/{}".format("https://citizenscience.ch", tk.decode("utf-8"))
        text = "Hello! \n Someone requested a password for your account. Please click the link {} to change it. \n Thanks, The Citizen Science Team".format(
            reset
        )
        msg = message.EmailMessage()
        msg.set_content(text)
        smtp_user = "info@citizenscience.ch"
        msg["Subject"] = "Password Reset for Citizen Science Project"
        msg["From"] = smtp_user
        msg["To"] = user.email
        try:
            s = smtplib.SMTP("asmtp.mailstation.ch", 587)
            s.login(smtp_user, "UniZuETH2018")
            s.sendmail(smtp_user, [user.email], msg.as_string())
            s.quit()
        except Exception as e:
            print("ERROR RESETTING", e)
            return e, 503
        return NoContent, 200
    else:
        return NoContent, 401

@db_session
def get_subs(id=None):
    user = User[id].first()
    user = User.get(id=id)
    if user:
        submissions = user.submissions
        # TODO paging
        return [s.to_dict() for s in submissions]
    else:
        abort(404)

@db_session
def verify_reset(reset):
    print(reset)
    try:
        token = ts.unsign(reset["token"], 2000)
        user = db_session.query(User).filter(User.id == reset["id"]).one_or_none()
        user.pwd = pbkdf2_sha256.encrypt(reset["pwd"], rounds=200000, salt_size=16)
        db_session.commit()
        return True, 200
    except Exception as e:
        print(e)
        return False, 401
