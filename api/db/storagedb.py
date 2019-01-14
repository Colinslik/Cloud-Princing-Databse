# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from define import HOME_DEFAULT
from sqldb import SqlDB


Table = [('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
         ('time', "TIMESTAMP DATETIME DEFAULT(STRFTIME('%Y-%m-%dT%H:%M:%fZ', 'NOW'))"),
         ('region', 'TEXT DEFAULT NA'), ('storage_type', 'TEXT DEFAULT NA'),
         ('size', 'REAL DEFAULT -1.0'), ('price', 'REAL DEFAULT -1.0')]


class StorageDB(SqlDB):
    def __init__(self, vendor):
        self.db_file = "%s/var/%s/storage.db" % (HOME_DEFAULT, vendor)
        self.tb_name = 'storage'
        self.tb_schema = Table

        SqlDB.__init__(self, self.db_file, self.tb_name, self.tb_schema)
