#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from httplib import OK, INTERNAL_SERVER_ERROR
import json
import traceback

from flask_restful import Resource
from flask_restful import reqparse

from db.influx_storagedb import StorageDB


class StorageList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('limit', type=int, location='args')
        self.reqparse.add_argument('offset', type=int, location='args')
        self.reqparse.add_argument('tsfrom', type=str, location='args')
        self.reqparse.add_argument('tsto', type=str, location='args')

        super(StorageList, self).__init__()

    def get(self, vendor, region):
        # list
        args = self.reqparse.parse_args()
        limit = args.get('limit') or 20
        offset = args.get('offset') or 0

        try:
            db = StorageDB()

            cond = "vendor = '%s'" % vendor
            if region == 'ALL':
                cond += ' AND "region" != \'NA\''
            else:
                cond += ' AND "region" = \'%s\'' % region
            if not args['tsfrom'] and not args['tsto']:
                rows, total = db.get_last()
                cond += ' AND "time" <= \'{0}\' AND "time" >= \'{0}\' - 1d'.format(
                    rows[0]["time"])
            else:
                if args['tsfrom']:
                    cond += ' AND "time" >= \'%s\'' % (args['tsfrom'])
                if args['tsto']:
                    cond += ' AND "time" <= \'%s\'' % (args['tsto'])

            rows, total = db.list(condition=cond,
                                  sort=[("time", "DESC")],
                                  limit=limit, offset=offset)

            for item in rows:
                for key, value in item.iteritems():
                    if isinstance(value, unicode):
                        item[key] = value.replace(
                            "\\n", "\n").replace("\\r", "\r")

        except Exception:
            formatted_lines = traceback.format_exc().splitlines()
            return {"message": formatted_lines[-1]}, INTERNAL_SERVER_ERROR

        return {'storages': rows, 'count': len(rows), 'offset': offset, 'total': total}, OK

    def put(self, vendor, region):
        # insert or update
        self.reqparse.add_argument('storages', type=list, location='json')
        args = self.reqparse.parse_args()
        storages = args['storages']
        db = StorageDB()

        # insert
        fields = {}
        for item in storages:
            tags = {"region": str(region),
                    "vendor": str(vendor)}
            for key, value in item.iteritems():
                if isinstance(value, int):
                    fields.update({str(key): int(value)})
                elif isinstance(value, long):
                    fields.update({str(key): float(value)})
                else:
                    fields.update({str(key): str(value)})
            rows, total = db.insert(tags, fields)

        return {'storages': rows, 'count': len(rows), 'offset': 0, 'total': total}, OK
