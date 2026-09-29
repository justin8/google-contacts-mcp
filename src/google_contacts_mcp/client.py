from typing import Any, Dict, List, Optional
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

PERSON_FIELDS = (
    "names,emailAddresses,phoneNumbers,addresses,birthdays,organizations,biographies,urls"
)


class ContactsClient:
    def __init__(self, credentials: Credentials):
        self.service = build("people", "v1", credentials=credentials, cache_discovery=False)

    @staticmethod
    def _parse_person(person: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Google People API person object into a clean dictionary."""
        resource_name = person.get("resourceName", "")
        etag = person.get("etag", "")

        # Names
        names = person.get("names", [])
        display_name = names[0].get("displayName", "") if names else ""
        given_name = names[0].get("givenName", "") if names else ""
        family_name = names[0].get("familyName", "") if names else ""

        # Phones
        phones = []
        for p in person.get("phoneNumbers", []):
            phones.append({
                "value": p.get("value", ""),
                "type": p.get("type", "other"),
            })

        # Emails
        emails = []
        for e in person.get("emailAddresses", []):
            emails.append({
                "value": e.get("value", ""),
                "type": e.get("type", "other"),
            })

        # Addresses
        addresses = []
        for a in person.get("addresses", []):
            addresses.append({
                "formatted": a.get("formattedValue", ""),
                "street": a.get("streetAddress", ""),
                "city": a.get("city", ""),
                "region": a.get("region", ""),
                "postal_code": a.get("postalCode", ""),
                "country": a.get("country", ""),
                "type": a.get("type", "other"),
            })

        # Birthdays
        birthdays = []
        for b in person.get("birthdays", []):
            date_dict = b.get("date", {})
            birthdays.append({
                "text": b.get("text", ""),
                "year": date_dict.get("year"),
                "month": date_dict.get("month"),
                "day": date_dict.get("day"),
            })

        # Organizations / Work
        orgs = []
        for o in person.get("organizations", []):
            orgs.append({
                "name": o.get("name", ""),
                "title": o.get("title", ""),
                "department": o.get("department", ""),
            })

        # Biographies / Notes
        bios = [bio.get("value", "") for bio in person.get("biographies", []) if bio.get("value")]

        return {
            "resource_name": resource_name,
            "etag": etag,
            "display_name": display_name,
            "given_name": given_name,
            "family_name": family_name,
            "phones": phones,
            "emails": emails,
            "addresses": addresses,
            "birthdays": birthdays,
            "organizations": orgs,
            "notes": "\n".join(bios),
        }

    def search_contacts(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search contacts by query string (name, email, phone)."""
        response = self.service.people().searchContacts(
            query=query,
            readMask=PERSON_FIELDS,
            pageSize=min(max_results, 30),
        ).execute()

        results = []
        for match in response.get("results", []):
            person = match.get("person")
            if person:
                results.append(self._parse_person(person))
        return results

    def get_contact(self, resource_name: str) -> Dict[str, Any]:
        """Retrieve full contact details by resourceName (e.g. 'people/c12345')."""
        if not resource_name.startswith("people/"):
            resource_name = f"people/{resource_name}"

        person = self.service.people().get(
            resourceName=resource_name,
            personFields=PERSON_FIELDS,
        ).execute()
        return self._parse_person(person)

    def list_contacts(self, page_size: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
        """List user's contacts with pagination."""
        response = self.service.people().connections().list(
            resourceName="people/me",
            personFields=PERSON_FIELDS,
            pageSize=min(page_size, 100),
            pageToken=page_token,
            sortOrder="LAST_MODIFIED_DESCENDING",
        ).execute()

        connections = [self._parse_person(p) for p in response.get("connections", [])]
        return {
            "contacts": connections,
            "next_page_token": response.get("nextPageToken"),
            "total_people": response.get("totalPeople"),
        }

    def create_contact(
        self,
        given_name: str,
        family_name: Optional[str] = None,
        phone_numbers: Optional[List[Dict[str, str]]] = None,
        email_addresses: Optional[List[Dict[str, str]]] = None,
        addresses: Optional[List[Dict[str, str]]] = None,
        birthday: Optional[Dict[str, int]] = None,
        organization: Optional[str] = None,
        job_title: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new contact in Google Contacts."""
        body: Dict[str, Any] = {
            "names": [{"givenName": given_name, "familyName": family_name or ""}],
        }

        if phone_numbers:
            body["phoneNumbers"] = [
                {"value": p.get("value"), "type": p.get("type", "mobile")}
                for p in phone_numbers
                if p.get("value")
            ]

        if email_addresses:
            body["emailAddresses"] = [
                {"value": e.get("value"), "type": e.get("type", "home")}
                for e in email_addresses
                if e.get("value")
            ]

        if addresses:
            body["addresses"] = [
                {
                    "streetAddress": a.get("street", ""),
                    "city": a.get("city", ""),
                    "region": a.get("region", ""),
                    "postalCode": a.get("postal_code", ""),
                    "country": a.get("country", ""),
                    "type": a.get("type", "home"),
                }
                for a in addresses
            ]

        if birthday:
            b_dict: Dict[str, Any] = {}
            if "year" in birthday:
                b_dict["year"] = birthday["year"]
            if "month" in birthday:
                b_dict["month"] = birthday["month"]
            if "day" in birthday:
                b_dict["day"] = birthday["day"]
            body["birthdays"] = [{"date": b_dict}]

        if organization or job_title:
            body["organizations"] = [{
                "name": organization or "",
                "title": job_title or "",
            }]

        if notes:
            body["biographies"] = [{"value": notes, "contentType": "TEXT_PLAIN"}]

        created = self.service.people().createContact(body=body).execute()
        return self._parse_person(created)

    def update_contact(
        self,
        resource_name: str,
        phone_numbers: Optional[List[Dict[str, str]]] = None,
        email_addresses: Optional[List[Dict[str, str]]] = None,
        addresses: Optional[List[Dict[str, str]]] = None,
        birthday: Optional[Dict[str, int]] = None,
        organization: Optional[str] = None,
        job_title: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update fields on an existing contact."""
        if not resource_name.startswith("people/"):
            resource_name = f"people/{resource_name}"

        # Fetch current record to get etag and existing fields
        current = self.service.people().get(
            resourceName=resource_name,
            personFields=PERSON_FIELDS,
        ).execute()

        body: Dict[str, Any] = {
            "etag": current.get("etag"),
        }
        update_fields = []

        if phone_numbers is not None:
            body["phoneNumbers"] = [
                {"value": p.get("value"), "type": p.get("type", "mobile")}
                for p in phone_numbers
                if p.get("value")
            ]
            update_fields.append("phoneNumbers")

        if email_addresses is not None:
            body["emailAddresses"] = [
                {"value": e.get("value"), "type": e.get("type", "home")}
                for e in email_addresses
                if e.get("value")
            ]
            update_fields.append("emailAddresses")

        if addresses is not None:
            body["addresses"] = [
                {
                    "streetAddress": a.get("street", ""),
                    "city": a.get("city", ""),
                    "region": a.get("region", ""),
                    "postalCode": a.get("postal_code", ""),
                    "country": a.get("country", ""),
                    "type": a.get("type", "home"),
                }
                for a in addresses
            ]
            update_fields.append("addresses")

        if birthday is not None:
            b_dict: Dict[str, Any] = {}
            if "year" in birthday:
                b_dict["year"] = birthday["year"]
            if "month" in birthday:
                b_dict["month"] = birthday["month"]
            if "day" in birthday:
                b_dict["day"] = birthday["day"]
            body["birthdays"] = [{"date": b_dict}]
            update_fields.append("birthdays")

        if organization is not None or job_title is not None:
            body["organizations"] = [{
                "name": organization or "",
                "title": job_title or "",
            }]
            update_fields.append("organizations")

        if notes is not None:
            body["biographies"] = [{"value": notes, "contentType": "TEXT_PLAIN"}]
            update_fields.append("biographies")

        if not update_fields:
            return self._parse_person(current)

        updated = self.service.people().updateContact(
            resourceName=resource_name,
            updatePersonFields=",".join(update_fields),
            body=body,
        ).execute()
        return self._parse_person(updated)

    def delete_contact(self, resource_name: str) -> bool:
        """Delete a contact by resourceName."""
        if not resource_name.startswith("people/"):
            resource_name = f"people/{resource_name}"
        self.service.people().deleteContact(resourceName=resource_name).execute()
        return True
