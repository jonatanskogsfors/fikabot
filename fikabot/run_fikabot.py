#!/usr/bin/env python3

import os

from fikabot import FikaBot


def main():
    bot_id = os.environ.get("BOT_ID")
    slack_bot_token = os.environ.get('SLACK_BOT_TOKEN')

    FikaBot(bot_id, slack_bot_token).do_your_thing()


if __name__ == "__main__":
    main()
