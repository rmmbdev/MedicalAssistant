from time import sleep

from celery import Celery
from celery.contrib.abortable import AbortableTask
from client_manipulator import BotHandler
import json
from environs import Env

env = Env()
env.read_env()

TEL_CLIENT_BOT_TOKEN = env.str("TEL_CLIENT_BOT_TOKEN")
bot_handler = BotHandler(TEL_CLIENT_BOT_TOKEN)

app = Celery('tasks', broker='amqp://localhost', backend="redis://localhost")


def save_image():
    print("Image Saved!")


@app.task(bind=True, base=AbortableTask)
def breast_cancer_detection(self, chat_id, message):
    save_image()

    message - "Process finished!"
    if not self.is_aborted():
        resp = bot_handler.send_message(chat_id, message)
        print(resp.text)
