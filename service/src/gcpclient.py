import time

from db.influx_instancedb import InstanceDB
from db.influx_networkdb import NetworkDB
from db.influx_storagedb import StorageDB
from vendorclient import VendorlientApi


class GCPClientApi(VendorlientApi):

    def __init__(self,
                 endpoint='https://cloudpricingcalculator.appspot.com/static/data'):
        super(GCPClientApi, self).__init__(endpoint)

    def get_api_result(self):
        url_arg = 'pricelist.json'

        return self._send_cmd(url_arg, "GET")


if __name__ == "__main__":
    try:
        gcpclient = GCPClientApi()
        json_data = gcpclient.load_from_json_file(
            '/opt/prophetstor/alameter/var/price_data/', 'gcp_price.json')
        updated_time = str(time.time())
        db_instance = InstanceDB()
        db_storage = StorageDB()
        db_network = NetworkDB()

        json_data["gcp_price_list"]["CP-COMPUTEENGINE-OS"].update(
            {"free": {"low": 0.00,
                      "high": 0.00}})
        for key, value in json_data["gcp_price_list"].iteritems():
            if not key.startswith("CP-COMPUTEENGINE-"):
                continue
            if "cores" in value:
                params = {
                    "unit": "Hrs",
                    "currency": "USD",
                    "instancetype": key,
                    "vcpu": str(value["cores"]),
                    "memory": str(value["memory"])
                }
                for os, osprice in json_data["gcp_price_list"]["CP-COMPUTEENGINE-OS"].iteritems():
                    if type(osprice) is not dict:
                        continue
                    params.update({
                        "operatingsystem": os,
                        "osprice": osprice
                    })
                    for region, price in value.iteritems():
                        if region == "cores" or region == "memory" or region == "gceu" or region == "maxNumberOfPd" or region == "maxPdSize" or region == "ssd":
                            continue
                        params.update({
                            "region": region,
                            "priceperunit": str(price)
                        })

#                        print params
#                        params.update({"updated": updated_time})
#                        gcpclient.update_instance(
#                            "gcp", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                        gcpclient.update_database(
                            db_instance, "gcp", updated_time, params)

    except Exception as e:
        print e
