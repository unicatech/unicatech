from django.urls import path
from .views import IndexView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
]

urlpatterns += staticfiles_urlpatterns()

