from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)

GERRIT_URL = os.environ["GERRIT_URL"]
GERRIT_BRANCH = os.environ["GERRIT_BRANCH"]
TARGET_URL = os.environ["TARGET_URL"]


def send_webhook(event, payload):
    header = {"Content-Type": "application/json", "X-GitHub-Event": event}
    print("Sending GitHub style webhook to target:")
    print("    target:", TARGET_URL)
    print("    header:", header)
    print("    payload:", payload)
    response = requests.post(TARGET_URL, json=payload, headers=header)
    print(
        "Webhook sent. Status Code:",
        response.status_code,
        ", Response:",
        response.content,
    )


def ref_updated(data):
    update = data["refUpdate"]
    url = GERRIT_URL + "/" + update["project"] + ".git"
    return {
        "ref": update["refName"],
        "after": update["newRev"],
        "repository": {
            "ssh_url": url,
            "html_url": url,
            "git_url": "",
            "clone_url": "",
        },
        "pusher": {"name": data["submitter"]["username"]},
    }


def patchset_created(data):
    change = data["change"]
    return {
        "repository": {
            "ssh_url": GERRIT_URL + "/" + change["project"] + ".git",
            "html_url": "",
            "git_url": "",
            "clone_url": "",
        },
        "pull_request": {
            "base": {"ref": change["branch"]},
            "head": {"sha": data["patchSet"]["revision"]},
        },
        "number": change[
            "number"
        ],  # won't work as refs/pull/<number>/head is hardcoded
    }


gerrit_to_github = {
    "ref-updated": {"event": "push", "translation": ref_updated},
    #    "patchset_created": {"event": "some", "translation": patchset_created},
}


@app.route("/", methods=["POST"])
def hook():
    print("Received webhook from Gerrit: " + str(request.data))
    data = json.loads(request.data)
    event_type = data["type"]

    if event_type in gerrit_to_github:
        event_handler = gerrit_to_github[event_type]
        event = event_handler["event"]
        payload = event_handler["translation"](data)
        send_webhook(event, payload)
    else:
        print("Unhandled event type: " + event_type)

    return "Success"


if __name__ == "__main__":
    app.run()
