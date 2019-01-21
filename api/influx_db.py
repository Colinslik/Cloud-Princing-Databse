# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright (c) 2013-2018 ProphetStor Data Services, Inc.
# All Rights Reserved.
#

from influxdb import InfluxDBClient


class InfluxDB(object):
    """
    InfluxDB Database Query
    """

    def __init__(self, db_info, tb_name):
        self.conn = None

        self.db_info = db_info
        self.tb_name = tb_name

        self._get_connection()
        self._create_database()

    def __del__(self):
        pass

    def _get_connection(self):
        # '172.31.6.17', 8086, 'dpInfluxdb', 'DpPassw0rd', 'telegraf', ssl=True, verify_ssl=False
        self.conn = InfluxDBClient(host=self.db_info['host'],
                                   port=int(self.db_info['port']),
                                   username=self.db_info['username'],
                                   password=self.db_info['password'],
                                   database=self.db_info['database'],
                                   ssl=self.db_info.get('ssl', True),
                                   verify_ssl=self.db_info.get(
                                       'verfiy_ssl', False),
                                   timeout=self.db_info.get('timeout', None))

    def _create_database(self):
        try:
            table_list = self.conn.get_list_database()
            for table in table_list:
                if table['name'] == self.db_info['database']:
                    return True

            self.conn.create_database(self.db_info['database'])
            return True

        except Exception:
            return False

    def get_last(self):
        rows, total = self.list(sort=[
                                ("time", "DESC")], limit=1,  count=False)
        return rows, total

    def get_last_group(self, group=None, slimit=1):
        rows, total = self.list(sort=[("time", "DESC")],
                                group=group, limit=1, slimit=slimit,  count=False)
        return rows, total

    def list(self, condition=None, sort=[], group=[], limit=None, slimit=None, page=0, offset=0, count=True):
        total = 0
        cmd1 = "SELECT * FROM %s" % self.tb_name
        cmd2 = "SELECT count(*) FROM %s" % self.tb_name
        if condition:
            cmd1 += " WHERE " + condition
            cmd2 += " WHERE " + condition
        if group:
            cmd1 += " GROUP BY " + ", ".join(["%s" % i for i in group])
        if sort:
            cmd1 += " ORDER BY " + ", ".join(["%s %s" % i for i in sort])
        if limit:
            cmd1 += " LIMIT " + str(limit)
        if slimit:
            cmd1 += " SLIMIT " + str(slimit)
        if page:
            offset += page * limit if limit else page * 20
        if offset:
            cmd1 += " OFFSET " + str(offset)

        result = self.conn.query(cmd1)

        # TODO: support multiple series
        columns = result.raw.get('series', [{}])[0].get('columns', [])
        rows = []
        for count in result.raw.get('series', [{}]):
            values = count.get('values', [])
            row = []
            for v in values:
                row.append({item[0]: item[1] for item in zip(columns, v)})
            if group:
                row[0].update({item[0]: item[1]
                               for item in count.get('tags').items()})

            rows += row

        if count:
            result = self.conn.query(cmd2)
            # {u'series': [{u'values': [[u'1970-01-01T00:00:00Z', 41540, 41540, 41540, 41540, 41540, 41540, 1671]]
            total = result.raw.get('series', [{}])[
                0].get('values', [[]])[0][1:]
            total = 0 if not total else max(total)

        return rows, total

    def insert(self, tags, fields):
        json_body = [
            {
                "measurement": self.tb_name,
                "tags": tags,
                "fields": fields
            }
        ]
        self.conn.write_points(json_body, time_precision='ms')

        return self.get_last()
