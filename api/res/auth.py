#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from httplib import FORBIDDEN
import os

from flask import jsonify, make_response
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):

    return True


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), FORBIDDEN)
