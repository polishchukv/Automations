# Import necessary modules
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, Response
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter
from slack_sdk.errors import SlackApiError
from threading import Thread
import json

# Load Environment Variables
# This is done to keep sensitive data like API keys out of the code
env_path = Path(".") / "Rotation Bot" / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize Flask and Slack client
# Flask is used to create a web server that Slack can send events to
# The Slack client is used to interact with the Slack API
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)
client = WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

# Define the RotationBot class
class RotationBot:
    def __init__(self, client):
        self.client = client
        self.schedule = self.load_schedule()
        # Initialize a background scheduler
        # This is used to schedule tasks to run at certain times
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.post_rotation_update, 'cron', day_of_week='mon', hour=9, minute=0)
        self.scheduler.start()

    def load_schedule(self):
        # Load your rotation schedule from a JSON file or other source
        with open('schedule.json') as f:
            return json.load(f)

    def get_channel_id(self, channel_name):
        # Get the ID of a channel by its name
        # This is necessary because the Slack API uses channel IDs, not names
        try:
            response = self.client.conversations_list(limit=1000, types='public_channel,private_channel')
            for channel in response['channels']:
                if channel['name'] == channel_name:
                    return channel['id']
        except SlackApiError as e:
            self.handle_api_error(e)
        return None

    def get_channel_members(self, channel_id):
        # Get the members of a channel by its ID
        # This is used to send messages to all members of a channel
        try:
            response = self.client.conversations_members(channel=channel_id)
            return response['members']
        except SlackApiError as e:
            self.handle_api_error(e)
        return []

    def post_message(self, channel, text):
        # Post a message to a channel
        # This is used to send updates and reminders to the channel
        try:
            self.client.chat_postMessage(channel=channel, text=text)
        except SlackApiError as e:
            self.handle_api_error(e)

    def post_rotation_update(self):
        # Post a rotation update to the channel
        # This is scheduled to run every Monday at 9:00
        channel_id = self.get_channel_id('paramount-infosec-vm-vlad')
        if not channel_id:
            return

        members = self.get_channel_members(channel_id)
        if not members:
            return

        messages = []
        for day, user_id in self.schedule.items():
            user_info = client.users_info(user=user_id)
            user_name = user_info['user']['name']
            messages.append(f"- {day}: @{user_name}")

        self.post_message(channel_id, "\n".join(messages))

        # Send DM to today's user
        current_day = time.strftime("%A")
        if current_day in self.schedule:
            user_id = self.schedule[current_day]
            dm_channel = self.client.conversations_open(users=user_id)['channel']['id']
            self.post_message(dm_channel, f"Reminder: It's your turn for the P0 rotation update.")

    def handle_api_error(self, error):
        # Handle API errors
        # If the error is a rate limit error, wait for the specified amount of time
        # Otherwise, print the error
        if error.response["error"] == "ratelimited":
            delay = int(error.response.headers['Retry-After'])
            time.sleep(delay)
        else:
            print(f"Slack API error: {error}")

# Define routes for the Flask app
# These are endpoints that Slack can send events to
@app.route('/test-action', methods=['POST'])
def test_action():
    # Handle the /test-action command
    # If the user is *assignee*, send a message saying they don't have permission
    # Otherwise, send a message saying the command works
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')

    user_info = client.users_info(user=user_id)
    real_name = user_info['user']['real_name']

    if user_id == 'U05CHR5EFMM':
        client.chat_postMessage(channel=channel_id, text=f"{real_name} I'm bout to kick you from this channel, who gave you permission to run commands?")
    else:
        client.chat_postMessage(channel=channel_id, text=f"Wow {real_name}, /test-action works!")

    return Response(), 200

@app.route('/list-users', methods=['POST'])
def message():
    # Handle the /list-users command
    # This command lists all users in the 'paramount-infosec-vm-vlad' channel
    def process_request():
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        bot = RotationBot(client)
        channel_id = bot.get_channel_id('paramount-infosec-vm-vlad')

        if channel_id is None:
            print("[/list-users] Channel not found")
            return

        result = client.conversations_members(channel=channel_id)
        member_ids = result['members']
        for member_id in member_ids:
            user_info = client.users_info(user=member_id)
            if not (user_info['user'].get('is_bot') or user_info['user'].get('is_app_user')):
                print(user_info['user']['real_name'] + " - " + user_info['user']['id'])
                client.chat_postMessage(channel=channel_id, text=user_info['user']['real_name'] + " - " + user_info['user']['id'])

    Thread(target=process_request).start()
    return Response(), 200

@app.route('/slack/events', methods=['POST'])
def slack_events():
    # Handle events from Slack
    # If the event is a challenge, return the challenge value
    # Otherwise, return a 200 status code
    data = request.get_json()
    if "challenge" in data:
        challenge = data["challenge"]
        return Response(challenge), 200
    else:
        return Response(), 200

# Run the Flask app if the script is run directly
if __name__ == "__main__":
    app.run(debug=True)