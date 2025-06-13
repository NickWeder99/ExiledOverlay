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

The overlay uses the official PoE OAuth API for account access. Register a
**confidential** application on
[the Path of Exile website](https://www.pathofexile.com/oauth/authorize) to obtain your
**client id** and **client secret**. Set the following environment variables
before running the application:

- `POE_CLIENT_ID` *(required)*
- `POE_CLIENT_SECRET` *(required)*

The provided credentials are cached in `~/.exiledoverlay_credentials.json` after first use so they only need to be set once. During login a browser window will open asking for permission. OAuth tokens are stored in `~/.exiledoverlay_tokens.json` with permissions `600` so only your user can read them.

Launch the overlay and open the **Account** view to initiate the login flow at any time.

Tokens include their expiration time. Use ``poe_auth.ensure_valid_token()`` to
retrieve a usable token, which will automatically refresh it when needed.

Alternatively you can authorize using just your account name. Enter the name in
the **Account** view's input field and the overlay will log in as a *public*
client. Public clients do not require a client secret but have shorter token
lifetimes. The account must be registered as a public OAuth client on the PoE
website or the authorization page will display an ``invalid_client`` error.

### Requesting a token with a refresh token

If you already have a valid ``refresh_token`` you can obtain a new access token
directly using the ``poe_auth.request_token_via_refresh`` helper which performs
a ``POST`` request to ``https://www.pathofexile.com/oauth/token`` with form
encoded parameters::

    client_id=<your id>
    client_secret=<your secret>
    grant_type=refresh_token
    refresh_token=<stored refresh token>

The response contains a new ``access_token`` and ``refresh_token`` among other
fields. The helper automatically stores the returned token on disk with an
``expires_at`` timestamp.

