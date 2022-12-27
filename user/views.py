import secrets

from modernrpc.core import rpc_method
from modernrpc.auth import set_authentication_predicate
from django.contrib.auth import authenticate
from tawa3.tools import is_authenticated

from user.models import User, AccessToken

@rpc_method
def register(email, username, password, **kwargs):
  try:
    user = User.objects.create_user(email=email, username=username, password=password)

    user.save()
  except Exception as e:
    raise Exception('Username and or email already exists')

  # Generate Access Token and store, send it back to the client
  token = login(username, password, **kwargs)

  return token


@rpc_method
def login(username, password, **kwargs):
  
  user = authenticate(username=username, password=password)

  # Generate Access Token and store, send it back to the client

  if user is not None:
    token = secrets.token_urlsafe(64).replace('-', '_')
    access_token = AccessToken.objects.create(user=user, token=token)

    return {
      'token': access_token.token,
      'user': user.toJSON()
    }

  else:
    raise Exception('Invalid credentials') 


@rpc_method
@set_authentication_predicate(is_authenticated)
def logout(**kwargs):
  user = user = kwargs.get('request').user

  if user.is_authenticated:
    AccessToken.objects.filter(user=user).delete()
    return True
  return False


@rpc_method
@set_authentication_predicate(is_authenticated)
def get_user(**kwargs):
  user = kwargs.get('request').user
  return user.toJSON()