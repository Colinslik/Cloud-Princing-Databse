import json
import os

import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AWSClientApi(object):

    def __init__(self,
                 endpoint='https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws',
                 offercode='AmazonEC2',
                 outputtype='json',
                 db_endpoint='http://172.31.6.71:31256/alameter/api'):
        self.endpoint = endpoint
        self.offercode = offercode
        self.outputtype = outputtype
        self.db_endpoint = db_endpoint

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
        url_arg = '{0}/current/index.{1}'.format(
            self.offercode, self.outputtype)

        return self._send_cmd(url_arg, "GET")

    def load_from_json_file(self, filename):
        if not os.path.exists(filename):
            json_data = self.get_api_result()
            with open(filename, 'w') as outfile:
                json.dump(json_data, outfile)
        with open(filename) as f:
            data = json.load(f)

        return data

    def update_instance(self, vendor, region, params):
        url_arg = '{0}/instances/{1}'.format(vendor, region)
        body = {
            "instances": [params]
        }
        return self._send_cmd(url_arg, body, "PUT", self.db_endpoint)

    def update_storage(self, vendor, region, params):
        url_arg = '{0}/storages/{1}'.format(vendor, region)
        body = {
            "storages": [params]
        }
        return self._send_cmd(url_arg, body, "PUT", self.db_endpoint)

    def update_network(self, vendor, region, params):
        url_arg = '{0}/networks/{1}'.format(vendor, region)
        body = {
            "networks": [params]
        }
        return self._send_cmd(url_arg, body, "PUT", self.db_endpoint)


if __name__ == "__main__":
    try:
        awsclient = AWSClientApi()
        json_data = awsclient.load_from_json_file('./AmazonEC2.json')
        for key, value in json_data["terms"]["OnDemand"].iteritems():
            '''
            print key, value.values()[0]["priceDimensions"].values()[0]["description"], \
                value.values()[0]["priceDimensions"].values()[0]["unit"], \
                value.values()[0]["priceDimensions"].values()[0]["pricePerUnit"].keys()[0], \
                value.values()[0]["priceDimensions"].values()[
                0]["pricePerUnit"].values()[0]
            '''
            params = {
                "description": value.values()[0]["priceDimensions"].values()[0]["description"],
                "unit": value.values()[0]["priceDimensions"].values()[0]["unit"],
                "currency": value.values()[0]["priceDimensions"].values()[0]["pricePerUnit"].keys()[0],
                "priceperunit": value.values()[0]["priceDimensions"].values()[
                    0]["pricePerUnit"].values()[0]
            }
            if json_data["products"][key]["productFamily"] == "Compute Instance":
                '''
                print json_data["products"][key]["productFamily"], \
                    json_data["products"][key]["attributes"]["location"], \
                    json_data["products"][key]["attributes"]["instanceType"], \
                    json_data["products"][key]["attributes"]["vcpu"], \
                    json_data["products"][key]["attributes"]["memory"], \
                    json_data["products"][key]["attributes"]["storage"], \
                    json_data["products"][key]["attributes"]["networkPerformance"], \
                    json_data["products"][key]["attributes"]["operatingSystem"], \
                    json_data["products"][key]["attributes"]["ecu"]
                '''
                params.update({
                    "instancetype": json_data["products"][key]["attributes"]["instanceType"],
                    "vcpu": json_data["products"][key]["attributes"]["vcpu"],
                    "memory": json_data["products"][key]["attributes"]["memory"],
                    "storage": json_data["products"][key]["attributes"]["storage"],
                    "networkperformance": json_data["products"][key]["attributes"]["networkPerformance"],
                    "operatingsystem": json_data["products"][key]["attributes"]["operatingSystem"],
                    "ecu": json_data["products"][key]["attributes"]["ecu"]
                })

                awsclient.update_instance("AWS", str(
                    json_data["products"][key]["attributes"]["location"]), params)

            elif json_data["products"][key]["productFamily"] == "Storage":
                '''
                print json_data["products"][key]["productFamily"], \
                    json_data["products"][key]["attributes"]["location"], \
                    json_data["products"][key]["attributes"]["volumeType"], \
                    json_data["products"][key]["attributes"]["maxVolumeSize"], \
                    json_data["products"][key]["attributes"]["maxIopsvolume"], \
                    json_data["products"][key]["attributes"]["maxThroughputvolume"]
                '''
                params.update({
                    "volumetype": json_data["products"][key]["attributes"]["volumeType"],
                    "volumesize": json_data["products"][key]["attributes"]["maxVolumeSize"],
                    "iops": json_data["products"][key]["attributes"]["maxIopsvolume"],
                    "throughput": json_data["products"][key]["attributes"]["maxThroughputvolume"]
                })

                awsclient.update_storage("AWS", str(
                    json_data["products"][key]["attributes"]["location"]), params)

            elif json_data["products"][key]["productFamily"] == "Data Transfer":
                if json_data["products"][key]["attributes"]["fromLocation"] == "External":
                    # print "UPLOAD",
                    # json_data["products"][key]["attributes"]["toLocation"]
                    params.update({
                        "transfertype": "UPLOAD",
                    })

                    awsclient.update_network("AWS", str(
                        json_data["products"][key]["attributes"]["toLocation"]), params)

                elif json_data["products"][key]["attributes"]["toLocation"] == "External":
                    # print "DOWNLOAD",
                    # json_data["products"][key]["attributes"]["fromLocation"]
                    params.update({
                        "transfertype": "DOWNLOAD",
                    })

                    awsclient.update_network("AWS", str(
                        json_data["products"][key]["attributes"]["fromLocation"]), params)

    except Exception as e:
        print e
