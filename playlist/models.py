from django.db import models
from user.models import User


class Playlist(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)

  def __str__(self):
    return f'Playlist: {self.name}'

  def toJSON(self, recursive=True):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'created_at': self.created_at,
      'updated_at': self.updated_at,
      'creator': self.creator.toJSON() if recursive else self.creator.username,
      'songs': [song.toJSON() for song in self.songs.all()] if recursive else None
    }

  class Meta:
    ordering = ['-created_at']
    verbose_name = 'Playlist'
    verbose_name_plural = 'Playlists'

SONG_TYPES = (
  ('spotify', 'Spotify'),
  ('youtube', 'YouTube'),
  ('soundcloud', 'SoundCloud'),
  ('mp3', 'MP3'),
)

class Song(models.Model):
  title = models.CharField(max_length=200)
  artists = models.CharField(max_length=200)
  album = models.CharField(max_length=200)
  length = models.IntegerField()
  cover = models.CharField(max_length=200)

  playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='songs')
  added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=None)

  platform_id = models.CharField(max_length=200)

  class SongType(models.TextChoices):
    SPOTIFY = 'spotify', 'Spotify'
    YOUTUBE = 'youtube', 'YouTube'
    SOUNDCLOUD = 'soundcloud', 'SoundCloud'
    MP3 = 'mp3', 'MP3'

  song_type = models.CharField(max_length=20, choices=SongType.choices, default=SongType.SPOTIFY)

  def __str__(self):
    return f'{self.title} by {self.artists}'


  def toJSON(self, recursive=True):
    return {
      'id': self.id,
      'title': self.title,
      'artists': self.artists,
      'album': self.album,
      'length': self.length,
      'cover': self.cover,
      'added_by': self.added_by.toJSON() if recursive else self.added_by.username,
      'song_type': self.song_type
    }