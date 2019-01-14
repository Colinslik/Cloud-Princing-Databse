import json
import requests
import azure


class AzureClientApi(object):

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def _send_cmd(self, url_arg, params=None, method="GET"):

        url = '{0}/{1}'.format(self.endpoint, url_arg)

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

    def update_instance(self, vendor, region, params):
        url_arg = '{0}/instances/{1}'.format(vendor, region)
        body = {
            "instances": [params]
        }
        return self._send_cmd(url_arg, body, "PUT")

    def update_storage(self, vendor, region, params):
        url_arg = '{0}/storages/{1}'.format(vendor, region)
        body = {
            "storages": [params]
        }
        return self._send_cmd(url_arg, body, "PUT")

    def update_network(self, vendor, region, params):
        url_arg = '{0}/networkouts/{1}'.format(vendor, region)
        body = {
            "networkouts": [params]
        }
        return self._send_cmd(url_arg, body, "PUT")


if __name__ == "__main__":
    azure = azure.Azure()
    azureclient = AzureClientApi("http://172.31.6.18:8345/alameter/api")

    for region, data_raw in azure.get_instance_price().iteritems():
        for instance_type, data_info in data_raw.iteritems():
            azureclient.update_instance(
                "Azure",
                region,
                {"image_type": "linux",
                 "machine_type": "NA",
                 "instance_type": instance_type,
                 "region": region,
                 "ecu": data_info['ecu'] if 'ecu' in data_info else 'NA',
                 "memory": data_info['memory'] if 'memory' in data_info else -1.0,
                 "price": data_info['price'] if 'price' in data_info and isinstance(data_info['price'], float) else 0.0,
                 "vcpu": data_info['vcpu'] if 'vcpu' in data_info else -1,
                 "storage_size": data_info['storage_size'] if 'storage_size' in data_info else 'NA',
                 "storage_type": data_info['storage_type'] if 'storage_type' in data_info else 'NA',
                 })

    for region, data_raw in azure.get_storage_price().iteritems():
        for storage_type, data_info in data_raw.iteritems():
            azureclient.update_storage(
                "Azure",
                region,
                {"region": region,
                 "size": data_info["size"],
                 "storage_type": storage_type,
                 "price": data_info["price"] if isinstance(data_info["price"], float) else 0.0
                 })

    for region, data_raw in azure.get_network_price().iteritems():
        for limit, price in data_raw.iteritems():
            if '-' in limit:
                pos = limit.find("-")
                upper_limit = float(
                    limit[:pos]) * 1024 if 'TB' in limit[-2:] else float(limit[:-2])
                lower_limit = float(
                    limit[pos + 1:-2]) * 1024 if 'TB' in limit[-2:] else float(limit[:-2])
            elif '>' in limit:
                pos = limit.find(">")
                upper_limit = -1.0
                lower_limit = float(
                    limit[pos + 1:-2]) * 1024 if 'TB' in limit[-2:] else float(limit[:-2])
            elif '<' in limit:
                pos = limit.find("<")
                upper_limit = float(
                    limit[pos + 1:-2]) * 1024 if 'TB' in limit[-2:] else float(limit[:-2])
                lower_limit = -1.0
            else:
                upper_limit = float(
                    limit[:-2]) * 1024 if 'TB' in limit[-2:] else float(limit[:-2])
                lower_limit = -1.0
            azureclient.update_network(
                "Azure",
                region,
                {"region": region,
                 "upper_limit": upper_limit,
                 "lower_limit": lower_limit,
                 "price": price if isinstance(price, float) else 0.0
                 })
#    print azure.get_instance_price()
#    print azure.get_storage_price()
#    print azure.get_network_price()
