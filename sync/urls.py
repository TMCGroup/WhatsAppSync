from django.conf.urls import url
import views

urlpatterns = [

    url(r'^download/$', views.download_attach),
    url(r'^close/$', views.close_connection),
    url(r'^read/$', views.read_logs),
    url(r'^move/$', views.move_files),
    url(r'^add/$', views.enter_files_into_the_db),
    url(r'^contacts/$', views.call_center_contacts),
    url(r'^send/$', views.send_rapidpro_data),
    url(r'^get/$', views.get_reapidpro_messages),
    url(r'^archive/$', views.archive_rapidpro),


]


