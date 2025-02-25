from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_protect
from .models import Book, BookInstance, Author, BookReview
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import password_validation
from django.views.generic.edit import FormMixin
from .forms import BookReviewForm, UserUpdateForm, ProfileUpdateForm, BookInstanceCreateUpdateForm
from django.contrib.auth.decorators import login_required


# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status="g").count()
    num_authors = Author.objects.all().count()
    num_visits = request.session.get("num_visits", 1)
    request.session['num_visits'] = num_visits + 1

    my_context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
    }
    return render(request, template_name="index.html", context=my_context)


def authors(request):
    authors = Author.objects.all()
    paginator = Paginator(authors, per_page=5)
    page_number = request.GET.get("page")
    paged_author = paginator.get_page(page_number)
    context = {
        'authors': paged_author,
    }
    return render(request, template_name="authors.html", context=context)


def author(request, author_id):
    author = Author.objects.get(pk=author_id)
    context = {
        "author": author,
    }
    return render(request, template_name="author.html", context=context)


class BookListView(generic.ListView):
    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate_by = 9


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = "book.html"
    context_object_name = "book"
    form_class = BookReviewForm

    def get_success_url(self):
        return reverse("book", kwargs={"pk": self.object.pk})

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super().form_valid(form)


def search(request):
    query = request.GET.get("query")
    book_search_results = Book.objects.filter(
        Q(title__icontains=query) | Q(summary__icontains=query) | Q(author__first_name__icontains=query) | Q(
            author__last_name__icontains=query))
    author_search_results = Author.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(description__icontains=query))
    context = {
        "query": query,
        "books": book_search_results,
        "authors": author_search_results,
    }
    return render(request, template_name="search.html", context=context)


class MyBookInstanceListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "my_copies.html"
    context_object_name = "copies"

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user)


@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, message=f'Vartotojo vardas {username} užimtas!')
                return redirect("register")
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, message=f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect("register")
                else:
                    try:
                        password_validation.validate_password(password)
                    except password_validation.ValidationError as err:
                        for error in err:
                            messages.error(request, error)
                            return redirect("register")
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'Vartotojas {username} užregistruotas!')
                    return redirect("login")
        else:
            messages.error(request, message="Slaptažodžiai nesutampa!")
            return redirect("register")

    return render(request, template_name="register.html")


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        new_email = request.POST["email"]
        if not new_email:
            messages.error(request, "El. paštas negali būti tuščias!")
            return redirect("profile")
        if request.user.email != new_email and User.objects.filter(email=new_email).exists():
            messages.error(request, message=f'Vartotojas su el. paštu {new_email} jau užregistruotas!')
            return redirect("profile")
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.info(request, "Profilis atnaujintas")
            return redirect("profile")
    context = {
        "u_form": UserUpdateForm(instance=request.user),
        "p_form": ProfileUpdateForm(instance=request.user.profile),
    }
    return render(request, template_name="profile.html", context=context)


class BookInstanceListView(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = BookInstance
    template_name = "instances.html"
    context_object_name = "instances"

    def test_func(self):
        return self.request.user.profile.is_employee


class BookInstanceDetailView(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = BookInstance
    template_name = "instance.html"
    context_object_name = "instance"

    def test_func(self):
        return self.request.user.profile.is_employee


class BookInstanceCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = BookInstance
    # fields = ['book', 'status', 'due_back', 'reader']
    template_name = "instance_form.html"
    success_url = "/library/instances/"
    form_class = BookInstanceCreateUpdateForm

    def test_func(self):
        return self.request.user.profile.is_employee


class BookInstanceUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = BookInstance
    # fields = ['book', 'status', 'due_back', 'reader']
    template_name = "instance_form.html"
    form_class = BookInstanceCreateUpdateForm
    # success_url = "/library/instances/"

    def get_success_url(self):
        return reverse('instance', kwargs={"pk": self.object.pk})

    def test_func(self):
        return self.request.user.profile.is_employee


class BookInstanceDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = BookInstance
    success_url = "/library/instances/"
    context_object_name = "instance"
    template_name = "instance_delete.html"

    def test_func(self):
        return self.request.user.profile.is_employee


class BookReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = BookReview
    fields = ['content']
    template_name = "review_update.html"
    # success_url = "/library/books/"

    def get_success_url(self):
        return reverse('book', kwargs={"pk": self.object.book.pk})

    def test_func(self):
        return self.get_object().reviewer == self.request.user


class BookReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = BookReview
    context_object_name = "review"
    template_name = "review_delete.html"

    def get_success_url(self):
        return reverse('book', kwargs={"pk": self.object.book.pk})

    def test_func(self):
        return self.get_object().reviewer == self.request.user