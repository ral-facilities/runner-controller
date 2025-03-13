# runner-controller
Polls to find queued workflow jobs and registers a runner to organisations with queued jobs.

## How it works
- Polls repositories for queued workflow runs. The GitHub docs suggest using webhooks but this is not possible behind a firewall.
- Creates a runner registration token for the organisation that owns the repository with the queued job. It is registered for the organisation instead of the repository because the permissions required to register to the repository (administer:write) are too permissive.
- Registers and runs the actions-runner. The `--ephemeral` flag is used so that the runner exits once the job is complete, the runner is also unregistered automatically.
- It uses a GitHub App for permissions. The alternative would be a Personal Access Token but using these is disabled by default for organisations.

## How to set up and run

1. Install actions-runner. Set `RUNNER_DIR` in `config.py`.

2. Create a GitHub App (go to Settings -> Developer settings -> GitHub Apps). It needs the following permissions:
    - Repository permissions: `actions:read`
    - Organisation permissions: `organization_self_hosted_runners:write`

   Make a note of the Client ID and set CLIENT_ID in `config.py`.

3. On the app page, generate a private key. The private key will download automatically. Copy the private key and set `PRIVATE_KEY_FILE` in `config.py`.

4. Install the GitHub App into any organisations that you want to register runners for.

5. Populate `ORGANISATIONS` in `config.py` with the organisations and repositories.

6. Install requirements: `pip install --user -r requirements.txt`

7. Run it: `./runner-controller.py`

8. To exit, either `ctrl-c` or create a file called `stopfile`.
