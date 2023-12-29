import json
import yaml
import logging

from pymongo import MongoClient
from cerberus import Validator
from flask import Flask, abort, request

app = Flask(__name__)
mongo_client = MongoClient("mongodb://root:test1234@registry_db")
db = mongo_client["registrydb"]
#logging.info(db.server_info)


def load_cerberus_validator_by_filename(filename):
    with open(filename, "r") as f:
        content = yaml.safe_load(f.read())
        #logging.error(content)
        return Validator(content)


CRB_DATASTORE_INFO = load_cerberus_validator_by_filename("def_datastore_info.yml")


def is_valid_registration_information(reginfo):    
    success = CRB_DATASTORE_INFO.validate(reginfo)
    if not success:
        logging.error(CRB_DATASTORE_INFO.errors)
    return success


@app.route("/api/registry", methods=["POST"])
def register_datastore():    
    json_data = json.loads(request.data)
    #logging.info(json_data)
    if is_valid_registration_information(json_data):
        country = json_data["country"]        
        key = f"{country}:{json_data['purpose']}:{json_data['entry_point_url']}"
        registry_colstore = db[f"registry_{country}"]
        json_data["_id"] = key
        registry_colstore.find_one_and_replace({"_id": key}, json_data, upsert=True)
        return {"_id": key}
    else:
        abort(500, "Invalid content does not fullfill required format")


#
# This is our simplified version of DataServicesDirectory.findDataServices
# @see https://oots.pages.code.europa.eu/tdd/apidoc/data-services-directory/find-data-services
#
# @param country menas jurisdiction-admin-l2 which in real OOTS is based on "Nomenclature of Territorial Units for Statistics 2024 (NUTS)"
# @param purpose means evicence-type-classification
#
# NUTS Codes see https://code.europa.eu/oots/tdd/tdd_chapters/-/blob/master/OOTS-EDM/codelists/OOTS/NUTS2024-CodeList.gc?ref_type=heads
# (are not used here in the example but in real OOTS)
@app.route("/api/registry/<country>/<purpose>", methods=["GET"])
def find_datastore_for(country, purpose=None):    
    registry_colstore = db[f"registry_{country}"]
    result = registry_colstore.find({"country": country, "purpose": purpose})        
    return list(result)