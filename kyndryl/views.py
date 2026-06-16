from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from .models import KyndrylRegistration
from .forms import KyndrylRegistrationForm


class RegistrationCreateView(CreateView):
    model = KyndrylRegistration
    form_class = KyndrylRegistrationForm
    template_name = 'kyndryl/register.html'

    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            f'Registration successful! Your registration number is {self.object.registration_number}.'
        )
        return redirect(
            reverse('kyndryl:register_success', kwargs={
                'registration_number': self.object.registration_number
            })
        )

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class RegistrationSuccessView(TemplateView):
    template_name = 'kyndryl/register_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_number = self.kwargs.get('registration_number')
        context['registration'] = get_object_or_404(
            KyndrylRegistration, registration_number=registration_number
        )
        return context


class ProfileDetailView(DetailView):
    model = KyndrylRegistration
    template_name = 'kyndryl/profile_detail.html'
    context_object_name = 'registration'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['beneficiary_list'] = obj.get_beneficiary_belonging_display_list()
        return context


class ProfileUpdateView(UpdateView):
    model = KyndrylRegistration
    form_class = KyndrylRegistrationForm
    template_name = 'kyndryl/profile_edit.html'
    context_object_name = 'registration'

    def get_success_url(self):
        return reverse('kyndryl:profile_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class RegistrationListView(ListView):
    model = KyndrylRegistration
    template_name = 'kyndryl/registration_list.html'
    context_object_name = 'registrations'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q', '').strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(email_id__icontains=search) |
                Q(mobile_number__icontains=search) |
                Q(registration_number__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context