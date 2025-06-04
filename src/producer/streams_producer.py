from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
import asyncio
import time
import logging
import json
import os
from datetime import datetime
from twitch_api import fetch_top_games, fetch_top_streams, fetch_users_by_ids_batch, init_twitch
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Environment variables
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
STREAMS_TOPIC = os.getenv('TOPIC')
USERS_TOPIC = os.getenv('USERS_TOPIC')

class KafkaStreamProducer:
    """Kafka producer for Twitch streams and users data."""
    
    def __init__(self):
        logger.info("Initializing Kafka producer with JSON serialization...")
        # Initialize producers with JSON value serialization
        kafka_config = {'bootstrap.servers': KAFKA_BROKER}
        self.streams_producer = SerializingProducer({
            **kafka_config,
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': lambda v, ctx: json.dumps(v).encode('utf-8')
        })
        self.users_producer = SerializingProducer({
            **kafka_config,
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': lambda v, ctx: json.dumps(v).encode('utf-8')
        })
        logger.info("Kafka JSON producers initialized successfully")
    
    def produce_stream(self, stream_data):
        """Produce a single stream record to Kafka."""
        self.streams_producer.produce(
            topic=STREAMS_TOPIC,
            key=stream_data['user_id'],
            value=stream_data
        )
    
    def produce_streams_batch(self, streams_data):
        """Produce multiple stream records to Kafka."""
        start_time = time.time()
        for stream_data in streams_data:
            self.produce_stream(stream_data)
        self.streams_producer.flush()
        duration = time.time() - start_time
        logger.info(f"Produced {len(streams_data)} streams to Kafka in {duration:.2f}s")
    
    def produce_user(self, user_data):
        """Produce a single user record to Kafka."""
        self.users_producer.produce(
            topic=USERS_TOPIC,
            key=user_data['id'],
            value=user_data
        )
    
    def produce_users_batch(self, users_data, data_retrieved_at=None):
        """Produce multiple user records to Kafka."""
        start_time = time.time()
        for user_dict in users_data:
            # Transform user data to match schema
            transformed_user = self.transform_user_data(user_dict, data_retrieved_at)
            self.produce_user(transformed_user)
        self.users_producer.flush()
        duration = time.time() - start_time
        logger.info(f"Produced {len(users_data)} users to Kafka in {duration:.2f}s")
    
    def transform_stream_data(self, stream, data_retrieved_at=None):
        """Transform Twitch stream object to producer format."""
        # ensure có tzinfo, rồi convert về Asia/Ho_Chi_Minh
        dt = stream.started_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        local = dt.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        started_at_str = local.strftime("%Y-%m-%d %H:%M:%S")
        tags_str = ",".join(stream.tags) if stream.tags else ""

        # Format data retrieval time
        if data_retrieved_at is None:
            data_retrieved_at = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
        data_retrieved_at_str = data_retrieved_at.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "id": stream.id,
            "user_id": stream.user_id,
            "user_login": stream.user_login,
            "user_name": stream.user_name,
            "game_id": stream.game_id,
            "game_name": stream.game_name,
            "type": stream.type,
            "title": stream.title,
            "viewer_count": stream.viewer_count,
            "started_at": started_at_str,
            "language": stream.language,
            "thumbnail_url": stream.thumbnail_url,
            "is_mature": stream.is_mature,
            "tags": tags_str,
            "data_retrieved_at": data_retrieved_at_str
        }
    
    def transform_user_data(self, user_dict, data_retrieved_at=None):
        """Transform Twitch user dict to producer format."""
        # datetime is already imported globally, ZoneInfo too.
        
        created_at_input = user_dict.get('created_at')
        dt_for_formatting = None

        if isinstance(created_at_input, str):
            try:
                # Parse ISO format datetime string, ensure it's UTC if no tzinfo
                parsed_dt = datetime.fromisoformat(created_at_input.replace('Z', '+00:00'))
                if parsed_dt.tzinfo is None:
                    dt_for_formatting = parsed_dt.replace(tzinfo=ZoneInfo("UTC"))
                else:
                    dt_for_formatting = parsed_dt.astimezone(ZoneInfo("UTC")) # Convert to UTC
            except ValueError:
                dt_for_formatting = datetime.now(ZoneInfo("UTC")) # Fallback to current UTC time
        elif hasattr(created_at_input, 'timestamp') and hasattr(created_at_input, 'astimezone'): # Check if it's a datetime-like object
            # Ensure it's UTC
            if created_at_input.tzinfo is None:
                dt_for_formatting = created_at_input.replace(tzinfo=ZoneInfo("UTC"))
            else:
                dt_for_formatting = created_at_input.astimezone(ZoneInfo("UTC"))
        else:
            dt_for_formatting = datetime.now(ZoneInfo("UTC")) # Fallback to current UTC time
        
        # Convert to Asia/Ho_Chi_Minh and format
        local_created_at = dt_for_formatting.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
        created_at_str = local_created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format data retrieval time
        if data_retrieved_at is None:
            data_retrieved_at = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
        data_retrieved_at_str = data_retrieved_at.strftime("%Y-%m-%d %H:%M:%S")
        
        email_val = user_dict.get('email')

        return {
            "id": user_dict.get('id', ''),
            "login": user_dict.get('login', ''),
            "display_name": user_dict.get('display_name', ''),
            "type": user_dict.get('type', ''),
            "broadcaster_type": user_dict.get('broadcaster_type', ''),
            "description": user_dict.get('description', ''),
            "profile_image_url": user_dict.get('profile_image_url', ''),
            "offline_image_url": user_dict.get('offline_image_url', ''),
            "view_count": user_dict.get('view_count', 0),
            "email": email_val if email_val is not None else "",  # Changed: Send "" if email is None
            "created_at": created_at_str,
            "data_retrieved_at": data_retrieved_at_str
        }

