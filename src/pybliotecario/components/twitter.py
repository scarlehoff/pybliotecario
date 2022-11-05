"""
    Module to interact with twitter

    In order to use this module, create a new application in the
    [twitter developers portal](https://developer.twitter.com/)
    and fill in `.pybliotecario.ini` the keys requested by `_authenticate`:

    ```ini
    [TWITTER]
    access_token = <acces_token>
    access_token_secret = <access_token_secret>
    consumer_key = <consumer_key>
    consumer_secret = <consumer_secret>
    ```
"""
import logging

import tweepy as tw

from pybliotecario.components.component_core import Component

logger = logging.getLogger(__name__)
COMP_NAME = "TWITTER"


def _authenticate(config):
    """Authenticate a user using a consumer key and consumer secret"""
    at = config["access_token"]
    ats = config["access_token_secret"]
    ck = config["consumer_key"]
    cs = config["consumer_secret"]
    auth = tw.OAuth1UserHandler(
        consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats
    )
    return tw.API(auth)


def _parse_tweet(tweet):
    """Convert a tweet into a text string"""
    author = tweet.author
    text = tweet.text
    return f"{author.name} (@{author.screen_name}): {text}"


def _prepare_tweet_list(list_of_tweets):
    """Make a list of tweets into a string that can be sent"""
    all_tweets = []
    for tweet in list_of_tweets:
        all_tweets.append(_parse_tweet(tweet))
    return "\n-\n".join(all_tweets)


def _parse_tl_command(command_data):
    """Parse the command data from a TL
    This can be:
        @user N
        N @user
        @user
        N

    Returns
    -------
        user: username
        N: number of tweets to retrieve
    """
    if "@" in command_data:
        data = command_data.split()
        # If there are extra stuff we don't care
        if len(data) < 2:
            return data[0], None
        if data[0].startswith("@"):
            username = data[0][1:]
            N = data[1]
        else:
            username = data[1][1:]
            N = data[0]
        return username, N
    return None, command_data


class TwitterComponent(Component):
    """
    Interact with twitter
    """

    help_text = """
    > Twitter module
    /twitter_tl [@user] [N=20]: send the last N tweets from the TL [of user @user]
    /twitter_mentions [N=5]: send the last N mentions
    /twitter_tweet <text>: send a tweet"""

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        self._api = _authenticate(self.read_config_section(COMP_NAME))

    @classmethod
    def configure_me(cls):
        # TODO:
        # Add automatic get token thing
        pass

    def _get_timeline(self, n=None):
        """Send the last ``n`` tweets from the user timeline"""
        if n is None:
            n = 20
        return _prepare_tweet_list(self._api.home_timeline(count=n))

    def _get_timeline_from_user(self, user, n=None):
        """Send the last ``n`` tweets from @user"""
        if n is None:
            n = 10
        return _prepare_tweet_list(self._api.user_timeline(screen_name=user, count=n))

    def _get_mentions(self, n=None):
        """Send the last ``n`` mentions of the user"""
        if n is None:
            n = 5
        return _prepare_tweet_list(self._api.mentions_timeline(count=n))

    def _send_tweet(self, tweet_msg):
        """Sends tweet_msg as a tweet"""
        if len(tweet_msg) > 280:
            self.send_msg("The tweet is too long! Please limit yourself to 280 characters!")
            return
        self._api.update_status(tweet_msg)
        return "tweet sent"

    def telegram_message(self, msg):
        """Digest the telegram msg"""
        command = msg.command
        data = msg.text.strip()
        if command == "twitter_tl":
            user, n = _parse_tl_command(data)
            if user is None:
                response = self._get_timeline(n)
            else:
                response = self._get_timeline_from_user(user, n)
        elif command == "twitter_mentions":
            response = self._get_mentions(data)
        elif command == "twitter_tweet":
            response = self._send_tweet(data)
        else:
            response = "Command not recognized"
        self.send_msg(response)
