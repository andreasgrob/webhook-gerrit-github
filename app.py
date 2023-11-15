from flask import Flask, request
import json
import requests

app = Flask(__name__)


@app.route("/", methods=["POST"])
def hook():
    print("Received webhook from Gerrit: " + str(request.data))
    data = json.loads(request.data)
    eventType = data["type"]

    if eventType == "ref-updated":
        update = data["refUpdate"]
        payload = {
            "ref": update["refName"],
            "after": update["newRev"],
            "repository": {
                "ssh_url": "ssh://admin@gerrit-gerrit-service.gerrit:29418/"
                + update["project"]
                + ".git",
                "html_url": "",
                "git_url": "",
                "clone_url": "",
            },
        }
        url = "https://cjoc.eks.agrob.core.pscbdemos.com/casc-retriever/retriever-github-webhook"
        header = {"Content-Type": "application/json", "X-GitHub-Event": "push"}
        print("Sending GitHub style webhook to CasC Retriever:")
        print("    target: " + url)
        print("    header: " + str(header))
        print("    payload: " + str(payload))
        response = requests.post(url, json=payload, headers=header)
        print(
            "Webhook sent. Status Code:",
            response.status_code,
            ", Response:",
            response.content,
        )
    else:
        print("Unhandled event type: " + eventType)

    return "Success"


if __name__ == "__main__":
    app.run()
