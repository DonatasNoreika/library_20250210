from django.shortcuts import render
from django.http import HttpResponse
from .models import Book, BookInstance, Author

# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status="g").count()
    num_authors = Author.objects.all().count()
    my_context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,

    }
    return render(request, template_name="index.html", context=my_context)
    # return HttpResponse(f"<h1>Labas, pasauli! Laba diena</h1><p>{num_books}, {num_instances}, {num_instances_available}, {num_authors}</p>")