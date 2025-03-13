# Organisations to register runners for, and repositories in those organisations to check for queued jobs
ORGANISATIONS = [
    {
        "name": "example-org",
        "repositories": [
            "repo1",
            "repo2",
            "repo3",
        ]
    },
]

# Client ID of the GitHub App
CLIENT_ID = "your-client-id"

# File containing a private key for the GitHub App
PRIVATE_KEY_FILE = "downloaded.private-key.pem"

# Directory where actions-runner is installed
RUNNER_DIR = "/tmp/actions-runner"

# If this is too short you could hit the API rate limit
POLLING_INTERVAL = 30.0 #seconds

# Exit cleanly if this file exists
STOPFILE = "stopfile"
