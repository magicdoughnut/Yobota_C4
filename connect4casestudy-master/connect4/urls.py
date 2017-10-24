from django.conf.urls import url
import views

urlpatterns = [
    url(r'^login/$', views.loginview, name = 'login'),
    url(r'^signup/$', views.signup, name = 'signup'),
    url(r'^logout/$', views.logoutview, name = 'logout'),
    url(r'^games/$', views.games, name = 'games'),
    url(r'^play/(?P<game_id>[0-9]+)/$', views.play, name = 'play'),
]
