from db import Task, Project, DB, Media
from api import model
import uuid
from middleware.response_handler import ResponseHandler
from flask import session, request, current_app, abort
from datetime import datetime
from pony.orm import core, commit, select
from pony.flask import db_session


def reimport_tasks_csv(pid, body):
   return handle_import(pid, body, True)

def import_tasks_csv(pid, body):
    return handle_import(pid, body, False)

@db_session
def handle_import(pid, body, reimport):
    p = Project.get(id=pid)
    tasks = []
    path = ''
    if reimport:
        p.tasks.clear()
        commit()
    if p:
        for row in body:
            try:
                if len(row.keys()) > 0 and row['part_of'] and row['title']:
                    row['part_of'] = p.id
                    if 'path' in row:
                        path = row['path']
                        row['info']['path'] = row['path']
                        del row['path']
                    res, t = model.post(Task, row)
                    if path != '':
                        # TODO check source and annotate with type
                        # TODO allow upload to storage
                        res, media  = model.post(Media, {'source_id': t.id, 'path': path, 'name': path, 'task': t})
                        path = ''
                    tasks.append(t.to_dict())
            except Exception as e:
                abort(500, e)
        return ResponseHandler(201, "Tasks imported successfully", body=tasks).send()
    else:
        return ResponseHandler(404, "No Project Found", body={}).send()

@db_session
def import_media_csv(tid, body):
    t = Task.get(id=tid)
    media = []
    if t:
        for row in body:
            try:
                row['source_id'] = tid
                if not 'name' in row:
                    row['name'] = row['path']
                res, m = model.post(Media, row)
                media.append(m.to_dict)
            except Exception as e:
                abort(500, e)
    else:
        return ResponseHandler(404, "No Source ID for Media found", body={}).send()

@db_session
def import_remote_csv(pid, content):
    pass

