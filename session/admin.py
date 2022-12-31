from django.contrib import admin

from session.models import Session, SessionSettings, KokopelliEvent, Spotify, CurrentlyPlaying
class SessionAdmin(admin.ModelAdmin):
  # allow editing of created_at
  readonly_fields = ('created_at', 'updated_at')

admin.site.register(Session, SessionAdmin)
admin.site.register(SessionSettings)
admin.site.register(KokopelliEvent)  
admin.site.register(Spotify)
admin.site.register(CurrentlyPlaying)