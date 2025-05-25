from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
import asyncio
from twitch_api import fetch_top_games, fetch_top_streams, init_twitch
import json
import os


def register_schema(schema_registry_client, subject, schema_path):
    with open(schema_path, 'r') as schema_file:
        schema = schema_file.read()
    avro_schema = Schema(schema_str=schema , schema_type='AVRO')
    schema_id = schema_registry_client.register_schema(subject, avro_schema)
    return schema_id


def get_schema(schema_registry_client, subject):
    schema_str = schema_registry_client.get_latest_version(subject).schema.schema_str
    return AvroSerializer(schema_registry_client, schema_str)


def produce_lol_streams_message(producer, subject, key, value):
    producer.produce(subject, key=key, value=value)
    producer.flush()


schema_path = "../schemas/lol_streams_avro_schema.json"
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
TOPIC = os.getenv('TOPIC')
SUBJECT = 'streams-value'
SCHEMA_REGISTRY_URL = os.getenv('SCHEMA_REGISTRY_URL')

schema_registry_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})

register_schema(schema_registry_client, SUBJECT, schema_path)

kafka_config = {
    'bootstrap.servers': KAFKA_BROKER,
}

lol_streams_producer = SerializingProducer({
    **kafka_config,
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': get_schema(schema_registry_client, SUBJECT)
})


async def produce_lol_streams():
    """Fetch streams from Twitch and produce to Kafka with Avro schema."""
    twitch = await init_twitch()
    while True:
        games = await fetch_top_games(twitch)
        for game in games:
            streams = await fetch_top_streams(twitch, game.id)
            for s in streams:
                record = {
                    "id": s.id,
                    "user_id": s.user_id,
                    "user_login": s.user_login,
                    "user_name": s.user_name,
                    "game_id": s.game_id,
                    "game_name": s.game_name,
                    "type": s.type,
                    "title": s.title,
                    "viewer_count": s.viewer_count,
                    "started_at": int(s.started_at.timestamp() * 1000),
                    "language": s.language,
                    "thumbnail_url": s.thumbnail_url,
                    "tag_ids": s.tag_ids,
                    "is_mature": s.is_mature,
                    "tags": s.tags
                }
                
                lol_streams_producer.produce(
                    topic=TOPIC,
                    key=s.user_id,
                    value=record
                )
                lol_streams_producer.flush()
        await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(produce_lol_streams())
