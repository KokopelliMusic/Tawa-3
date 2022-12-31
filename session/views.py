import datetime
import traceback
import pytz
import json

from django.db import transaction
from django.core import serializers

from dateutil import parser

from modernrpc.core import rpc_method
from modernrpc.auth import set_authentication_predicate

from tawa3.tools import is_authenticated, is_staff, J
from session.models import KokopelliEvent, Session, Queue, SessionSettings, Spotify, CurrentlyPlaying
from playlist.models import Song

from django_redis import get_redis_connection
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

redis = get_redis_connection('default')


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_event_history(session_id, **kwargs):
  event_cache = redis.lrange('session::' + session_id, 0, 99)

  events = []

  for event in event_cache:
    events.append(json.loads(event.decode('utf-8')))
  
  return events


@rpc_method
@set_authentication_predicate(is_authenticated)
def push_event(session_id, client_type, event_type, data, **kwargs):
  now = datetime.datetime.now().isoformat()
  event = {
    'client_type': client_type,
    'event_type': event_type,
    'data': data,
    'date': now,
    'session_id': session_id
  }

  pipeline = redis.pipeline()
  # Push the event to the list
  redis.lpush(f'session::{session_id}', json.dumps(event))
  # Trim the list to 100 elements
  redis.ltrim(f'session::{session_id}', 0, 99)
  # Execute the pipeline!
  pipeline.execute()

  channel_layer = get_channel_layer()

  # Send the event to the group
  async_to_sync(channel_layer.group_send)(
    session_id,
    {"type": "event", "event": event}
  )

  return {
    'success': True
  }


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_session(session_id, **kwargs):
  settings = SessionSettings.objects.get(session__session_id=session_id)

  return J(settings)


@rpc_method
@set_authentication_predicate(is_staff)
def get_sessions(**kwargs):
  return [J(x) for x in Session.objects.all()]


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_session_settings(session_id, **kwargs):
  return J(SessionSettings.objects.get(session_id=session_id))


def delete_old_sessions():
  one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
  one_day_ago = one_day_ago.replace(tzinfo=pytz.UTC)

  old_sessions = Session.objects.filter(claimed=False, created_at__lt=one_day_ago).all()

  if len(old_sessions) > 0:
    for s in old_sessions:
      s.delete()


@rpc_method
def create_temp_session(**kwargs):
  session = Session.objects.create()

  # Check if there are any old sessions that are not claimed
  delete_old_sessions()

  return J(session)
  

@rpc_method
@set_authentication_predicate(is_authenticated)
def claim_session(playlist_id, session_id, settings, **kwargs):
  # Exceptions are handled by the RPC framework, so we do not need a try/catch block

  # Open a atomic transaction
  with transaction.atomic():
    user = kwargs['request'].user
    token = kwargs['request'].access_token

    # first check if the session is already claimed
    session = Session.objects.get(session_id=session_id)

    if session.claimed == True:
      raise Exception('Session already claimed')

    # Then: delete all other (old) sessions for this user
    old_session = Session.objects.filter(user=user).all()

    if len(old_session) > 0:
      for s in old_session:
        s.delete()

    # Claim the session

    session.playlist_id = playlist_id
    session.claimed = True
    session.user = user
    session.save()

    # Create the session settings
    a = settings['allowed_events']
    del settings['allowed_events']
    allowed_events = []
    for e in a:
      name = e['name']
      event = KokopelliEvent.objects.filter(name=name)

      if (len(event) == 0):
        raise Exception('Event not found: ' + name)

      allowed_events.append(event[0])

    session_settings = SessionSettings.objects.create(session=session, **settings)
    session_settings.allowed_events.set(allowed_events)
    session_settings.save()

    # Everything went right! Now notify the webplayer that the session has been claimed

    spotify = Spotify.objects.get(user=user)

    push_event(session.session_id, 'tawa', 'session_created', json.dumps({
      'session': J(session),
      'settings': J(session_settings),
      'spotify': J(spotify),
      'user': J(user),
      'user_token': J(token)
    }))
    
    return J(session)


@rpc_method
@set_authentication_predicate(is_authenticated)
def join_session(session_id):
  """
    Lets an user "join" a session, which does not really do anything anymore
    but it's still here for legacy reasons. We check if the session is correct and claimed, and if so, we return the session
  """

  session = Session.objects.get(session_id=session_id)

  if session.claimed == False:
    raise Exception('Session not claimed, cannot join')

  return J(session)


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_spotify(**kwargs):
  user = kwargs['request'].user

  spotify = Spotify.objects.filter(user=user).first()

  if spotify is None:
    raise Exception('Spotify not connected!')

  return J(spotify)


@rpc_method
@set_authentication_predicate(is_authenticated)
def set_spotify(access_token, refresh_token, expires_at, **kwargs):
  user = kwargs['request'].user

  spotify = Spotify.objects.filter(user=user).first()

  if spotify is None:
    spotify = Spotify.objects.create(user=user, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
  else:
    spotify.access_token = access_token
    spotify.refresh_token = refresh_token
    spotify.expires_at = parser.parse(expires_at)
    spotify.save()

  return J(spotify)


@rpc_method
@set_authentication_predicate(is_authenticated)
def update_spotify(access_token, expires_at, **kwargs):
  user = kwargs['request'].user

  spotify = Spotify.objects.filter(user=user).first()

  if spotify is None:
    raise Exception('Spotify not connected!')

  spotify.access_token = access_token
  spotify.expires_at = parser.parse(expires_at)
  spotify.save()

  return J(spotify)


@rpc_method
@set_authentication_predicate(is_authenticated)
def delete_spotify(**kwargs):
  user = kwargs['request'].user

  spotify = Spotify.objects.filter(user=user).first()

  if spotify is None:
    raise Exception('Spotify not connected!')

  spotify.delete()

  return True


@rpc_method
@set_authentication_predicate(is_authenticated)
def set_currently_playing(song_id, session_id, **kwargs):  
  with transaction.atomic():
    song = Song.objects.get(id=song_id)
    session = Session.objects.get(session_id=session_id)
    
    # Delete all currently playing songs for this session
    CurrentlyPlaying.objects.filter(session=session).delete()

    currenty_playing = CurrentlyPlaying.objects.create(song=song, session=session)

    # Then, increment the play count for this song
    song.play_count += 1
    song.save()

    # Remove the song from the queue
    queue = Queue.objects.filter(session=session, song=song).first()

    if queue is not None:
      queue.delete()

    # Notify all clients that a new song is playing
    push_event(session.session_id, 'tawa', 'play_song', {
      'song': J(song),
    })

    return J(currenty_playing)


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_currently_playing(session_id, **kwargs):
  p = CurrentlyPlaying.objects.get(session__session_id=session_id)

  return J(p)


@rpc_method
@set_authentication_predicate(is_authenticated)
def set_queue(ids, session_id):
  with transaction.atomic():
    session = Session.objects.get(session_id=session_id)

    if type(ids) is not list:
      raise Exception('ids must be an array')

    # Delete all songs in the queue for this session
    Queue.objects.filter(session=session).delete()

    q = []

    for idx, id in enumerate(ids):
      # Check if all songs exist
      song = Song.objects.get(id=id)
      # Create the queue object
      queue = Queue.objects.create(song=song, session=session, position=idx)
      q.append(queue)

    return {
      'queue': [J(queue) for queue in q]
    }


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_queue(session_id, **kwargs):
  queue = Queue.objects.filter(session__session_id=session_id).order_by('position').all()

  return [J(q) for q in queue]