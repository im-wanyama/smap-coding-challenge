from . import views
from django.urls import re_path

urlpatterns = [
    re_path(r'^$', views.front_page, name='layout'),
    re_path(r'^summary/$', views.summary, name='summary'),
    re_path(r'^detail_search/$', views.detail, name='detail'),
    re_path(r'^detail_search/find/$', views.detail_search,
            name='detail_search'),
    re_path(r'^api/detail_search/find/$', views.detail_search_api),
    re_path(r'^api/summary/$', views.summary_api)
]
