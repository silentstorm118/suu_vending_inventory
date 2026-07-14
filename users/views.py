from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import UserCreateForm, UserEditForm

User = get_user_model()


def admin_required(view_func):
    """Decorator: login + is_staff. Redirects non-admins to dashboard."""

    @login_required
    def wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect("dashboard:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapped


@admin_required
def user_list(request):
    """
    GET  /users/  — list all users, render create form.
    POST /users/  — create a new user.
    """
    users = User.objects.all().order_by("date_joined")
    create_form = UserCreateForm()

    if request.method == "POST":
        create_form = UserCreateForm(request.POST)
        if create_form.is_valid():
            create_form.save()
            return redirect("users:user_list")

    context = {
        "users": users,
        "create_form": create_form,
    }
    return render(request, "users/users.html", context)


@admin_required
def user_edit(request, pk):
    """
    POST /users/<pk>/edit/  — update name, email, role.
    """
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = UserEditForm(request.POST, user=user)
        if form.is_valid():
            form.save()

    return redirect("users:user_list")


@admin_required
def user_delete(request, pk):
    """
    POST /users/<pk>/delete/  — delete user, cannot delete self.
    """
    if request.method == "POST":
        user = get_object_or_404(User, pk=pk)
        if user.pk != request.user.pk:
            user.delete()

    return redirect("users:user_list")
