import time

from db.influx_instancedb import InstanceDB
from db.influx_networkdb import NetworkDB
from db.influx_storagedb import StorageDB
from vendorclient import VendorlientApi


class AWSClientApi(VendorlientApi):

    def __init__(self,
                 endpoint='https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws',
                 offercode='AmazonEC2',
                 outputtype='json'):
        super(AWSClientApi, self).__init__(endpoint, offercode, outputtype)

    def get_api_result(self):
        url_arg = '{0}/current/index.{1}'.format(
            self.offercode, self.outputtype)

        return self._send_cmd(url_arg, "GET")


if __name__ == "__main__":
    try:
        awsclient = AWSClientApi()
        json_data = awsclient.load_from_json_file(
            '/opt/prophetstor/alameter/var/price_data/', 'AmazonEC2.json')
        updated_time = str(time.time())
        db_instance = InstanceDB()
        db_storage = StorageDB()
        db_network = NetworkDB()
        for key, value in json_data["terms"]["OnDemand"].iteritems():
            params = {
                "description": value.values()[0]["priceDimensions"].values()[0]["description"],
                "unit": value.values()[0]["priceDimensions"].values()[0]["unit"],
                "currency": value.values()[0]["priceDimensions"].values()[0]["pricePerUnit"].keys()[0],
                "priceperunit": value.values()[0]["priceDimensions"].values()[
                    0]["pricePerUnit"].values()[0]
            }
            if json_data["products"][key]["productFamily"] == "Compute Instance":
                params.update({
                    "region": json_data["products"][key]["attributes"]["location"],
                    "instancetype": json_data["products"][key]["attributes"]["instanceType"],
                    "vcpu": json_data["products"][key]["attributes"]["vcpu"],
                    "memory": json_data["products"][key]["attributes"]["memory"],
                    "storage": json_data["products"][key]["attributes"]["storage"],
                    "networkperformance": json_data["products"][key]["attributes"]["networkPerformance"],
                    "operatingsystem": json_data["products"][key]["attributes"]["operatingSystem"],
                    "ecu": json_data["products"][key]["attributes"]["ecu"],
                    "preinstalledsw": json_data["products"][key]["attributes"]["preInstalledSw"]
                })
                if "On Demand" not in params["description"]:
                    continue

#                print params
#                params.update({"updated": updated_time})
#                awsclient.update_instance(
#                    "aws", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                awsclient.update_database(
                    db_instance, "aws", updated_time, params)

            elif json_data["products"][key]["productFamily"] == "Storage":
                params.update({
                    "region": json_data["products"][key]["attributes"]["location"],
                    "volumetype": json_data["products"][key]["attributes"]["volumeType"],
                    "volumesize": json_data["products"][key]["attributes"]["maxVolumeSize"],
                    "iops": json_data["products"][key]["attributes"]["maxIopsvolume"],
                    "throughput": json_data["products"][key]["attributes"]["maxThroughputvolume"]
                })

#                print params
#                params.update({"updated": updated_time})
#                awsclient.update_storage(
#                    "aws", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                awsclient.update_database(
                    db_storage, "aws", updated_time, params)

            elif json_data["products"][key]["productFamily"] == "Data Transfer":
                if json_data["products"][key]["attributes"]["fromLocation"] == "External":
                    params.update({
                        "region": json_data["products"][key]["attributes"]["toLocation"],
                        "transfertype": "UPLOAD",
                        "beginrange": value.values()[0]["priceDimensions"].values()[0]["beginRange"],
                        "endrange": value.values()[0]["priceDimensions"].values()[0]["endRange"]
                    })

#                    print params
#                    params.update({"updated": updated_time})
#                    awsclient.update_network(
#                        "aws", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                    awsclient.update_database(
                        db_network, "aws", updated_time, params)

                elif json_data["products"][key]["attributes"]["toLocation"] == "External":
                    params.update({
                        "region": json_data["products"][key]["attributes"]["fromLocation"],
                        "transfertype": "DOWNLOAD",
                        "beginrange": value.values()[0]["priceDimensions"].values()[0]["beginRange"],
                        "endrange": value.values()[0]["priceDimensions"].values()[0]["endRange"]
                    })

#                    print params
#                    params.update({"updated": updated_time})
#                    awsclient.update_network(
#                        "aws", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                    awsclient.update_database(
                        db_network, "aws", updated_time, params)

    except Exception as e:
        print e
