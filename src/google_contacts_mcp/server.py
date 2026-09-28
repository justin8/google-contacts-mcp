import argparse
import sys
from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer

from .auth import get_credentials, get_credentials_path, get_token_path, run_auth_flow
from .client import ContactsClient

server = MCPServer(
    name="google-contacts",
    instructions="MCP Server providing secure access to Google Contacts via the official Google People API.",
)


def _get_client() -> ContactsClient:
    creds = get_credentials()
    if not creds:
        token_file = get_token_path()
        creds_file = get_credentials_path()
        raise RuntimeError(
            f"Google Contacts is not authenticated.\n"
            f"Please ensure '{creds_file}' exists and run 'google-contacts-mcp --auth' "
            f"in your terminal to complete login. Token will be saved to '{token_file}'."
        )
    return ContactsClient(creds)


@server.tool()
def auth_status() -> Dict[str, Any]:
    """Check the current authentication status of Google Contacts."""
    creds = get_credentials()
    creds_path = get_credentials_path()
    token_path = get_token_path()

    return {
        "authenticated": creds is not None and creds.valid,
        "credentials_path": str(creds_path),
        "credentials_exist": creds_path.exists(),
        "token_path": str(token_path),
        "token_exists": token_path.exists(),
    }


@server.tool()
def search_contacts(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Search Google Contacts by name, email, or phone number.
    
    Args:
        query: Name, email address, or keyword to search for.
        max_results: Maximum number of contacts to return (default 10).
    """
    client = _get_client()
    return client.search_contacts(query=query, max_results=max_results)


@server.tool()
def get_contact(resource_name: str) -> Dict[str, Any]:
    """Get complete contact details (phone numbers, addresses, birthdays, emails, notes).
    
    Args:
        resource_name: The Google Contact resource name (e.g. 'people/c1234567890' or 'c1234567890').
    """
    client = _get_client()
    return client.get_contact(resource_name=resource_name)


@server.tool()
def list_contacts(page_size: int = 50, page_token: Optional[str] = None) -> Dict[str, Any]:
    """List Google Contacts with pagination.
    
    Args:
        page_size: Number of contacts per page (max 100).
        page_token: Next page token from a previous call.
    """
    client = _get_client()
    return client.list_contacts(page_size=page_size, page_token=page_token)


@server.tool()
def create_contact(
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
    """Create a new contact in Google Contacts.
    
    Args:
        given_name: First name.
        family_name: Last name.
        phone_numbers: List of dicts, e.g. [{"value": "+1-555-0199", "type": "mobile"}].
        email_addresses: List of dicts, e.g. [{"value": "jane@example.com", "type": "work"}].
        addresses: List of dicts, e.g. [{"street": "123 Main St", "city": "Seattle", "region": "WA", "postal_code": "98101", "country": "USA", "type": "home"}].
        birthday: Dict with keys 'year', 'month', 'day' (e.g. {"month": 5, "day": 12}).
        organization: Company or organization name.
        job_title: Professional title.
        notes: Biography / general contact notes.
    """
    client = _get_client()
    return client.create_contact(
        given_name=given_name,
        family_name=family_name,
        phone_numbers=phone_numbers,
        email_addresses=email_addresses,
        addresses=addresses,
        birthday=birthday,
        organization=organization,
        job_title=job_title,
        notes=notes,
    )


@server.tool()
def update_contact(
    resource_name: str,
    phone_numbers: Optional[List[Dict[str, str]]] = None,
    email_addresses: Optional[List[Dict[str, str]]] = None,
    addresses: Optional[List[Dict[str, str]]] = None,
    birthday: Optional[Dict[str, int]] = None,
    organization: Optional[str] = None,
    job_title: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Update fields on an existing Google Contact.
    
    Args:
        resource_name: Contact ID (e.g. 'people/c1234567890').
        phone_numbers: New list of phone numbers.
        email_addresses: New list of emails.
        addresses: New list of physical addresses.
        birthday: Dict with keys 'year', 'month', 'day'.
        organization: Company or organization name.
        job_title: Professional title.
        notes: Contact notes.
    """
    client = _get_client()
    return client.update_contact(
        resource_name=resource_name,
        phone_numbers=phone_numbers,
        email_addresses=email_addresses,
        addresses=addresses,
        birthday=birthday,
        organization=organization,
        job_title=job_title,
        notes=notes,
    )


def main():
    parser = argparse.ArgumentParser(description="Google Contacts MCP Server")
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Run interactive OAuth consent flow in your browser to log in",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether valid credentials and tokens exist",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8085,
        help="Local port for OAuth redirect callback (default 8085)",
    )

    args = parser.parse_args()

    if args.auth:
        print("Starting Google OAuth consent flow...")
        creds = run_auth_flow(port=args.port)
        print(f"Successfully authenticated! Tokens saved to {get_token_path()}")
        sys.exit(0)

    if args.check:
        status = auth_status()
        print(f"Auth Status: {status}")
        sys.exit(0 if status["authenticated"] else 1)

    # Run as MCP server over stdio
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
