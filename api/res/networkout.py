#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from datetime import datetime
from httplib import NOT_FOUND, INTERNAL_SERVER_ERROR
from httplib import OK, NO_CONTENT
import json
import traceback

from flask_restful import Resource
from flask_restful import reqparse

from db.networkoutdb import NetworkoutDB
#from res.auth import auth


class NetworkoutList(Resource):
    #    decorators = [auth.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('limit', type=int, location='args')
        self.reqparse.add_argument('offset', type=int, location='args')
        self.reqparse.add_argument('tsfrom', type=str, location='args')
        self.reqparse.add_argument('tsto', type=str, location='args')

        super(NetworkoutList, self).__init__()

    def get(self, vendor, region):
        # list
        args = self.reqparse.parse_args()
        limit = args.get('limit') or 20
        offset = args.get('offset') or 0

        try:
            db = NetworkoutDB(vendor)

            if region == 'ALL':
                cond = "NOT region = 'NA'"
            else:
                cond = "region = '%s'" % region
            if not args['tsfrom'] and not args['tsto']:
                cond += " AND substr(time,0,14) IN (select substr(time,0,14) from %s GROUP BY date(time) ORDER BY time DESC limit 1)" % db.tb_name
            else:
                if args['tsfrom']:
                    cond += " AND time >= %s" % (args['tsfrom'])
                if args['tsto']:
                    cond += " AND time <= %s" % (args['tsto'])

            rows, total = db.list(condition=cond,
                                  sort=[("time", "DESC")],
                                  limit=limit, offset=offset, count=True)

            for item in rows:
                for key, value in item.iteritems():
                    if isinstance(value, unicode):
                        item[key] = value.replace(
                            "\\n", "\n").replace("\\r", "\r")

        except Exception:
            formatted_lines = traceback.format_exc().splitlines()
            return {"message": formatted_lines[-1]}, INTERNAL_SERVER_ERROR

        return {'networkouts': rows, 'count': len(rows), 'offset': offset, 'total': total}, OK

    def put(self, vendor, region):
        # insert or update
        self.reqparse.add_argument('networkouts', type=list, location='json')
        args = self.reqparse.parse_args()
        networkouts = args['networkouts']
        db = NetworkoutDB(vendor)

        # insert
        for item in networkouts:
            row = {"region": str(region)}
            for key, value in item.iteritems():
                if isinstance(value, int):
                    row.update({str(key): int(value)})
                else:
                    row.update({str(key): str(value)})
            db.insert(row)

        return json.dumps({'networkouts': networkouts}, ensure_ascii=False).decode('utf-8'), OK
