# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

import json
import os
from influx_db import InfluxDB


class NetworkDB(InfluxDB):
    def __init__(self):
        self.tb_name = 'network'

        host = os.environ["INFLUXDB_SERVICE_HOST"]
        port = os.environ["INFLUXDB_SERVICE_PORT"]
        username = "root"
        password = "root"
        self.db_info = {'host': host,
                        'port': int(port),
                        'username': username,
                        'password': password,
                        'database': "telegraf",
                        'ssl': False}

        InfluxDB.__init__(self, self.db_info, self.tb_name)


if __name__ == '__main__':
    import traceback

    try:
        db = NetworkDB()

        print("\n========== List ==========")
        print(db.list(condition="pda_server = 'WIN-6I9H2SO6EFG'",
                      sort=[("time", "DESC")], limit=10, offset=0))

    except Exception:
        traceback.print_exc()
        formatted_lines = traceback.format_exc().splitlines()
        print(formatted_lines[-1])
