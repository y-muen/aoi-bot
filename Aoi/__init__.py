import os
import re
import pydoc
import inspect
from functools import wraps
import discord
import numpy as np
import datetime

JST = datetime.timezone(datetime.timedelta(hours=9), name='JST')


def help_command():
    def _help_command(func):
        params = inspect.signature(func).parameters
        i = list(params.keys()).index("interaction")

        @wraps(func)
        async def wrapper(*args, **kwargs):
            if kwargs.get("help"):
                interaction: discord.Interaction = args[i]
                embed = discord.Embed(description=pydoc.render_doc(func))
                await interaction.response.send_message(embed=embed)
            else:
                return await func(*args, **kwargs)
        return wrapper
    return _help_command


def has_permission(**kwargs):
    def _has_permission(func):
        params = inspect.signature(func).parameters
        i = list(params.keys()).index("interaction")
        required = kwargs

        @wraps(func)
        async def wrapper(*args, **kwargs):
            interaction: discord.Interaction = args[i]
            actual = dict(iter(interaction.user.guild_permissions))
            if not all([actual[key] for key in required.keys()]):
                return await interaction.response.send_message(f"Previlage is required: {', '.join(required.keys())}.",
                                                               ephemeral=True)
            else:
                return await func(*args, **kwargs)
        return wrapper
    return _has_permission


def convert_mention_to_user(mention: str):
    """Convert mention to user to user_id."""
    res = re.match(r"^<@\!?(\d+)>$", mention)
    if res is None:
        return mention
    else:
        return res.group(1)


def convert_mention_to_channel(mention: str):
    """Convert mention to channel to profile_id."""
    res = re.match(r"^<#(\d+)>$", mention)
    if res is None:
        return mention
    else:
        return res.group(1)


def convert_mention_to_role(mention: str):
    """Convert mention to role to freshman_id."""
    res = re.match(r"^<@&(\d+)>$", mention)
    if res is None:
        return mention
    else:
        return res.group(1)


def convert_user_to_mention(user_id: str):
    """Convert user_id mention to user."""
    if user_id is None:
        return None

    return f"<@{user_id}>"


def convert_channel_to_mention(profile_id: str):
    """Convert profile_id to mention to channel."""
    if profile_id is None:
        return None

    return f"<#{profile_id}>"


def convert_role_to_mention(freshman_id: str):
    """Convert freshman_id mention to role."""
    if freshman_id is None:
        return None

    return f"<@&{freshman_id}>"


def get_token():
    """Get token of Discord bot."""
    return os.environ["TOKEN"]


def get_database_url():
    """Get database URL of Heroku Postgres."""
    return os.environ["DATABASE_URL"]


def get_twitter_consumer_key():
    """Get consumer_key of Twitter."""
    return os.environ["TWITTER_CONSUMER_KEY"]


def get_twitter_consumer_secret():
    """Get twitter_consumer_secret of Twitter."""
    return os.environ["TWITTER_CONSUMER_SECRET"]


class SearchText(object):
    def __init__(self, value, flags=0):
        self.pattern = re.compile(value, flags=flags)

    def __eq__(self, value: str):
        if isinstance(value, str):
            return bool(self.pattern.search(value))
        if isinstance(value, self.__class__):
            return self.pattern == value.pattern
        else:
            return False


def create_embed(message: discord.Message) -> discord.Embed:
    embed = discord.Embed(description=message.content)
    embed.set_author(name=message.author.nick or message.author.name,
                     icon_url=message.author.avatar)
    return embed


def calc_level(sec: int) -> int:
    """Level `n` requires `2**(n-1)` hours."""
    hour = np.clip(sec // 3600, 0.5, None)
    return int(1 + np.log2(hour) // 1)


def calc_hour(level: int) -> int:
    """Level `n` requires `2**(n-1)` hours."""
    if level <= 0:
        return 0
    else:
        return 2**(level - 1)


def get_delta(tzinfo: datetime.timezone = JST):
    """"""
    now = datetime.datetime.now(tzinfo)
    target = datetime.datetime(now.year,
                               now.month,
                               now.day + int(now.hour >= 5),
                               5,
                               0,
                               0,
                               tzinfo=tzinfo)
    print(f"Now: {now}.")
    print(f"Target: {target}.")
    return (target.timestamp() - now.timestamp())
