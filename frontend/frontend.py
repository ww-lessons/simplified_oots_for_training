import json
import requests
import aiohttp
import asyncio
import logging

from flask import Flask, send_file, abort, request

app = Flask(
    __name__, 
    static_folder="static", 
    template_folder="templates"
)

REGISTRY_URL = "http://registry:5000/api/registry"
SUPPORTED_COUNTRIES = {
    "de": "Deutschland",
    "cz": "Česká republika"
}
SUPPORTED_PURPOSES = {
    "university.registration": "Immatrikulationsbescheinigung",
    "university.graduation": "Studienabschluss",
    "university.deregistration": "Exmatrikulationsbescheinigung"
}

# delivery url of the one page app
@app.route('/', methods=["GET"])
def get_index():
    return send_file("templates/index.html")


# Webapi for one page app
@app.route("/api/countries", methods=["GET"])
def get_countries():
    return SUPPORTED_COUNTRIES


# While EvidenceBroker 
# @see https://oots.pages.code.europa.eu/tdd/apidoc/evidence-broker
# is almost completely left out in this example,
# this is our minimal replacement for Evidence Type Lookup Service.
# @see https://oots.pages.code.europa.eu/tdd/apidoc/evidence-broker/get-evidence-types
#
# (The upcoming samples will go closer and closer to real OOTS conformance)
@app.route("/api/purposes", methods=["GET"])
def get_purposes():
    return SUPPORTED_PURPOSES


@app.route("/api/find/<country>/<purpose>/<eid>", methods=["GET"])
def find_documents_per_eid(country, purpose, eid):
    servers = __find_relevant_servers(country, purpose)
    search_results = asyncio.run(
        __find_documents_async_all(country, purpose, eid, servers)
    )    
    return search_results


@app.route("/api/document", methods=["GET"])
def get_document():
    document_url = request.args.get("url")
    document = requests.get(document_url, timeout=1000).json()

    if not document["country"] in SUPPORTED_COUNTRIES.keys():
        abort(400, "Invalid request, unsupported country")
    if not document["purpose"] in SUPPORTED_PURPOSES.keys():
        abort(400, "Invalid request, unsupported purpose")

    return document


# helper functions for the above web api
def __find_relevant_servers(country, purpose):
    if not country in SUPPORTED_COUNTRIES.keys():
        abort(400, "Invalid request, unsupported country")
    if not purpose in SUPPORTED_PURPOSES.keys():
        abort(400, "Invalid request, unsupported purpose")

    url = f"{REGISTRY_URL}/{country}/{purpose}"
    result = requests.get(url)
    return result.json()


async def __find_documents_async(session, country, purpose, eid, entry_point_url):
    url = f"{entry_point_url}/{country}/{purpose}/{eid}/list"
    async with session.get(url) as response:
        return await response.json()


# helper for async mass lockup for documents in multiple repositories
async def __find_documents_async_all(country, purpose, eid, servers):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for server in servers:
            tasks.append(asyncio.ensure_future(__find_documents_async(session, country, purpose, eid, server["entry_point_url"])))
        results = await asyncio.gather(*tasks)        
        result = []
        for part in results:
            result.extend(part)
        return result

