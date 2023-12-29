import logging
import json
import os
import platform
import re
import requests
import yaml

from bson.objectid import ObjectId
from pymongo import MongoClient, HASHED, ASCENDING
from flask import Flask, request, abort, Response
from cerberus import Validator

app = Flask(__name__)
mongo_client = MongoClient("mongodb://root:test1234@backend_db")

# constants
HOSTNAME = os.environ.get("D_HOSTNAME") if "D_HOSTNAME" in os.environ.keys() else platform.node()
PREFIX = os.environ.get("D_PREFIX") if "D_PREFIX" in os.environ.keys() else "u"
CENTRAL_REGISTRY_URL = "http://registry:5000/api/registry"
COUNTRY = os.environ.get("COUNTRY") if "COUNTRY" in os.environ.keys() else "it"
SUPPORTED_PURPOSES = [
    "university.registration",
    "university.graduation",
    "university.deregistration"
]
RE_DOMAIN_PURPOSE = re.compile(r"^(?P<domain>[a-z]+)\.(?P<purpose>[a-z]+)$")

# self registration of the backend system at the central registry 
# automatically at startup of the backend system
for purpose in SUPPORTED_PURPOSES:
    response = requests.post(
        url=CENTRAL_REGISTRY_URL, 
        json={
            "country": COUNTRY,
            "purpose": purpose,
            "entry_point_url": f"http://{HOSTNAME}:5000/api/documentstore",
            "version": 1
        }
    )
    logging.info(f"Registered {purpose}: {response}")


# load the validation configuration for stored documents at startup
def __get_element_from_purpose(purpose:str, element:str) -> str:
    result = RE_DOMAIN_PURPOSE.search(purpose)
    return result.group(element)


def __get_validator_definition_for(country, domain, purpose):
    path = os.path.join(country, domain, f"{purpose}.yml")
    if not os.path.isfile(path):
        raise RuntimeError("document definition for {path} does not exists!")
    with open(path, "r") as f:        
        validation_definition = yaml.safe_load(f)        
    return validation_definition


CONFIG = {
    COUNTRY: {
        domain: {
            __get_element_from_purpose(p, "purpose"): __get_validator_definition_for(COUNTRY, domain, __get_element_from_purpose(p, "purpose"))
            for p in SUPPORTED_PURPOSES
            if p.startswith(f"{domain}.")
        }
        for domain in set([__get_element_from_purpose(p, "domain") for p in SUPPORTED_PURPOSES])        
    }
}


def get_validator_for(country, domain, purpose):    
    if not (
        country in CONFIG.keys() 
        and domain in CONFIG[country].keys()
        and purpose in CONFIG[country][domain].keys()
    ):
        raise RuntimeError("Invalid combination aof country, domain and purpose")
    
    return Validator(CONFIG[country][domain][purpose])


# functions of the REST API of the backend system
@app.route('/api/documentstore/purpose', methods=["GET"])
def get_supported_purposes():
    return SUPPORTED_PURPOSES


@app.route("/api/documentstore/<country>/<full_purpose>/<eid>/responsible", methods=["GET"])
def get_responsibility_for(country, full_purpose, eid):
    if country != COUNTRY:
        abort(400, "Bad Request - country not supported by this server")
    if full_purpose not in SUPPORTED_PURPOSES:
        abort(400, "Bad Request - purpose not supported by this server")

    domain = __get_element_from_purpose(full_purpose, "domain")
    purpose = __get_element_from_purpose(full_purpose, "purpose")
    
    db = mongo_client[f"{domain}_{country}"]
    colstore = db[f"{PREFIX}_{purpose}_store"]

    # Index based search
    result = colstore.count_documents({
        "country": country,
        "purpose": full_purpose,
        "eid": eid
    })
    if result > 0:
        return {
            "country": country,
            "purpose": purpose,
            "eid": eid,
            "responsible": result > 0
        }
    else:
        abort(404, "Not found - not responsible for")


@app.route("/api/documentstore/<country>/<full_purpose>/<eid>/list", methods=["GET"])
def list_documents(country, full_purpose, eid):
    if country != COUNTRY:
        abort(400, "Bad Request - country not supported by this server")
    if full_purpose not in SUPPORTED_PURPOSES:
        abort(400, "Bad Request - purpose not supported by this server")

    domain = __get_element_from_purpose(full_purpose, "domain")
    purpose = __get_element_from_purpose(full_purpose, "purpose")

    db = mongo_client[f"{domain}_{country}"]
    colstore = db[f"{PREFIX}_{purpose}_store"]

    result = list(colstore.find({        
        "country": country,
        "purpose": full_purpose,
        "eid": eid
    }).limit(1000))

    return [
        {
            "_id": f"{item['_id']}",
            "country": country,
            "purpose": full_purpose,
            "eid": item["eid"],
            "signing_authority_defaulttext": item["signing_authority_defaulttext"] if "signing_authority_defaulttext" in item.keys() else "Unbekannt",
            "url": f"http://{HOSTNAME}:5000/api/documentstore/{country}/{full_purpose}/{item['_id']}"
        }
        for item in result
    ]


@app.route("/api/documentstore/<country>/<full_purpose>/<document_id>", methods=["GET"])
def get_document(country, full_purpose, document_id):
    if country != COUNTRY:
        abort(400, "Bad Request - country not supported by this server")
    if full_purpose not in SUPPORTED_PURPOSES:
        abort(400, "Bad Request - purpose not supported by this server")

    domain = __get_element_from_purpose(full_purpose, "domain")
    purpose = __get_element_from_purpose(full_purpose, "purpose")

    db = mongo_client[f"{domain}_{country}"]
    colstore = db[f"{PREFIX}_{purpose}_store"]

    result = colstore.find_one({"_id": ObjectId(document_id)})
    
    if result["country"] == country and result["purpose"] == full_purpose:
        result["_id"] = f"{result['_id']}" # convert ID to string because of JSON serialization, ObjectId is not serializable itself
        return result
    else:
        abort(400, "Bad Request - country or purpose does not match")


@app.route("/api/documentstore/<country>/<full_purpose>", methods=["POST"])
def store_document(country, full_purpose):
    if country != COUNTRY:
        abort(400, "Bad Request - country not supported by this server")
    if full_purpose not in SUPPORTED_PURPOSES:
        abort(400, "Bad Request - purpose not supported by this server")
    
    domain = __get_element_from_purpose(full_purpose, "domain")
    purpose = __get_element_from_purpose(full_purpose, "purpose")

    json_data = json.loads(request.data)
    validator = get_validator_for(country, domain, purpose)
    if not validator.validate(json_data):
        abort(400, f"Bad Request - {validator.errors}")
    
    db = mongo_client[f"{domain}_{country}"]
    colstore = db[f"{PREFIX}_{purpose}_store"]
    info = colstore.insert_one(json_data)

    # if index exist it will not be recreated
    # see https://www.mongodb.com/docs/manual/reference/method/db.collection.createIndex/#behaviors
    colstore.create_index({
        "country": ASCENDING,
        "purpose": ASCENDING,
        "eid": HASHED 
    })

    return Response(response=json.dumps({"_id": f"{info.inserted_id}"}), status=201, content_type="application/json") # 201 = Created