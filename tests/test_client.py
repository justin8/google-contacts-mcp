from unittest.mock import MagicMock

from google_contacts_mcp.client import ContactsClient


def test_parse_person():
    raw = {
        "resourceName": "people/c12345",
        "etag": "test-etag",
        "names": [{"displayName": "Jane Doe", "givenName": "Jane", "familyName": "Doe"}],
        "phoneNumbers": [{"value": "+1-555-0100", "type": "mobile"}],
        "emailAddresses": [{"value": "jane@example.com", "type": "work"}],
        "addresses": [{
            "formattedValue": "100 Pine St, SF, CA",
            "streetAddress": "100 Pine St",
            "city": "SF",
            "region": "CA",
            "postalCode": "94111",
            "country": "USA",
            "type": "work",
        }],
        "birthdays": [{"date": {"year": 1990, "month": 5, "day": 12}, "text": ""}],
        "organizations": [{"name": "Acme", "title": "Lead", "department": "R&D"}],
        "biographies": [{"value": "Test notes"}],
    }

    parsed = ContactsClient._parse_person(raw)
    assert parsed["resource_name"] == "people/c12345"
    assert parsed["display_name"] == "Jane Doe"
    assert parsed["given_name"] == "Jane"
    assert parsed["family_name"] == "Doe"
    assert parsed["phones"] == [{"value": "+1-555-0100", "type": "mobile"}]
    assert parsed["emails"] == [{"value": "jane@example.com", "type": "work"}]
    assert len(parsed["addresses"]) == 1
    assert parsed["addresses"][0]["city"] == "SF"
    assert parsed["birthdays"] == [{"text": "", "year": 1990, "month": 5, "day": 12}]
    assert parsed["organizations"][0]["name"] == "Acme"
    assert parsed["notes"] == "Test notes"


def test_search_contacts_mock():
    mock_creds = MagicMock()
    mock_service = MagicMock()
    mock_people = MagicMock()
    mock_service.people.return_value = mock_people

    client = ContactsClient(mock_creds)
    client.service = mock_service

    mock_search = MagicMock()
    mock_search.execute.return_value = {
        "results": [
            {
                "person": {
                    "resourceName": "people/c999",
                    "names": [{"displayName": "Alice Smith"}],
                }
            }
        ]
    }
    mock_people.searchContacts.return_value = mock_search

    results = client.search_contacts("Alice")
    assert len(results) == 1
    assert results[0]["display_name"] == "Alice Smith"
    mock_people.searchContacts.assert_called_once()


def test_get_contact_mock():
    mock_creds = MagicMock()
    mock_service = MagicMock()
    mock_people = MagicMock()
    mock_service.people.return_value = mock_people

    client = ContactsClient(mock_creds)
    client.service = mock_service

    mock_get = MagicMock()
    mock_get.execute.return_value = {
        "resourceName": "people/c123",
        "names": [{"displayName": "Bob Builder"}],
    }
    mock_people.get.return_value = mock_get

    contact = client.get_contact("c123")
    assert contact["resource_name"] == "people/c123"
    assert contact["display_name"] == "Bob Builder"
    mock_people.get.assert_called_once_with(
        resourceName="people/c123",
        personFields="names,emailAddresses,phoneNumbers,addresses,birthdays,organizations,biographies,urls",
    )


def test_delete_contact_mock():
    mock_creds = MagicMock()
    mock_service = MagicMock()
    mock_people = MagicMock()
    mock_service.people.return_value = mock_people

    client = ContactsClient(mock_creds)
    client.service = mock_service

    mock_del = MagicMock()
    mock_del.execute.return_value = {}
    mock_people.deleteContact.return_value = mock_del

    deleted = client.delete_contact("people/c123")
    assert deleted is True
    mock_people.deleteContact.assert_called_once_with(resourceName="people/c123")
