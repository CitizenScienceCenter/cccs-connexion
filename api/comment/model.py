import connexion
from db import orm_handler, Comment, utils
from flask import request
import logging
from api import model

# db_session = orm_handler.db_session

Model = Comment

def get_comments(limit=100, search_term=None):
    ms, code = model.get_all(Model, limit, search_term)
    if len(ms) > 0 and isinstance(ms[0], Comment):
        return [m.dump() for m in ms][:limit], code
    else:
        return [dict(m) for m in ms][:limit], code


def get_comment(cid=None):
    m, code = model.get_one(Model, cid)
    return m.dump() if m is not None else m, code

def create_comment(body):
    m, code = model.post(Model, body)
    return m.dump(), code

def update_comment(id, body):
    m, code = model.put(Model, id, body)
    return m.dump(), code

def delete_comment(id):
    return model.delete(Model, id)
