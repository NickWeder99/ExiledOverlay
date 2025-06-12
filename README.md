# ExiledOverlay

This project contains various modules used by an overlay application.

## Running the test suite

The repository uses **pytest** for testing. After installing `pytest` you can
run the tests from the repository root:

```bash
pip install pytest
pytest
```

The tests currently cover the LevelGuide helper module located under `ui.modules.levelguide` and the PoE OAuth helper in `api.poe_auth`.

## Logging into Path of Exile

The overlay uses the official PoE OAuth API for account access. Register an application on
[the Path of Exile website](https://www.pathofexile.com/oauth/authorize) to obtain your
**client id** and, for confidential clients, a **client secret**. Set the following
environment variables before running the application:

- `POE_CLIENT_ID` *(required)*
- `POE_CLIENT_SECRET` *(optional for public clients)*

During login a browser window will open asking for permission. OAuth tokens are stored in `~/.exiledoverlay_tokens.json` with permissions `600` so only your user can read them.

Launch the overlay and open the **Account** view to initiate the login flow at any time.

Tokens include their expiration time. Use ``poe_auth.ensure_valid_token()`` to
retrieve a usable token, which will automatically refresh it when needed.

