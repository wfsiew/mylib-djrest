from django.urls import path, re_path
from . import views

urlpatterns = [
    path('users/', views.UserList.as_view()),
    re_path('user/delete/(?P<pk>[0-9]+)/$', views.UserDelete.as_view()),
    re_path('user/detail/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
    re_path('user/picture/(?P<pk>[0-9]+)/$', views.UserPicture.as_view()),

    path('books/',views.BookList.as_view()),
    re_path('book/create/', views.BookCreate.as_view()),
    re_path('book/delete/(?P<pk>[0-9]+)/$', views.BookDelete.as_view()),
    re_path('book/update/(?P<pk>[0-9]+)/$', views.BookUpdate.as_view()),
    re_path('book/detail/(?P<pk>[0-9]+)/$', views.BookDetail.as_view()),
    re_path('book/checkout/(?P<book_id>[0-9]+)/$', views.BookCheckout.as_view()),
    re_path('book/return/(?P<book_id>[0-9]+)/$', views.BookReturn.as_view()),

    re_path('bookstatus/(?P<pk>[0-9]+)/$', views.BookStatus.as_view()),
    path('daily/', views.Daily.as_view()),

    path('blacklist/', views.BlackListUserList.as_view()),
    re_path('blacklist/(?P<pk>[0-9]+)/$', views.BlackListUserDetail.as_view()),
]