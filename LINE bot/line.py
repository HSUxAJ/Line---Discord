from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import requests
import os
import json

app = Flask(__name__)

groups_name = []

discord_webhook = []

choose = 8

line_bot_api = LineBotApi(os.environ['LINEBOT_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINEBOT_SECRET'])

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def create_request_data(event, text=None) -> dict:
	group_id = event.source.group_id
	user_id = event.source.user_id
	profile = line_bot_api.get_group_member_profile(group_id, user_id)
	headers = {"content-type": "application/json; charset=UTF-8",'Authorization':'Bearer {}'.format(os.environ['LINEBOT_ACCESS_TOKEN'])}
	url = 'https://api.line.me/v2/bot/group/' + group_id + '/summary'
	response = requests.get(url, headers=headers)
	response = response.json()
	g_name = response['groupName']
	global choose
	choose = groups_name.index(g_name)
	request_data = {
        "content":text,
        "username":profile.display_name,
        "avatar_url":profile.picture_url
    }
	return request_data

def get_binary_data(event) -> str:
    content = line_bot_api.get_message_content(event.message.id)
    file = b""
    for i in content.iter_content():
        file += i
    return file
	
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	global choose
	request_data = create_request_data(event, event.message.text)
	requests.post(url=discord_webhook[choose], data=request_data)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
	global choose
	request_data = create_request_data(event)
	file = get_binary_data(event)
	requests.post(url=discord_webhook[choose], data=request_data, files={'Media.jpg':file})

@handler.add(MessageEvent, message=VideoMessage)
def handle_video(event):
	global choose
	request_data = create_request_data(event)
	file = get_binary_data(event)
	requests.post(url=discord_webhook[choose], data=request_data, files={'Media.mp4':file})

@handler.add(MessageEvent, message=FileMessage)
def handle_file(event):
	global choose
	request_data = create_request_data(event)
	file_name = event.message.file_name
	file = get_binary_data(event)
	requests.post(url=discord_webhook[choose], data=request_data, files={file_name:file})


app.run(host='0.0.0.0', port=8080)