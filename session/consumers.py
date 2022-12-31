import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django_redis import get_redis_connection

class SessionConsumer(WebsocketConsumer):
  def connect(self):
    self.session_id = self.scope['url_route']['kwargs']['session_id']
    self.redis = get_redis_connection('default')

    async_to_sync(self.channel_layer.group_add)(
      self.session_id,
      self.channel_name
    )

    self.accept()


  def disconnect(self, close_code):
    async_to_sync(self.channel_layer.group_discard)(
      self.session_id,
      self.channel_name
    )

  def validate_json(self, obj):
    errors = []

    if not 'session_id' in obj:
      errors.append('Session ID not found in JSON object')

    if not 'client_type' in obj:
      errors.append('Client type not found in JSON object')

    if not 'event_type' in obj:
      errors.append('Event type not found in JSON object')

    if not 'data' in obj:
      errors.append('Data not found in JSON object')

    if not 'date' in obj:
      errors.append('Date not found in JSON object')

    return errors



  def receive(self, text_data):
    event_json = '{}'
    try:
      event_json = json.loads(text_data)
      errors = self.validate_json(event_json)
    except:
      errors = ['Invalid JSON']

    if len(errors) > 0:
      self.send(text_data=json.dumps({
        'errors': errors
      }))
      return

    # no errors, so we can set the cache and dump the event to all clients
    pipeline = self.redis.pipeline()
    # Push the event to the list
    self.redis.lpush(f'session::{self.session_id}', text_data)
    # Trim the list to 100 elements
    self.redis.ltrim(f'session::{self.session_id}', 0, 99)
    # Execute the pipeline!
    pipeline.execute()

    # Send the event to all clients
    async_to_sync(self.channel_layer.group_send)(
      self.session_id,
      {"type": "event", "event": {
        'errors': errors,
        'event_data': event_json
      }}
    )


  def event(self, event):
    self.send(text_data=json.dumps(event['event']))
  