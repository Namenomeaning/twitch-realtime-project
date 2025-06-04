import json
import asyncio
import os
import time
import logging
from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')


async def fetch_top_games(twitch):
    """Fetch top 10 games."""
    start_time = time.time()
    result = []
    async for game in twitch.get_top_games(first=10):
        result.append(game)
        if len(result) >= 10:
            break
    
    duration = time.time() - start_time
    logger.debug(f"Fetched {len(result)} top games in {duration:.2f}s")
    return result


async def fetch_top_streams(twitch, game_id):
    """Fetch top 50 streams for a game."""
    start_time = time.time()
    result = []
    async for stream in twitch.get_streams(game_id=game_id, first=50):
        result.append(stream)
        if len(result) >= 50:
            break
    
    duration = time.time() - start_time
    logger.debug(f"Fetched {len(result)} streams for game {game_id} in {duration:.2f}s")
    return result


async def fetch_user_info(twitch, login):
    """Fetch user info by Twitch login name."""
    start_time = time.time()
    user = await first(twitch.get_users(logins=[login]))
    duration = time.time() - start_time
    logger.debug(f"Fetched user info for {login} in {duration:.2f}s")
    return user.to_dict() if user else None

async def fetch_users_by_ids_batch(twitch, user_ids, batch_size=100):
    """Fetch user info for multiple user IDs in batches to handle API limits."""
    start_time = time.time()
    all_users = {}
    
    # Split user_ids into chunks of batch_size
    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]
        logger.debug(f"Fetching batch {i//batch_size + 1}: {len(batch)} users")
        
        batch_start = time.time()
        async for user in twitch.get_users(user_ids=batch):
            all_users[user.id] = user.to_dict()
        
        batch_duration = time.time() - batch_start
        logger.debug(f"Batch {i//batch_size + 1} completed in {batch_duration:.2f}s")
    
    duration = time.time() - start_time
    logger.debug(f"Fetched {len(all_users)} users in {duration:.2f}s ({len(user_ids)//batch_size + 1} batches)")
    return all_users


async def init_twitch():
    """Initialize and authenticate Twitch client asynchronously."""
    logger.info("Initializing Twitch API client...")
    start_time = time.time()
    twitch = await Twitch(os.getenv('APP_ID'), os.getenv('APP_SECRET'))
    duration = time.time() - start_time
    logger.info(f"Twitch API client initialized in {duration:.2f}s")
    return twitch
