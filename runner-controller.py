#!/usr/bin/env python3

import datetime
import github
import pathlib
import random
import subprocess
import sys
import time
import traceback
from config import CLIENT_ID, ORGANISATIONS, POLLING_INTERVAL, PRIVATE_KEY_FILE, RUNNER_DIR, STOPFILE

TOKEN_PERMISSIONS = {"actions": "read", "organization_self_hosted_runners": "write"}


def log(text):
    timestamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    print("{}  {}".format(timestamp, text))


# Read private key
log("Reading private key...")
with open(PRIVATE_KEY_FILE, 'r') as pem_file:
    private_key = pem_file.read()

app_auth = github.Auth.AppAuth(CLIENT_ID, private_key)
github_integration = github.GithubIntegration(auth=app_auth)


github_object_cache = {}
def get_github_for_org(org_name:str) -> github.Github:
    if org_name not in github_object_cache:
        installation = github_integration.get_org_installation(org_name)
        g = github_integration.get_github_for_installation(installation.id, TOKEN_PERMISSIONS)
        github_object_cache["org_name"] = g

    return github_object_cache["org_name"]


def get_runner_registration_token(org_name:str) -> str:
    # This isn't implemented in PyGithub yet so do a 'manual' API call
    g = get_github_for_org(org_name)
    url = "https://api.github.com/orgs/{}/actions/runners/registration-token".format(org_name)
    _, data = g.requester.requestJsonAndCheck("POST", url)
    return data["token"]


def get_orgs_with_queued_jobs() -> list[str]:
    orgs = ORGANISATIONS.copy()
    random.shuffle(orgs)

    orgs_with_queued_jobs = []

    for org in orgs:
        try:
            repos = org["repositories"].copy()
            random.shuffle(repos)

            g = get_github_for_org(org["name"])

            for repo in repos:
                full_name_or_id = "{}/{}".format(org["name"], repo)
                workflow_runs = g.get_repo(full_name_or_id, lazy=True).get_workflow_runs(status="queued")

                if workflow_runs.totalCount > 0:
                    log("Found queued workflow run in repository: {}/{}".format(org["name"], repo))
                    orgs_with_queued_jobs.append(org)
                    break
        except Exception as e:
            log("Caught exception")
            traceback.print_exception(e)
            continue

    return orgs_with_queued_jobs


def unregister_runner() -> None:
    subprocess.check_call(["./config.sh", "remove"], cwd=RUNNER_DIR)


def register_runner(org_name:str, token:str) -> None:
    subprocess.check_call(["./config.sh", "--url", "https://github.com/{}".format(org_name), "--token", token, "--ephemeral", "--unattended"], cwd=RUNNER_DIR)


def run_runner() -> None:
    subprocess.check_call(["./run.sh"], cwd=RUNNER_DIR)


def check_for_stopfile() -> None:
    if STOPFILE is not None:
        if pathlib.Path(STOPFILE).exists():
            log("Stopfile found, exiting...")
            sys.exit()


def main() -> None:
    while True:
        check_for_stopfile()
        log("Polling for queued workflow runs...")
        try:
            orgs_with_queued_jobs = get_orgs_with_queued_jobs()
        except Exception as e:
            orgs_with_queued_jobs = []
            log("Caught exception")
            traceback.print_exception(e)

        if len(orgs_with_queued_jobs) > 0:
            for org in orgs_with_queued_jobs:
                try:
                    check_for_stopfile()
                    log("Registering runner to organisation: {}".format(org["name"]))
                    unregister_runner()
                    registration_token = get_runner_registration_token(org["name"])
                    register_runner(org["name"], registration_token)
                    run_runner()
                    log("Workflow run complete")
                except Exception:
                    log("Caught exception")
                    traceback.print_exception(e)
                    continue
        else:
            log("No queued workflow runs found")

        check_for_stopfile()
        log("Waiting...")
        time.sleep(POLLING_INTERVAL)


try:
    main()
except KeyboardInterrupt:
    pass
