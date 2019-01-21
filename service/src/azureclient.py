import time

from db.influx_instancedb import InstanceDB
from db.influx_networkdb import NetworkDB
from db.influx_storagedb import StorageDB
from vendorclient import VendorlientApi


class AzureClientApi(VendorlientApi):

    def __init__(self,
                 endpoint='https://azure.microsoft.com/api/v2/pricing',
                 offercode='virtual-machines-software'):
        super(AzureClientApi, self).__init__(endpoint, offercode)

    def get_api_result(self):
        url_arg = '{0}/calculator'.format(
            self.offercode)

        return self._send_cmd(url_arg, "GET")


if __name__ == "__main__":
    try:
        azureclient = AzureClientApi(
            offercode='virtual-machines-software')
        json_data = azureclient.load_from_json_file(
            '/opt/prophetstor/alameter/var/price_data/', 'virtual-machines-software.json')
        updated_time = str(time.time())
        db_instance = InstanceDB()
        db_storage = StorageDB()
        db_network = NetworkDB()
        for key, value in json_data["offers"].iteritems():
            if "baseOfferSlug" not in value:
                continue
            params = {
                "unit": "Hrs",
                "currency": "USD",
                "instancetype": key,
                "operatingsystem": value["baseOfferSlug"],
                "vcpu": str(value["cores"]),
                "memory": str(value["ram"]),
                "storage": str(value["diskSize"]),
                "isvcpu": value["isVcpu"]
            }
            for region, price in value["prices"].iteritems():
                params.update({
                    "region": region,
                    "priceperunit": str(price["value"])
                })

#                print params
#                params.update({"updated": updated_time})
#                azureclient.update_instance(
#                    "azure", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                azureclient.update_database(
                    db_instance, "azure", updated_time, params)

        azureclient = AzureClientApi(
            offercode='managed-disks')
        json_data = azureclient.load_from_json_file(
            '/opt/prophetstor/alameter/var/price_data/', 'managed-disks.json')
        for key, value in json_data["offers"].iteritems():
            if "size" not in value:
                continue
            params = {
                "unit": "Month",
                "currency": "USD",
                "volumetype": key,
                "volumesize": str(value["size"]) if "size" in value else "0",
                "iops": str(value["iops"]) if "iops" in value else "0",
                "throughput": str(value["speed"]) if "speed" in value else "0"
            }
            for region, price in value["prices"].iteritems():
                params.update({
                    "region": region,
                    "priceperunit": str(price["value"])
                })

#                print params
#                params.update({"updated": updated_time})
#                azureclient.update_storage(
#                    "azure", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                azureclient.update_database(
                    db_storage, "azure", updated_time, params)

        azureclient = AzureClientApi(
            offercode='bandwidth')
        json_data = azureclient.load_from_json_file(
            '/opt/prophetstor/alameter/var/price_data/', 'bandwidth.json')
        for key, value in json_data["graduatedOffers"].iteritems():
            params = {
                "unit": "Month",
                "currency": "USD"
            }
            begin_range = "0"
            for region, pricelist in value.iteritems():
                for pricedata in pricelist["prices"]:
                    params.update({
                        "region": region,
                        "priceperunit": str(pricedata["price"]["value"]),
                        "transfertype": "DOWNLOAD",
                        "beginrange": begin_range,
                        "endrange": str(pricedata["limit"])
                    })

                    begin_range = str(pricedata["limit"])
#                    print params
#                    params.update({"updated": updated_time})
#                    azureclient.update_network(
#                        "azure", "http://172.31.6.71:8999/alameter-api/v1/prices", params)
                    azureclient.update_database(
                        db_network, "azure", updated_time, params)

    except Exception as e:
        print e
