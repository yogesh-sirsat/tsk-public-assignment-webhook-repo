from bson import ObjectId
from flask import Blueprint, jsonify, request
from app.extensions import mongo
from datetime import datetime, timedelta
import pytz

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


def get_day_with_suffix(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix


def get_formatted_datetime_string(timestamp_str):
    if timestamp_str.endswith('Z'):
        timestamp_str = timestamp_str[:-1] + '+00:00'

    action_time = datetime.fromisoformat(timestamp_str)
    action_time = action_time.astimezone(pytz.UTC)
    day_with_suffix = get_day_with_suffix(action_time.day)
    rest_of_formatted_time = action_time.strftime('%B %Y - %I:%M %p UTC')

    return f'{day_with_suffix} {rest_of_formatted_time}'


def process_pull_request_action(data, is_merged=False):
    event = {
        "request_id": data["pull_request"]["id"],
        "author": data["sender"]["login"],
        "action": "PULL_REQUEST",
        "from_branch": data["pull_request"]["head"]["ref"],
        "to_branch": data["pull_request"]["base"]["ref"],
        "timestamp": data["pull_request"]["created_at"],
    }
    if is_merged:
        event["action"] = "MERGE"
        event["timestamp"] = data["pull_request"]["merged_at"]
    return event


@webhook.route('/receiver', methods=["POST"])
def receiver():
    try:
        data = request.json
        action_type = request.headers.get('X-GitHub-Event')
        event = None
        if action_type == "push":
            event = {
                "request_id": data["head_commit"]["id"],
                "author": data["sender"]["login"],
                "action": "PUSH",
                "to_branch": data["ref"].split("/")[-1],  # e.g. refs/heads/master
                "timestamp": data["head_commit"]["timestamp"],
            }
        elif action_type == "pull_request":
            if data["action"] == "opened":
                event = process_pull_request_action(data)
            elif data["action"] == "closed" and data["pull_request"]["merged"]:
                event = process_pull_request_action(data, is_merged=True)

        if event:
            event["timestamp"] = get_formatted_datetime_string(event["timestamp"])
            mongo.db.events.insert_one(event)
        return {}, 201
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500


@webhook.route('/get-events', methods=["GET"])
def get_events():
    try:
        last_event_id = request.args.get('last_event_id')

        # To get events from the last 15 seconds, we need to turn datetime into ObjectId
        fifteen_seconds_ago = datetime.utcnow() - timedelta(seconds=15)
        fifteen_seconds_ago_object_id = ObjectId.from_datetime(fifteen_seconds_ago)

        query = {"_id": {"$gt": fifteen_seconds_ago_object_id}}
        if last_event_id:
            query = {
                "$and": [
                    {"_id": {"$gt": ObjectId(last_event_id)}},
                    query
                ]
            }

        # Fetch events in latest first order
        events = list(mongo.db.events.find(query).sort('_id', -1))

        # Convert ObjectId to string for JSON response
        for event in events:
            event['_id'] = str(event['_id'])

        return jsonify(events)
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500
