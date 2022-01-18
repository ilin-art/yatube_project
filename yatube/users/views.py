from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html' 


def user_contact(request):
    form = ContactForm()
    return render(request, 'users/contact.html', {'form': form})