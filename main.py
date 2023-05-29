#!/usr/bin/env python

import datetime
import json
import os
import sys
from datetime import datetime
from time import sleep

from tasks import app

import telegram
from emoji import emojize
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    filters,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from yachalk import chalk
from tasks import breast_cancer_detection
from environs import Env

# region const definitions

env = Env()
env.read_env()

TEL_CLIENT_BOT_TOKEN = env.str("TEL_CLIENT_BOT_TOKEN")

START, CHOOSING, HELP, PHOTO, WAIT_RESULT = range(5)

with open("locale.json", encoding='utf-8', mode='r') as f:
    locale = json.load(f)

bot_language = "fa"
date_format = '%Y-%m-%d %H:%M:%S'
date_format_for_time_stamp = '%Y-%m-%d %H-%M'

main_markup = ReplyKeyboardMarkup(
    [
        ['{} {}'.format(locale["breast_cancer_label"], emojize(':stethoscope:'))],
        ['{} {}'.format(locale["help_label"], emojize(':scroll:'))],
        ['{} {}'.format(locale["stop"], emojize(':cross_mark:'))],
    ],
    one_time_keyboard=False,
    resize_keyboard=True
)

cancel_keyboard = [['{} {}'.format(locale["cancel_label"], emojize(':cross_mark:'))]]
cancel_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=False, resize_keyboard=True)

return_keyboard = [['{} {}'.format(locale["return_label"], emojize(':right_arrow_curving_left:'))]]
return_markup = ReplyKeyboardMarkup(return_keyboard, one_time_keyboard=False, resize_keyboard=True)

save_keyboard = [['{} {}'.format(locale["save"], emojize(':check_mark:'))]]
save_markup = ReplyKeyboardMarkup(save_keyboard, one_time_keyboard=True, resize_keyboard=True)

start_keyboard = [['{} {}'.format(locale["start_label"], emojize(':check_mark:'))]]
start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard=True, resize_keyboard=True)

actions = {
    "Breast Cancer 🩺": (breast_cancer_detection, locale["breast_cancer_send_file_text"]),
}

bot = telegram.Bot(token=TEL_CLIENT_BOT_TOKEN)


# endregion


# region utils


# endregion

# region state definitions
async def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation"""
    user = update.message.from_user
    print(f"user_id {user.id} started!")
    print(f"username {user.username} started!")
    print(f"first name {user.first_name} started!")
    print(f"last name {user.last_name} started!")
    sys.stdout.flush()

    await update.message.reply_text(
        locale["greeting"].format(f"{emojize(':x-ray:')}", f"{emojize(':handshake:')}", ),
    )
    await update.message.reply_text(
        locale["return_text"],
        reply_markup=main_markup
    )
    return CHOOSING


async def bot_help(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        locale["help_text"],
        reply_markup=main_markup
    )
    return CHOOSING


async def photo(update: Update, context: CallbackContext) -> int:
    text = actions[context.match.string][1]

    await update.message.reply_text(
        text,
        reply_markup=return_markup
    )
    return PHOTO


async def choose_option(update: Update, context: CallbackContext) -> int:
    if context.user_data["task_id"]:
        action = actions[context.match.string][0]
        action.AsyncResult(context.user_data["task_id"]).abort()

    await update.message.reply_text(
        locale["return_text"],
        reply_markup=main_markup
    )
    return CHOOSING


async def process_image(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        locale["process_image_intro"],
    )
    await update.message.reply_text(
        locale["process_image_attention"],
        reply_markup=cancel_markup
    )

    task = breast_cancer_detection.delay(update.message.chat_id)
    context.user_data["task_id"] = task.task_id

    return WAIT_RESULT


async def stop(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        locale["stop_title"],
        reply_markup=start_markup
    )
    user = update.message.from_user
    print(f"user_id {user.id} stopped!")
    sys.stdout.flush()
    return ConversationHandler.END


# endregion


def main() -> None:
    application = Application.builder().token(TEL_CLIENT_BOT_TOKEN).build()

    # Turing Machine
    # every state should be abstract
    # every action is defined as a function
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(
                filters.TEXT & filters.Regex(f'^{locale["start_label"]}(.)*$'),
                start
            ),
        ],
        states={
            CHOOSING: [
                CommandHandler('start', start),
                MessageHandler(
                    filters.TEXT & filters.Regex(f'^{locale["help_label"]}(.)*$'),
                    bot_help
                ),
                MessageHandler(
                    filters.TEXT & filters.Regex(f'^{locale["breast_cancer_label"]}(.)*$'),
                    photo
                ),
            ],
            PHOTO: [
                CommandHandler('start', start),
                MessageHandler(
                    filters.TEXT & filters.Regex(f'^{locale["return_label"]}(.)*$'),
                    choose_option
                ),
                MessageHandler(
                    filters.PHOTO,
                    process_image
                ),
            ],
            WAIT_RESULT: [
                CommandHandler('start', start),
                MessageHandler(
                    filters.TEXT & filters.Regex(f'^{locale["cancel_label"]}(.)*$'),
                    choose_option
                ),
            ]

        },
        fallbacks=[
            CommandHandler('stop', stop),
            MessageHandler(filters.Regex(f'^{locale["stop"]}(.)*$'), stop)
        ],
    )

    application.add_handler(conv_handler)

    # Start the Bot
    print(chalk.yellow("App started..."))
    sys.stdout.flush()
    application.run_polling()


if __name__ == '__main__':
    main()
