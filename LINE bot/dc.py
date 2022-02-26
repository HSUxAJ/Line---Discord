from flask import Flask, request, abort
import discord
from discord.ext import commands
from linebot import LineBotApi, WebhookHandler
from linebot.models import *
from lotify.client import Client
import os
import json
import keep_alive

bot = commands.Bot(command_prefix=';')

line_bot_api = LineBotApi(os.environ['LINEBOT_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['LINEBOT_SECRET'])
discord_bot_token = os.environ['DISCORDBOT_TOKEN']
lotify_token = os.environ['LOTIFY_TOKEN_LineBotTest']
discord_webhook_id = os.environ['DISCORD_WEBHOOK']
message_channel_id = os.environ['MESSAGE_CHANNEL_ID']
lotify = Client()

groups_name = []

groups_token = []

group_id = []

discord_channel_id = []

send = True
channel = 0

@bot.event
async def on_message(message):
    if message.author.bot: return
    global send, channel
    channel = discord_channel_id.index(str(message.channel.id))
    bot_send_message(message)
	#notify_send_message(message)

def bot_send_message(message):
	global channel
	if message.attachments == []:
		line_bot_api.push_message(group_id[channel], TextSendMessage(text=message.content))
	else:
		image_url = str(message.attachments[0])
		image_message = ImageSendMessage(
			original_content_url=image_url,
			preview_image_url=image_url
			)
		line_bot_api.push_message(group_id[channel], image_message)

def notify_send_message(message):
	lotify_message = '\n' + message.content
	lotify.send_message(
		access_token=lotify_token,
		message=lotify_message
	)

keep_alive.keep_alive()
bot.run(discord_bot_token)