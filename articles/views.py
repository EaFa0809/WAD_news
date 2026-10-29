from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)

from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
)

from django.views.generic.detail import SingleObjectMixin

from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
)

from django.urls import reverse, reverse_lazy

from .models import Article
from .forms import CommentForm


# ------------------------------------
# ARTICLE LIST
# ------------------------------------

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = "article_list.html"


# ------------------------------------
# ARTICLE DETAIL - GET
# ------------------------------------

class CommentGet(DetailView):
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        return context


# ------------------------------------
# ARTICLE DETAIL - POST COMMENT
# ------------------------------------

class CommentPost(SingleObjectMixin, FormView):
    model = Article
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)

        comment.article = self.object
        comment.author = self.request.user

        comment.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        context = {
            "object": self.object,
            "article": self.object,
            "form": form,
        }
        return self.render_to_response(context)

    def get_success_url(self):
        article = self.object

        return reverse(
            "article_detail",
            kwargs={"pk": article.pk},
        )


# ------------------------------------
# ARTICLE DETAIL
# ------------------------------------

class ArticleDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()

        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()

        return view(request, *args, **kwargs)


# ------------------------------------
# CREATE ARTICLE
# ------------------------------------

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "article_new.html"

    fields = (
        "title",
        "body",
    )

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)


# ------------------------------------
# UPDATE ARTICLE
# ------------------------------------

class ArticleUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView,
):
    model = Article

    fields = (
        "title",
        "body",
    )

    template_name = "article_edit.html"

    def test_func(self):
        obj = self.get_object()

        return obj.author == self.request.user


# ------------------------------------
# DELETE ARTICLE
# ------------------------------------

class ArticleDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView,
):
    model = Article
    template_name = "article_delete.html"

    success_url = reverse_lazy("article_list")

    def test_func(self):
        obj = self.get_object()

        return obj.author == self.request.user