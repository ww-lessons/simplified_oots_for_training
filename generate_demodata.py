import requests

from random import randint


BASE_URL_BY_COUNTRY = {
    "de": "http://localhost:8081/api/documentstore",
    "cz": "http://localhost:8083/api/documentstore",
}


def insert_content(content:dict):
    if not "country" in content.keys():
        raise RuntimeError("Invalid content, no country")
    if not "purpose" in content.keys():
        raise RuntimeError("Invalid content, no purpose")
    
    country = content["country"]
    purpose = content["purpose"]
    base_url = BASE_URL_BY_COUNTRY[country]
    url = f"{base_url}/{country}/{purpose}"

    response = requests.post(
        url=url,
        json=content
    )

    return response
    

def generate_deregistration(country, eid, authority, universitynumber, period_type):
    return {
        "country": country,
        "purpose": "university.deregistration",
        "eid": eid,
        "signing_authority_defaulttext": authority,
        "universitynumber": universitynumber,
        "registrationnumber": f"{randint(100000, 99999999)}",
        "firstname": f"Max {randint(10, 999)}",
        "surname": "Mustermann",
        "registration": {
            "first_period_year": 2020,
            "first_period_type": period_type,
            "first_period_subject": "Informatik"
        },
        "deregistration": {
            "date_of_deregistration": "2023-12-12",
            "cause_of_deregistration": "success"
        }
    }


def generate_graduation(country, eid, authority, universitynumber):
    grade = f"{randint(1, 3)}.{randint(0, 9)}"
    return {
        "country": country,
        "purpose": "university.graduation",
        "eid": eid,
        "signing_authority_defaulttext": authority,
        "universitynumber": universitynumber,
        "registrationnumber": f"{randint(100000, 99999999)}",
        "firstname": f"Max {randint(10, 999)}",
        "surname": "Mustermann",
        "grade": grade
    }


if __name__ == "__main__":
    # Max Mustermann (ein Abschluss)
    data = generate_graduation(
        country="de", 
        eid="12345678901@id.bund.de",
        authority="Hochschule Hof",
        universitynumber="7530"
    )
    resp = insert_content(data)
    if resp.status_code > 299:
        print(resp.content)

    # Maria Mustermann (zwei Abschlüsse)
    data = generate_graduation(
        country="de", 
        eid="12345678902@id.bund.de",
        authority="OTH Amberg Weiden",
        universitynumber="7550"
    )
    resp = insert_content(data)
    if resp.status_code > 299:
        print(resp.content)
    
    data = generate_graduation(
        country="de", 
        eid="12345678902@id.bund.de",
        authority="OTH Regensburg",
        universitynumber="7260"
    )
    resp = insert_content(data)
    if resp.status_code > 299:
        print(resp.content)