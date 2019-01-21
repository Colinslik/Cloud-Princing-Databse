#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from httplib import OK, NOT_FOUND

from flask import Flask, jsonify
from flask_restful import Api

from res.config import Config, ConfigList
from res.influx_instance import InstanceList
from res.influx_network import NetworkList
from res.influx_storage import StorageList


app = Flask(__name__)
api = Api(app)


@app.route('/')
def root():
    response = {"api": "ProphetStor Alameter API",
                "version": "1.0.0",
                "status": "running",
                "message": "Welcome to access Alameter API."}
    return jsonify(response), OK


@app.errorhandler(404)
def not_found(e):
    response = {"message": "Resource not found."}
    return jsonify(response), NOT_FOUND


# add api resources
api.add_resource(ConfigList, '/prices/<string:vendor>/configs',
                 '/prices/<string:vendor>/configs/')
api.add_resource(Config, '/prices/<string:vendor>/configs/<string:id>')
api.add_resource(InstanceList, '/prices/<string:vendor>/instances',
                 '/prices/<string:vendor>/instances/')
api.add_resource(NetworkList, '/prices/<string:vendor>/networks',
                 '/prices/<string:vendor>/networks/')
api.add_resource(StorageList, '/prices/<string:vendor>/storage',
                 '/prices/<string:vendor>/storage/')
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8999)
