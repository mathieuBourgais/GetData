# Google Health version

`mainGoogleHealth.py` exports heart rate, calories, floors, steps, distance, and
elevation data to CSV files in `data/`. It uses the Google Health API REST v4 and
does not reuse Fitbit OAuth tokens.

## Python environment

From `GetDataApp/`, create and activate a virtual environment, then install the
application dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-google-health.txt
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Google Health setup

1. Enable the Google Health API in a Google Cloud project.
2. Configure the OAuth consent screen and add your account as a test user if
   the app is still in testing.
3. Add the read-only scopes for **Activity and fitness** and **Health metrics
   and measurements**.
4. Create an OAuth client for a local desktop app and provide its client ID and
   client secret in the application. Google Health access may also require
   account linking and approval for restricted health scopes.
5. Run `python mainGoogleHealth.py`, connect, and select a date range.

For current setup and migration requirements, see Google's
[Google Health API setup guide](https://developers.google.com/health/setup) and
[OAuth scopes](https://developers.google.com/health/scopes).
