#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import time
import urllib.parse
from pathlib import Path
from uuid import uuid4

import telegram
from logzero import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
from tinydb import TinyDB, Query

from markdown_handler import MarkdownConverter

data_dir = Path('~', 'messagemerger').expanduser()
data_dir.mkdir(parents=True, exist_ok=True)
db = TinyDB(data_dir / 'db.json')
user_db = Query()

def start(update, context):
    text = 'I am a bot to help you merge messages.\n\nForward a bunch of messages and send /done when you are done.\nAlso use /split command to split a merged message.'
    update.message.reply_text(text)


def send_help(update, context):
    update.message.reply_text("Use /start to get information on how to use me.")


def store_forwarded_message(update, context):
    user_id = update.message.from_user.id
    try:
        first_name = update.message.forward_from.first_name + ': '
    except AttributeError:
        first_name = "HiddenUser: "
    text = first_name + update.message.text_html
    scheme = [text]
    context.user_data.setdefault(user_id, []).extend(scheme)


def split_messages(update, context):
    user_id = update.message.from_user.id
    try:
        current_contents = context.user_data[user_id]
        text = "\n".join(current_contents)
        first_name = text.split(': ')[0]
        text = text.replace(str(first_name) + ': ', '')
        text = re.sub(r'\n+', '\n', text).strip()
        messages = text.splitlines()
        filtered_chars = ['$', '&', '+', ',', ':', ';', '=', '?', '@', '#', '|', '<', '>', '.', '^', '*', '(', ')', '%',
                          '!', '-', '_']
        for part in messages:
            if part in filtered_chars:
                continue
            else:
                update.message.reply_text(part, parse_mode=ParseMode.HTML)
    except IndexError:
        pass
    except KeyError:
        update.message.reply_text("Forward a merged message, then send /split")
    finally:
        context.user_data.clear()


def done(update, context):
    user_id = update.message.from_user.id
    text = context.user_data[user_id]
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("📬 Share", url=https://github.com/Nertflix/button-creator-bot)], [
        InlineKeyboardButton("🗣 Show names", url=https://github.com/Nertflix/button-creator-bot)]])
    update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        
            


def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    token = os.environ.get('BOT_TOKEN')
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", send_help))
    dp.add_handler(CommandHandler("done", done))
    dp.add_handler(CommandHandler("split", split_messages))
    dp.add_handler(MessageHandler(Filters.forwarded & Filters.text, store_forwarded_message))
    dp.add_error_handler(error_callback)
    updater.start_polling()
    logger.info("Ready to rock..!")
    updater.idle()


if __name__ == "__main__":
    main()