async def produce_loop():
    """Main production loop for fetching and producing Twitch data."""
    twitch = await init_twitch()
    producer = KafkaStreamProducer()
    
    logger.info("Starting Twitch data production loop...")
    
    cycle_count = 0
    while True:
        cycle_start = time.time()
        cycle_count += 1
        
        try:
            logger.info(f"Starting cycle #{cycle_count}")
            
            # Fetch top games and streams
            api_start = time.time()
            logger.debug("Fetching top games...")
            games = await fetch_top_games(twitch)
            
            all_streams = []
            logger.debug(f"Fetching streams for {len(games)} games...")
            for game in games:
                streams = await fetch_top_streams(twitch, game.id)
                all_streams.extend(streams)
            
            # Record the time when API fetch completed
            data_retrieved_at = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
            api_duration = time.time() - api_start
            logger.info(f"API fetch completed: {len(games)} games, {len(all_streams)} streams in {api_duration:.2f}s")
            
            # Transform and produce stream records
            transform_start = time.time()
            streams_data = [producer.transform_stream_data(stream, data_retrieved_at) for stream in all_streams]
            transform_duration = time.time() - transform_start
            logger.debug(f"Stream data transformation took {transform_duration:.2f}s")
            
            producer.produce_streams_batch(streams_data)
            
            # Fetch and produce user records
            if all_streams:
                user_ids = list({s.user_id for s in all_streams})
                logger.debug(f"Fetching user data for {len(user_ids)} users...")
                
                user_api_start = time.time()
                users_data = await fetch_users_by_ids_batch(twitch, user_ids)
                # Record the time when user API fetch completed
                user_data_retrieved_at = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
                user_api_duration = time.time() - user_api_start
                logger.debug(f"User API fetch took {user_api_duration:.2f}s")
                
                producer.produce_users_batch(list(users_data.values()), user_data_retrieved_at)
            
            cycle_duration = time.time() - cycle_start
            total_api_time = api_duration + (user_api_duration if all_streams else 0)
            
            logger.info(f"Cycle #{cycle_count} completed: {len(streams_data)} streams, "
                       f"{len(users_data) if all_streams else 0} users produced. "
                       f"Total: {cycle_duration:.2f}s (API: {total_api_time:.2f}s)")
            
        except Exception as e:
            logger.error(f"Error in production cycle #{cycle_count}: {e}", exc_info=True)
        
        logger.info("Waiting 60 seconds before next cycle...")
        await asyncio.sleep(60)


if __name__ == '__main__':
    asyncio.run(produce_loop())
