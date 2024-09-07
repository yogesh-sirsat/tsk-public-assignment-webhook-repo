from bson import ObjectId
from flask import Blueprint, jsonify, request
from app.extensions import mongo
from datetime import datetime

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


def get_day_with_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix


def get_formatted_datetime_string(timestamp_str):
    action_time = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ')
    day_with_suffix = get_day_with_suffix(action_time.day)
    rest_of_formatted_time = action_time.strftime('%B %Y - %I:%M %p UTC')
    return f'{day_with_suffix} {rest_of_formatted_time}'


def process_push_action(data):
    event = {
        "request_id": data["head_commit"]["id"],
        "author": data["sender"]["login"],
        "action": "PUSH",
        "from_branch": data["ref"].split("/")[-1],  # e.g. refs/heads/master
        "timestamp": get_formatted_datetime_string(data["head_commit"]["timestamp"]),
    }
    mongo.db.events.insert_one(event)


def process_pull_request_action(data):
    event = {
        "request_id": data["pull_request"]["id"],
        "author": data["sender"]["login"],
        "action": "PULL_REQUEST",
        "from_branch": data["pull_request"]["head"]["ref"],
        "to_branch": data["pull_request"]["base"]["ref"],
        "timestamp": get_formatted_datetime_string(data["pull_request"]["created_at"]),
    }
    mongo.db.events.insert_one(event)


def process_merge_action(data):
    event = {
        "request_id": data["pull_request"]["id"],
        "author": data["sender"]["login"],
        "action": "MERGE",
        "from_branch": data["pull_request"]["head"]["ref"],
        "to_branch": data["pull_request"]["base"]["ref"],
        "timestamp": get_formatted_datetime_string(data["pull_request"]["merged_at"]),
    }
    mongo.db.events.insert_one(event)


@webhook.route('/receiver', methods=["POST"])
def receiver():
    try:
        data = request.json
        action_type = request.headers.get('X-GitHub-Event')
        print(action_type)
        if action_type == "push":
            process_push_action(data)
        elif action_type == "pull_request" and data["action"] == "opened":
            process_pull_request_action(data)
        elif action_type == "pull_request" and data["action"] == "closed" and data["pull_request"]["merged"]:
            process_merge_action(data)

        return {}, 201
    except Exception as e:
        return {"error": str(e)}, 500


@webhook.route('/get-events', methods=["GET"])
def get_events():
    try:
        last_event_id = request.args.get('last_event_id')

        if last_event_id:
            # Fetch events that occurred after the last fetched ObjectId
            events = list(mongo.db.events.find({'_id': {'$gt': ObjectId(last_event_id)}}).sort('_id', -1))
        else:
            events = list(mongo.db.events.find().sort('_id', -1))

        # Convert ObjectId to string for JSON response
        for event in events:
            event['_id'] = str(event['_id'])

        return jsonify(events)
    except Exception as e:
        return {"error": str(e)}, 500
