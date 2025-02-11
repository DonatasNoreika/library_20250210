from django.contrib import admin
from .models import Author, Book, Genre, BookInstance

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'display_genre']

# Register your models here.
admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance)
