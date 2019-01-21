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

from db.influx_instancedb import InstanceDB


class InstanceList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('limit', type=int, location='args')
        self.reqparse.add_argument('page', type=int, location='args')
        self.reqparse.add_argument('offset', type=int, location='args')
        self.reqparse.add_argument('tsfrom', type=str, location='args')
        self.reqparse.add_argument('tsto', type=str, location='args')
        self.reqparse.add_argument('region', type=str, location='args')
        self.reqparse.add_argument('instancetype', type=str, location='args')
        self.reqparse.add_argument(
            'operatingsystem', type=str, location='args')
        self.reqparse.add_argument(
            'preInstalledSw', type=str, location='args')

        super(InstanceList, self).__init__()

    def get(self, vendor):
        # list
        args = self.reqparse.parse_args()
        limit = args.get('limit') or 20
        page = args.get('page') or 0
        offset = args.get('offset') or 0

        try:
            db = InstanceDB()

            cond = '"vendor" = \'%s\'' % vendor
            if args['region']:
                cond += ' AND "region" = \'%s\'' % args['region']
            if args['instancetype']:
                cond += ' AND "instancetype" = \'%s\'' % args['instancetype']
            if args['operatingsystem']:
                cond += ' AND "operatingsystem" = \'%s\'' % args['operatingsystem']
            if args['preInstalledSw']:
                cond += ' AND "preInstalledSw" = \'%s\'' % args['preInstalledSw']
            if not args['tsfrom'] and not args['tsto']:
                rows, total = db.get_last_group(["vendor"], 3)
                updated = "0"
                for item in rows:
                    if item["vendor"] == vendor:
                        updated = item["updated"]
                        break
                cond += ' AND "updated" = \'{0}\''.format(
                    updated)
            else:
                if args['tsfrom']:
                    cond += ' AND "time" >= \'%s\'' % (args['tsfrom'])
                if args['tsto']:
                    cond += ' AND "time" <= \'%s\'' % (args['tsto'])

            rows, total = db.list(condition=cond,
                                  sort=[("time", "DESC")],
                                  limit=limit, page=page,
                                  offset=offset)

            for item in rows:
                for key, value in item.iteritems():
                    if isinstance(value, unicode):
                        item[key] = value.replace(
                            "\\n", "\n").replace("\\r", "\r")

        except Exception:
            formatted_lines = traceback.format_exc().splitlines()
            return {"message": formatted_lines[-1]}, INTERNAL_SERVER_ERROR

        return {'instances': rows, 'count': len(rows), 'limit': limit, 'page': page, 'offset': offset, 'total': total}, OK

    def put(self, vendor):
        # insert or update
        self.reqparse.add_argument('instances', type=list, location='json')
        args = self.reqparse.parse_args()
        instances = args['instances']
        db = InstanceDB()

        # insert
        fields = {}
        for item in instances:
            tags = {"vendor": str(vendor)}
            for key, value in item.iteritems():
                if isinstance(value, int):
                    fields.update({str(key): int(value)})
                elif isinstance(value, long):
                    fields.update({str(key): float(value)})
                else:
                    if key == "region" or key == "updated":
                        tags.update({str(key): str(value)})
                    else:
                        fields.update({str(key): str(value)})
            rows, total = db.insert(tags, fields)

        return {'instances': rows, 'count': len(rows), 'limit': 20, 'page': 0, 'offset': 0, 'total': total}, OK
