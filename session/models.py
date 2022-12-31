import json

from django.db import models
from django.utils.crypto import get_random_string

from user.models import User
from playlist.models import Playlist, Song

class SessionManager(models.Manager):

  allowed_chars = 'ABCDEFGHIJKLNOPQRSTUVXYZ'

  # Generate random session_id that does not exist in the database yet
  def create(self, **obj_data):
    session_id = get_random_string(length=4, allowed_chars=self.allowed_chars)
    
    # Check if session_id already exists in the database
    while self.filter(session_id=session_id).exists():
      # If it does, generate a new one
      session_id = get_random_string(length=4, allowed_chars=self.allowed_chars)
    
    # Set the session_id to the object data
    obj_data['session_id'] = session_id
    # Create the object
    return super().create(**obj_data)


class Session(models.Model):
  session_id = models.CharField(max_length=4, unique=True)
  playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
  claimed = models.BooleanField(default=False)

  objects = SessionManager()

  def toJSON(self, recursive=True):
    return {
      'session_id': self.session_id,
      'user': (self.user.toJSON() if recursive else self.user.username) if self.user else None,
      'playlist_id': self.playlist.id if self.playlist else None,
      'created_at': self.created_at.isoformat(),
      'updated_at': self.updated_at.isoformat(),
      'claimed': self.claimed
    }

  def __str__(self):
    return f'{self.session_id} - {self.claimed}'


class KokopelliEvent(models.Model):
  name = models.CharField(max_length=255)
  pretty_name = models.CharField(max_length=255)
  active = models.BooleanField(default=True)

  def toJSON(self, recursive=False):
    return {
      'name': self.name,
      'pretty_name': self.pretty_name,
      'active': self.active
    }

  def __str__(self):
    return self.pretty_name


class SessionSettings(models.Model):
  session = models.OneToOneField(Session, on_delete=models.CASCADE, primary_key=True)

  # Music Settings
  allow_spotify = models.BooleanField(default=True)
  allow_youtube = models.BooleanField(default=True)
  youtube_only_audio = models.BooleanField(default=False)

  # Event Settings
  allow_events = models.BooleanField(default=True)
  event_frequency = models.IntegerField(default=10)
  allowed_events = models.ManyToManyField(KokopelliEvent, blank=True)
  random_word_list = models.CharField(max_length=1000, default='[]')

  # Permissions
  anyone_can_use_player_controls = models.BooleanField(default=True)
  anyone_can_add_to_queue = models.BooleanField(default=True)
  anyone_can_remove_from_queue = models.BooleanField(default=True)
  anyone_can_see_history = models.BooleanField(default=True)
  anyone_can_see_queue = models.BooleanField(default=True)
  anyone_can_see_playlist = models.BooleanField(default=True)

  # Queue Settings
  algorithm_used = models.CharField(max_length=255, default='random')

  # Misc
  allow_guests = models.BooleanField(default=True)

  def toJSON(self, recursive=True):
    return {
      'session': self.session.toJSON() if recursive else self.session.session_id,
      'allow_spotify': self.allow_spotify,
      'allow_youtube': self.allow_youtube,
      'youtube_only_audio': self.youtube_only_audio,
      'allow_events': self.allow_events,
      'event_frequency': self.event_frequency,
      'allowed_events': [x.toJSON() for x in self.allowed_events.all()],
      'random_word_list': self.random_word_list,
      'anyone_can_use_player_controls': self.anyone_can_use_player_controls,
      'anyone_can_add_to_queue': self.anyone_can_add_to_queue,
      'anyone_can_remove_from_queue': self.anyone_can_remove_from_queue,
      'anyone_can_see_history': self.anyone_can_see_history,
      'anyone_can_see_queue': self.anyone_can_see_queue,
      'anyone_can_see_playlist': self.anyone_can_see_playlist,
      'algorithm_used': self.algorithm_used,
      'allow_guests': self.allow_guests
    }

  def __str__(self):
    return f'Settings for session: {self.session}'


class Spotify(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
  access_token = models.CharField(max_length=255)
  refresh_token = models.CharField(max_length=255)
  expires_at = models.DateTimeField()

  def toJSON(self, recursive=True):
    return {
      'user': self.user.toJSON() if recursive else self.user.username,
      'access_token': self.access_token,
      'refresh_token': self.refresh_token,
      'expires_at': self.expires_at.isoformat()
    }

  def __str__(self):
    return f'Spotify for user: {self.user.username}'


class CurrentlyPlaying(models.Model):
  song = models.ForeignKey(Song, on_delete=models.CASCADE)
  session = models.ForeignKey(Session, on_delete=models.CASCADE)
  started_at = models.DateTimeField(auto_now_add=True)

  def toJSON(self, recursive=True):
    return {
      'song': self.song.toJSON() if recursive else self.song.id,
      'session': self.session.toJSON() if recursive else self.session.session_id,
      'started_at': self.started_at.isoformat()
    }

  def __str__(self):
    return f'{self.song} - {self.session}'


class Queue(models.Model):
  session = models.ForeignKey(Session, on_delete=models.CASCADE)
  song = models.ForeignKey(Song, on_delete=models.CASCADE)
  position = models.IntegerField(default=0)

  def toJSON(self, recursive=True):
    return {
      'session': self.session.session_id,
      'song': self.song.toJSON() if recursive else self.song.id,
      'position': self.position
    }