from unittest.mock import MagicMock, patch

from google_contacts_mcp.server import auth_status, delete_contact


def test_auth_status():
    status = auth_status()
    assert "authenticated" in status
    assert "credentials_exist" in status
    assert "token_exist" in status or "token_exists" in status


def test_delete_contact_tool():
    with patch("google_contacts_mcp.server._get_client") as mock_get_client:
        mock_client = MagicMock()
        mock_client.delete_contact.return_value = True
        mock_get_client.return_value = mock_client

        res = delete_contact("people/c123")
        assert res == {"deleted": True, "resource_name": "people/c123"}
