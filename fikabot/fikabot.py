import datetime
import json
import pathlib
import random
import re
import time
import typing

import slackclient

import fika


class FikaBot:
    def __init__(self, bot_id: str, slack_bot_token, read_delay=1,
                 config_path: pathlib.Path = None):

        self.bot_id = bot_id

        if config_path is None:
            config_path = pathlib.Path(__file__).parent / 'configuration.json'
        self._config_path = config_path  # type: pathlib.Path

        self._read_delay = read_delay  # int
        self._fika_breaks = []  # type: typing.List[fika.Fika]
        self._fika_channel = None
        self._fika_patterns = []  # type: typing.List[typing.re.Pattern]

        self._register_configuration()

        self._slack_client = slackclient.SlackClient(slack_bot_token)

    @property
    def at_bot(self):
        return "<@{}>".format(self.bot_id)

    def do_your_thing(self):
        if self._slack_client.rtm_connect():
            print("{} is connected and running!".format(self.at_bot))
            while True:
                self._take_a_look_at_the_fika_situation()
                self._encourage_all_fika_mentions()
                time.sleep(self._read_delay)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

    def _take_a_look_at_the_fika_situation(self):
        for fika_break in self._fika_breaks:
            if fika_break.should_be_announced_to_the_world():
                message = self._formulate_a_good_announcement(fika_break.name)
                self._post_message_in_channel(message, self._fika_channel)
                fika_break.was_announced()

    def _formulate_a_good_announcement(self, event_name):
        configuration = self._read_configuration()
        phrases = configuration.get('phrases', {})
        emojis = configuration.get('emojis', {})

        interjection = self._select_any(phrases.get('interjections', ['Yo!']))
        announcement = self._select_any(phrases.get('announcements', ['It time for']))
        if '{}' in announcement or '{0}' in announcement:
            announcement = announcement.format(event_name)
        else:
            announcement = "{} {}!".format(announcement, event_name)

        emoji = self._select_any(emojis.get('fika', ['coffee']))
        message = "{} {} :{}:".format(
            interjection, announcement, emoji)
        return message

    def _encourage_all_fika_mentions(self):
        slack_messange = self._slack_client.rtm_read()
        if slack_messange:
            for message in slack_messange:
                if self._message_is_totally_about_fika(message):
                    self._respond_with_some_love(message)

    def _post_message_in_channel(self, message: str, channel: str):
        self._slack_client.api_call(
            "chat.postMessage", channel=channel, text=message, as_user=True)

    def _register_configuration(self):
        configuration = self._read_configuration()

        self._fika_channel = configuration.get('fika_channel')

        for fika_break in configuration['fika_breaks']:
            new_fika = fika.Fika(
                fika_break['name'],
                datetime.time(*fika_break['start']),
                datetime.time(*fika_break['stop']))

            self._fika_breaks.append(new_fika)

        for pattern in configuration.get('fika_patterns', []):
            self._fika_patterns.append(re.compile(pattern, flags=re.IGNORECASE))

    def _read_configuration(self) -> typing.Dict:
        with self._config_path.open('r') as config_file:
            configuration = json.load(config_file)
        return configuration

    def _respond_with_some_love(self, output: dict):
        emoji = self._grab_any_positive_emoji()
        self._slack_client.api_call(
            "reactions.add",
            channel=output.get('channel'),
            name=emoji,
            timestamp=output.get('ts')
        )

    def _message_is_totally_about_fika(self, output: dict) -> bool:
        it_is_text = 'text' in output
        written_by_a_human = 'bot_id' not in output
        if it_is_text and written_by_a_human:
            for pattern in self._fika_patterns:
                if pattern.search(output['text']):
                    return True
        return False

    def _grab_any_fika_emoji(self) -> typing.Optional[str]:
        return self._grab_any_emoji_by_topic('fika')

    def _grab_any_positive_emoji(self) -> typing.Optional[str]:
        return self._grab_any_emoji_by_topic('positive')

    def _grab_any_emoji_by_topic(self, topic: str) -> typing.Optional[str]:
        configuration = self._read_configuration()
        topic_emojis = configuration.get('emojis', {}).get(topic)
        emoji = self._select_any(topic_emojis)
        return emoji

    def _select_any(self, list_of_stuff: list):
        if not list_of_stuff:
            return None
        return random.choice(list_of_stuff)

