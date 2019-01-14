#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from httplib import NOT_FOUND, BAD_REQUEST, CONFLICT
from httplib import OK, CREATED, NO_CONTENT
import json

from flask_restful import Resource
from flask_restful import reqparse

from db.configdb import ConfigDB


#from res.auth import auth
class ConfigList(Resource):
    #    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'id', type=str, location='json', required=True)
        self.reqparse.add_argument(
            'config', type=dict, location='json', required=True)

        super(ConfigList, self).__init__()

    def get(self, host):
        # list
        db = ConfigDB(host)
        rows = db.list()
        for row in rows:
            row['config'] = json.loads(row['config'].decode('unicode-escape'))
        return {'configs': rows}, OK

    def post(self, host):
        # create
        retcode = CONFLICT

        args = self.reqparse.parse_args()
        id = args['id']
        config = args['config']

        db = ConfigDB(host)
        row = db.get(id)
        if row:
            return {"message": "Resource already exists."}, CONFLICT

        row = db.insert({'id': id, 'config': json.dumps(config)})
        retcode = CREATED

        config = json.loads(row['config'].decode('unicode-escape'))
        return {'config': config}, retcode


class Config(Resource):
    #decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'config', type=dict, location='json', required=True)

        super(Config, self).__init__()

    def get(self, host, id):
        # get
        db = ConfigDB(host)
        row = db.get(id)
        if not row:
            return {"message": "Resource '%s' not found." % id}, NOT_FOUND

        # XXX: not very clear why need to decode
        config = json.loads(row['config'].decode('unicode-escape'))
        #config = json.loads(row['config'].replace('\\\\', '\\'))

        return {'config': config}, OK

    def put(self, host, id):
        # update
        args = self.reqparse.parse_args()

        db = ConfigDB(host)
        row = db.get(id)
        if not row:
            return {"message": "Resource '%s' does not exist." % id}, BAD_REQUEST

        # whole content of config is updated
        row = db.update(id, {'config': json.dumps(args['config'])})

        config = json.loads(row['config'].decode('unicode-escape'))
        return {'config': config}, OK

    def delete(self, host, id):
        # delete
        db = ConfigDB(host)
        row = db.get(id)
        if not row:
            return {"message": "Resource '%s' does not exist." % id}, NOT_FOUND

        db.delete(id)

        return {}, NO_CONTENT
