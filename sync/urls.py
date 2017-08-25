from django.conf.urls import url
import views

urlpatterns = [
    url(r'^download/$', views.downloadattach),
    url(r'^close/$', views.closeconnection),
    url(r'^read/$', views.readlogs),
    url(r'^move/$', views.move_files),
    url(r'^add/$', views.enter_files_into_the_db),
    url(r'^contacts/$', views.call_center_contacts),
    url(r'^$', views.index, name='index'),

]


