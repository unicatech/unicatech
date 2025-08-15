from django.urls import path
from .views import IndexView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import LoginView,LogoutView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('accounts/login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
]

urlpatterns += staticfiles_urlpatterns()

