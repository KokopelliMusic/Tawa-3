import json


def is_authenticated(request):
  return request.user.is_authenticated


def is_staff(request):
  return request.user.is_staff


def to_json(obj):
  return obj.toJSON()

def to_json_small(obj):
  return obj.toJSON(recursive=False)


def J(obj):
  return obj.toJSON()


def JS(obj):
  return obj.toJSON(recursive=False)