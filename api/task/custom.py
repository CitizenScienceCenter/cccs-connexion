import connexion
from connexion import NoContent
from db import orm_handler, Task, Submission, Media, utils
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import joinedload
from flask import request
import sqlalchemy
import logging
from sqlalchemy.dialects import postgresql

# from flask_sqlalchemy_session import current_session as db_session

db_session = orm_handler.db_session


def project_tasks(id, limit=20, offset=0):
    print(id, limit, offset)
    task = (
        db_session.query(Task)
        .filter(Task.project_id == id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [p.dump() for p in task]


def get_region(pid, region):
    user = utils.get_user(request, db_session)
    task = (
        db_session.query(Task, Media)
        .outerjoin(Submission, Task.id == Submission.task_id)
        .join(Media, Media.source_id == Task.id)
        .filter(Task.info["SchoolState"].astext == user.info["region"])
        .filter(Submission.user_id != user.id)
        .filter(Task.project_id == id)
    )
    return


def delete_tasks(tasks):
    print("deleting {} tasks".format(len(tasks)))
    print(tasks)
    db_session.query(Task).filter(Task.id.in_(tasks)).delete(
        synchronize_session="fetch"
    )
    db_session.commit()
    return NoContent, 200


def get_random(pid, search):
    user = utils.get_user(request, db_session)
    task = (
        db_session.query(Task, Media)
        .outerjoin(Submission, Task.id == Submission.task_id)
        .join(Media, Media.source_id == Task.id)
        .filter(
            (Task.info["SchoolState"].astext == search)
            | (Task.info["SchoolState"].astext == "")
        )
        .filter((Submission.id == None) | (Submission.user_id != user.id))
        .order_by(func.random())
        .first()
    )
    if task is None:
        return NoContent, 404
    else:
        ret = {"task": task[0].dump(), "media": task[1].dump()}
        return ret, 200
