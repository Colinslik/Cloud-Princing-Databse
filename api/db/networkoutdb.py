# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from define import HOME_DEFAULT
from sqldb import SqlDB


Table = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
         ('time', "TIMESTAMP DATETIME DEFAULT(STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'NOW'))"),
         ('region', 'TEXT DEFAULT NA'), ('upper_limit', 'REAL DEFAULT -1.0'),
         ('lower_limit', 'REAL DEFAULT -1.0'), ('price', 'REAL DEFAULT -1.0')]


class NetworkoutDB(SqlDB):
    def __init__(self, vendor):
        self.db_file = "%s/var/%s/networkout.db" % (HOME_DEFAULT, vendor)
        self.tb_name = 'networkout'
        self.tb_schema = Table

        SqlDB.__init__(self, self.db_file, self.tb_name, self.tb_schema)


if __name__ == '__main__':
    import traceback

    try:
        db = NetworkoutDB('WIN-6I9H2SO6EFG')

        print("\n========== List ==========")
        print(db.list(condition="pda_server = 'WIN-6I9H2SO6EFG'",
                      sort=[("time", "DESC")], limit=10, offset=0))

    except Exception:
        traceback.print_exc()
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[-1])
