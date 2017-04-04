from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),

]