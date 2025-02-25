from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('authors/', views.authors, name="authors"),
    path('authors/<int:author_id>', views.author, name="author"),
    path('books/', views.BookListView.as_view(), name="books"),
    path('books/<int:pk>', views.BookDetailView.as_view(), name="book"),
    path('mycopies/', views.MyBookInstanceListView.as_view(), name='mycopies'),
    path('search/', views.search, name="search"),
    path('register/', views.register, name="register"),
    path('profile/', views.profile, name="profile"),
    path('instances/', views.BookInstanceListView.as_view(), name="instances"),
    path('instances/<int:pk>', views.BookInstanceDetailView.as_view(), name='instance'),
]
