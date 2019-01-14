#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

import re
import json
from httplib import OK, CREATED, NO_CONTENT
from httplib import NOT_FOUND, CONFLICT

from db.configdb import ConfigDB


CONF = "alameter.conf"
USER_CONF = "alameter.conf.user"


class Config():

    def __init__(self):
        pass

    @staticmethod
    def get(host, section):
        # get section

        db = ConfigDB(host)
        row = db.get(CONF)
        urow = db.get(USER_CONF)

        conf, uconf = {}, {}
        if row:
            conf = json.loads(row['config'].decode('unicode-escape'))
        if urow:
            uconf = json.loads(urow['config'].decode('unicode-escape'))

        if (section not in conf) and (section not in uconf):
            return None

        # update uconf into conf
        if section not in conf:
            conf[section] = uconf[section]
        else:
            conf[section].update(uconf.get(section, {}))

        return conf[section]

    @staticmethod
    def get_ex(host, sec_regex):
        # get sections
        # support regular expression of section name

        regex = re.compile(sec_regex)

        # read configurations
        db = ConfigDB(host)
        row = db.get(CONF)
        urow = db.get(USER_CONF)

        conf, uconf, nconf = {}, {}, {}
        if row:
            conf = json.loads(row['config'].decode('unicode-escape'))
        if urow:
            uconf = json.loads(urow['config'].decode('unicode-escape'))

        # merge matched sections
        for sec in conf:
            if not re.match(regex, sec):
                continue

            if sec not in nconf:
                nconf[sec] = conf[sec]

        for sec in uconf:
            if not re.match(regex, sec):
                continue

            # update uconf into conf
            if sec not in nconf:
                nconf[sec] = uconf[sec]
            else:
                nconf[sec].update(uconf[sec])

        return nconf

    @staticmethod
    def add(host, section, options):
        # add section

        db = ConfigDB(host)
        row = db.get(CONF)
        urow = db.get(USER_CONF)

        conf, uconf = {}, {}
        if row:
            conf = json.loads(row['config'].decode('unicode-escape'))
        if urow:
            uconf = json.loads(urow['config'].decode('unicode-escape'))

        if section in uconf or section in conf:
            # section exists
            return CONFLICT, {}

        uconf[section] = options

        # update back
        db.update(USER_CONF, {'config': json.dumps(uconf)})

        return CREATED, {section: uconf[section]}

    @staticmethod
    def update(host, section, options):
        # update section

        db = ConfigDB(host)
        urow = db.get(USER_CONF)

        uconf = {}
        if urow:
            uconf = json.loads(urow['config'].decode('unicode-escape'))

        if section not in uconf:
            # add options
            uconf[section] = options
        else:
            # update options
            uconf[section].update(options)

        # write back
        db.update(USER_CONF, {'config': json.dumps(uconf)})

        return OK, {section: uconf[section]}

    @staticmethod
    def delete(host, section):
        # delete section

        db = ConfigDB(host)
        urow = db.get(USER_CONF)

        uconf = {}
        if urow:
            uconf = json.loads(urow['config'].decode('unicode-escape'))

        if section not in uconf:
            return NOT_FOUND

        del uconf[section]

        # update back
        db.update(USER_CONF, {'config': json.dumps(uconf)})

        return NO_CONTENT


if __name__ == '__main__':

    host = 'WIN-6I9H2SO6EFG'
    section = 'section.test'
    options = {'option1': '111', 'option2': '222'}

    conf = Config()
    print(json.dumps(conf.get(host, 'main')))
    print
    print(json.dumps(conf.get(host, 'service.diskprophet')))
    print

    print(json.dumps(conf.get_ex(host, '^action\.').keys()))
    print

    print(conf.add(host, section, options))
    print(json.dumps(conf.get(host, section)))
    print

    options = {'option3': '111', 'option2': '333'}
    print(conf.update(host, section, options))
    print(json.dumps(conf.get(host, section)))
    print

    print(conf.delete(host, section))
