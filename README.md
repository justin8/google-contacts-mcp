# Google Contacts MCP Server

A clean, transparent, and secure [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for **Google Contacts**, built in Python using official Google and MCP SDKs.

Designed for AI assistants (Antigravity, Claude, Cursor, etc.) to securely query and manage contact details—such as phone numbers, physical addresses, birthdays, and organizations—without duplicating PII across personal notes and markdown vaults.

---

## Features

- **Direct & Secure**: Uses the official Google People API (`google-api-python-client`) and official MCP Python SDK (`mcp`).
- **No Third-Party Middlemen**: No telemetry, no hosted cloud proxies, and no obscure packages. Credentials and tokens stay strictly local on your machine.
- **Tools Included**:
  - `auth_status`: Check connection and token validity.
  - `search_contacts`: Search contacts by name, email, or phone.
  - `get_contact`: Fetch phone numbers, addresses, birthdays, emails, and notes for a contact.
  - `list_contacts`: Paginated listing of your contact network.
  - `create_contact`: Add new contacts directly to Google Contacts.
  - `update_contact`: Modify phone numbers, addresses, birthdays, or details.

---

## 1. Google Cloud Setup (One-Time)

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g. `personal-contacts-mcp`).
3. Enable the **People API**:
   - Go to **APIs & Services > Library**.
   - Search for **Google People API** and click **Enable**.
4. Configure the **OAuth Consent Screen**:
   - Go to **APIs & Services > OAuth consent screen**.
   - Choose **External** user type.
   - Fill in an App name (e.g. `Contacts MCP`) and your email address.
   - Under **Audience > Test users**, add your personal Google email address.
5. Create OAuth Credentials:
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth client ID**.
   - Select **Desktop app**.
   - Name it (e.g. `Contacts MCP Client`) and click **Create**.
6. Download Client Secrets:
   - Download the JSON credentials file.
   - Save it to `~/.config/google-contacts-mcp/credentials.json`:
     ```bash
     mkdir -p ~/.config/google-contacts-mcp
     mv ~/Downloads/client_secret_*.json ~/.config/google-contacts-mcp/credentials.json
     chmod 600 ~/.config/google-contacts-mcp/credentials.json
     ```

---

## 2. Authentication

Run the one-time interactive OAuth login:

```bash
uv run --directory ~/src/google-contacts-mcp google-contacts-mcp --auth
```

A browser window will open asking you to sign in with your Google account and grant contact permissions.
Once completed, your refresh token will be saved to `~/.config/google-contacts-mcp/token.json` (with `0600` permissions).

Verify your authentication status anytime:

```bash
uv run --directory ~/src/google-contacts-mcp google-contacts-mcp --check
```

---

## 3. MCP Configuration

### For Antigravity
Add the server to `~/.gemini/config/mcp_config.json`:

```json
{
  "mcpServers": {
    "google-contacts": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/justin/src/google-contacts-mcp",
        "google-contacts-mcp"
      ]
    }
  }
}
```

### For Claude Desktop / Cursor
In your client's MCP configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "google-contacts": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/justin/src/google-contacts-mcp",
        "google-contacts-mcp"
      ]
    }
  }
}
```

---

## 4. Environment Variables (Optional)

| Variable | Default | Description |
| :--- | :--- | :--- |
| `GOOGLE_CONTACTS_CONFIG_DIR` | `~/.config/google-contacts-mcp` | Base directory for credentials and tokens |
| `GOOGLE_CONTACTS_CREDENTIALS` | `<CONFIG_DIR>/credentials.json` | Path to Google OAuth client secret JSON |
| `GOOGLE_CONTACTS_TOKEN` | `<CONFIG_DIR>/token.json` | Path to saved token file |

---

## 5. Development

Install dependencies locally with `uv`:

```bash
cd ~/src/google-contacts-mcp
uv sync
```

Run tests / linting:

```bash
uv run pytest
```

---

## License

MIT
