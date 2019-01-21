import json
import os

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VendorlientApi(object):

    def __init__(self,
                 endpoint='',
                 offercode='',
                 outputtype=''):
        self.endpoint = endpoint
        self.offercode = offercode
        self.outputtype = outputtype

    def _send_cmd(self, url_arg, params=None, method="GET", endpoint=None):

        if not endpoint:
            endpoint = self.endpoint

        url = '{0}/{1}'.format(endpoint, url_arg)

        headers = {"Content-Type": "application/json"}

        try:
            if method == "GET":
                result = requests.get(
                    url, headers=headers, verify=False)
            elif method == "PUT":
                result = requests.put(
                    url, headers=headers, data=json.dumps(params), verify=False)
        except Exception as e:
            print ("%s" % (e))
            return None
        else:
            if result.status_code == 200:
                return json.loads(result.text)
            else:
                print (
                    "%s %s" % (result.status_code, result.text))
                return None

    def get_api_result(self):
        pass

    def load_from_json_file(self, path, filename):
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(path + filename):
            json_data = self.get_api_result()
            with open(path + filename, 'w') as outfile:
                json.dump(json_data, outfile)
        with open(path + filename) as f:
            data = json.load(f)

        return data

    def update_database(self, dbclient, vendor, updated_time, params):
        fields = {}
        tags = {"vendor": str(vendor),
                "updated": updated_time}
        for key, value in params.iteritems():
            if isinstance(value, int):
                fields.update({str(key): int(value)})
            elif isinstance(value, long):
                fields.update({str(key): float(value)})
            else:
                if key == "region":
                    tags.update({str(key): str(value)})
                else:
                    fields.update({str(key): str(value)})
        rows, total = dbclient.insert(tags, fields)
        return rows, total

    def update_instance(self, vendor, db_endpoint, params):
        url_arg = '{0}/instances'.format(vendor)
        body = {
            "instances": [params]
        }
        return self._send_cmd(url_arg, body, "PUT", db_endpoint)

    def update_storage(self, vendor, db_endpoint, params):
        url_arg = '{0}/storage'.format(vendor)
        body = {
            "storage": [params]
        }
        return self._send_cmd(url_arg, body, "PUT", db_endpoint)

    def update_network(self, vendor, db_endpoint, params):
        url_arg = '{0}/networks'.format(vendor)
        body = {
            "networks": [params]
        }
        return self._send_cmd(url_arg, body, "PUT", db_endpoint)


if __name__ == "__main__":
    pass
