import secrets

from modernrpc.core import rpc_method
from modernrpc.auth import set_authentication_predicate
from django.contrib.auth import authenticate
from tawa3.tools import is_authenticated

from user.models import AccessToken

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