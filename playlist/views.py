from playlist.models import Playlist, Song

from tawa3.tools import is_authenticated, J, JS

from modernrpc.core import rpc_method
from modernrpc.auth import set_authentication_predicate


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_playlists():
  return [JS(x) for x in Playlist.objects.all()]


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_playlist(playlist_id):
  return J(Playlist.objects.get(id=playlist_id))


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_own_playlists(**kwargs):
  user = kwargs.get('request').user

  return [J(x) for x in Playlist.objects.filter(creator=user)]


@rpc_method
@set_authentication_predicate(is_authenticated)
def create_playlist(name, description="No description yet :(", **kwargs):
  user = kwargs.get('request').user

  if name == "":
    raise Exception("Playlist name cannot be empty")

  playlist = Playlist.objects.create(name=name, creator=user, description=description)
  return J(playlist)


@rpc_method
@set_authentication_predicate(is_authenticated)
def delete_playlist(playlist_id, **kwargs):
  user = kwargs.get('request').user

  playlist = Playlist.objects.get(id=playlist_id)

  if not playlist:
    raise Exception("Playlist not found")

  if playlist.creator != user:
    raise Exception("You are not allowed to delete this playlist")

  playlist.delete()
  return True


@rpc_method
@set_authentication_predicate(is_authenticated)
def add_song_to_playlist(title, artists, album, length, cover, playlist_id, platform_id, song_type, **kwargs):
  user = kwargs.get('request').user

  # Cant find a better way to do this :()
  if title == "":
    raise Exception("Song title cannot be empty")

  if artists == "":
    raise Exception("Song artists cannot be empty")
  
  if album == "":
    raise Exception("Song album cannot be empty")

  if type(length) == 'int':
    raise Exception("Song length is not a number")

  if cover == "":
    raise Exception("Song cover cannot be empty")
  
  if type(playlist_id) == 'int':
    raise Exception("Playlist id is not a number")

  if platform_id == "":
    raise Exception("Song platform id cannot be empty")

  if song_type == "":
    raise Exception("Song type cannot be empty")

  playlist = Playlist.objects.get(id=playlist_id)

  duplicate_song = Song.objects.filter(playlist=playlist, platform_id=platform_id)

  if duplicate_song:
    raise Exception("Song already exists in playlist")

  if not playlist:
    raise Exception("Playlist not found")

  song = Song.objects.create(
    title=title,
    artists=artists,
    album=album,
    length=length,
    cover=cover,
    playlist=playlist,
    added_by=user,
    platform_id=platform_id,
    song_type=song_type
  )

  print(song)

  song.save()

  return J(song)


@rpc_method
@set_authentication_predicate(is_authenticated)
def delete_song_from_playlist(song_id, **kwargs):
  user = kwargs.get('request').user

  song = Song.objects.get(id=song_id)

  if not song:
    raise Exception("Song not found")

  if song.added_by != user or song.playlist.creator != user:
    raise Exception("You are not allowed to delete this song, since you either did not add it or you are not the creator of the playlist")

  song.delete()
  return True


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_specific_song(song_id):
  song = Song.objects.get(id=song_id)

  if not song:
    raise Exception("Song not found")

  return J(song)


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_number_of_users(playlist_id):

  songs = Song.objects.filter(playlist=playlist_id)

  if not songs:
    raise Exception("Playlist not found")

  unique_users = []

  for song in songs:
    if song.added_by not in unique_users:
      unique_users.append(song.added_by)

  return {
    'song_count': len(songs),
    'user_count': len(unique_users)
  }