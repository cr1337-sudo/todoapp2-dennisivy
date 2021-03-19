from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import *
# Create your views here.

# Si uso CBV automaticamente crea un usuario en el panel admin y la pagina


class CustomLoginView(LoginView):
    template_name = "base/login.html"
    fields = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks")


class RegisterPage(FormView):
    template_name = "base/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasks")

# Si el formualario es valido hace login automatico
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
# Sobre escribir el metodo get, si alguien quiere acceder a "Register"
# Y está logeado, se lo va a mandar a tasks

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tasks")


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = "tasks"
    # Restringe lo que un usuario puede ver, con esto solo ve las tareas que el publica

    def get_context_data(self, **kwargs):
        # El contexto hereda de la clase padre
        context = super().get_context_data(**kwargs)
        # Context["tasks"] porque antes el context object fue customizado
        context["tasks"] = context["tasks"].filter(user=self.request.user)
        context["count"] = context["tasks"].filter(complete=False).count()

        search_input = self.request.GET.get("search-area") or ""
        if search_input:
            context["tasks"] = context["tasks"].filter(
                title__icontains=search_input)
            #context["search_inpiut"] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"
    template_name = "base/task.html"


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")

    # Hace que un usuario pueda publicar un post SOLO con su usuario y no con otro
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ["title", "description", "complete"]
    success_url = reverse_lazy("tasks")


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = "task"
    success_url = reverse_lazy("tasks")
