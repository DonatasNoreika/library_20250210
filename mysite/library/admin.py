from django.contrib import admin
from .models import Author, Book, Genre, BookInstance

class BookInstanceInLine(admin.TabularInline):
    model = BookInstance
    extra = 0
    can_delete = False
    readonly_fields = ['uuid']
    fields = ['uuid', 'due_back', 'status']

class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'display_genre']
    inlines = [BookInstanceInLine]

class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ['uuid', 'book', 'due_back', 'status']
    list_filter = ['due_back', 'status']

    fieldsets = (
        ('General', {'fields': ('uuid', 'book')}),
        ('Availability', {'fields': ('status', 'due_back')}),
    )

# Register your models here.
admin.site.register(Author)
admin.site.register(Book, BookAdmin)
admin.site.register(Genre)
admin.site.register(BookInstance, BookInstanceAdmin)
