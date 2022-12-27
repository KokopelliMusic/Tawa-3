from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
  profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True)

  def toJSON(self):
    return {
      'id': self.id,
      'username': self.username,
      'profile_picture': self.profile_picture.url if self.profile_picture else None
    }

  def __str__(self):
    return self.username


class AccessToken(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  token = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f'{self.user.username} - {self.token}'