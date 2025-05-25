import json
import asyncio
import os
from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()


APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')


async def fetch_top_games(twitch):
    # collect first 10 games manually
    result = []
    async for game in twitch.get_top_games(first=10):
        result.append(game)
        if len(result) >= 10:
            break
    return result


async def fetch_top_streams(twitch, game_id):
    # collect first 10 streams manually
    result = []
    async for stream in twitch.get_streams(game_id=game_id, first=10):
        result.append(stream)
        if len(result) >= 10:
            break
    return result


async def fetch_user_info(twitch, login):
    """Fetch user info by Twitch login name."""
    user = await first(twitch.get_channel_information())
    return user.to_dict()


async def init_twitch():
    """Initialize and authenticate Twitch client asynchronously."""
    twitch = await Twitch(os.getenv('APP_ID'), os.getenv('APP_SECRET'))
    return twitch
