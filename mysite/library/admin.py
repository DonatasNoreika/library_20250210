from django.contrib import admin
from .models import Author, Book, Genre, BookInstance

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'display_genre']

class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'book', 'due_back', 'status']
    list_filter = ['due_back', 'status']

# Register your models here.
admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
