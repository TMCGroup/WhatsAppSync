from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'^download/$', views.downloadattach),
    url(r'^close/$', views.closeconnection),
    url(r'^read/$', views.readlogs),
    url(r'^move/$', views.move_files),
    url(r'^add/$', views.enter_files_into_the_db),
    url(r'^contact/$', views.call_center_contacts),
    url(r'^send/$', views.send_rapidpro_data),

]
