import requests

def test_insert_document():
    print("test_insert_document() - 1")
    document = {
        "country": "de",
        "purpose": "university.deregistration",
        "eid": "12345678901@id.bund.de",
        "signing_authority_defaulttext": "OTH Regensburg",
        "universitynumber": "7260",
        "registrationnumber": "12345678",
        "firstname": "Max",
        "surname": "Mustermann",
        "registration": {
            "first_period_year": 2020,
            "first_period_type": "Sommersemester",
            "first_period_subject": "Informatik"
        },
        "deregistration": {
            "date_of_deregistration": "2023-12-12",
            "cause_of_deregistration": "success"
        }
    }
    response = requests.post(
        url="http://localhost:8081/api/documentstore/de/university.deregistration",
        json=document
    )
    print(response.status_code)
    print(response.text)
    print("-----\n")

    print("test_insert_document() - 2")
    document = {
        "country": "de",
        "purpose": "university.deregistration",
        "eid": "12345678902@id.bund.de",
        "signing_authority_defaulttext": "OTH Amberg-Weiden",
        "universitynumber": "7550",
        "registrationnumber": "12345679",
        "firstname": "Max",
        "surname": "Mustermann",
        "registration": {
            "first_period_year": 2021,
            "first_period_type": "Sommersemester",
            "first_period_subject": "Betriebswirtschaft"
        },
        "deregistration": {
            "date_of_deregistration": "2023-12-13",
            "cause_of_deregistration": "success"
        }
    }
    response = requests.post(
        url="http://localhost:8084/api/documentstore/de/university.deregistration",
        json=document
    )
    print(response.status_code)
    print(response.text)
    print("-----\n")


if __name__ == "__main__":
    test_insert_document()