from django.http import HttpResponseBadRequest
from user.models import AccessToken

class AccessTokenMiddleware:

  def __init__(self, get_response):
    self.get_response = get_response


  def __call__(self, request):
    response = self.get_response(request)

    if request.method == 'POST' and (request.path == '/rpc' or request.path == '/rpc/'):
      client_type = request.META.get('HTTP_X_KOKOPELLI_CLIENT_TYPE', None)

      if not client_type:
        return HttpResponseBadRequest('X-Kokopelli-Client-Type header not specified')

    return response

  def process_view(self, request, view_func, *view_args, **view_kwargs):
    bearer_token = request.META.get('HTTP_AUTHORIZATION', None)

    if bearer_token:
      token_str = bearer_token.split(' ')[1]

      token_obj = AccessToken.objects.filter(token=token_str).first()

      if token_obj:
        request.user = token_obj.user
        request.access_token = token_obj

