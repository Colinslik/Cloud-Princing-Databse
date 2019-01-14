# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

import os
import json
from ConfigParser import SafeConfigParser

from define import HOME_DEFAULT
from sqldb import SqlDB, printTable
from db.instancedb import InstanceDB


Table = [('id', 'TEXT PRIMARY KEY'), ('config', 'TEXT')]


class ConfigDB(SqlDB):
    def __init__(self, host):
        self.db_file = "%s/var/%s/config.db" % (HOME_DEFAULT, host)
        self.tb_name = 'config'
        self.tb_schema = Table

        SqlDB.__init__(self, self.db_file, self.tb_name, self.tb_schema)

        if host != "local.host":
            # add default configuration
            db = InstanceDB()
            row = db.get(host)
            app = row['application']
            self._add_default(app)

    def _add_default(self, app):

        for id in ['alameter.conf', 'alameter.conf.user']:
            row = self.get(id)
            if row:
                # configuration exists
                continue

            # load configuration
            if id == 'alameter.conf':
                path = "%s/api/etc/%s.%s" % (HOME_DEFAULT, id, app.lower())
            else:
                path = "%s/api/etc/%s" % (HOME_DEFAULT, id)
            if not os.path.isfile(path):
                continue

            conf_parser = SafeConfigParser()
            conf_parser.read(path)

            conf = {}
            for s in conf_parser.sections():
                conf[s] = {}
                for o in conf_parser.options(s):
                    conf[s][o] = conf_parser.get(s, o)

            # insert to database
            row = self.get(id)
            if not row:
                # check again to prevent concurrent insert
                self.insert({'id': id, 'config': json.dumps(conf)})


if __name__ == '__main__':
    import traceback

    id = 'alameter.conf.user'
    config = {'main': {'main.interval': 3600, 'main.enabled': True}}

    try:
        db = ConfigDB('test')
        print("\n========== Insert ==========")
        item = {'id': id, 'config': json.dumps(config)}
        item = db.insert(item)

        print("\n========== List ==========")
        printTable(db.list(), [item[0] for item in Table])

        print("\n========== Update ==========")
        config['main']['main.interval'] = 60
        item = {'config': json.dumps(config)}
        item = db.update(id, item)

        print("\n========== List ==========")
        printTable(db.list(), [item[0] for item in Table])

        print("\n========== Delete =========")
        db.delete(id)

        print("\n========== List  ==========")
        printTable(db.list(), [item[0] for item in Table])

    except Exception:
        traceback.print_exc()
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[-1])

