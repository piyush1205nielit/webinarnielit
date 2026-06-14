# certificate/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse  # Add this import
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from registration.models import Student
from .models import CertificateDesign, StudentCertificate
from .forms import CertificateDesignForm, IssueCertificateForm
import qrcode
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control

def is_admin(user):
    return user.is_authenticated and user.is_staff


# ==================== STUDENT VIEWS ====================

def view_certificate(request, reg_number):
    """View certificate in HTML format"""
    try:
        student = get_object_or_404(Student, registration_number=reg_number)
        if not student.is_approved:
            messages.error(request, 'Certificate not available yet.')
            return redirect('registration:user_profile')
        
        certificate = StudentCertificate.objects.get(student=student)
        design = certificate.design or CertificateDesign.objects.filter(is_active=True).first()
        
        return render(request, 'certificate/view_certificate.html', {
            'certificate': certificate,
            'student': student,
            'design': design
        })
    except (Student.DoesNotExist, StudentCertificate.DoesNotExist):
        messages.error(request, 'Certificate not found.')
        return redirect('registration:user_profile')


def verify_certificate(request, cert_number):
    """Public certificate verification - Simple and clean"""
    try:
        certificate = StudentCertificate.objects.get(certificate_number=cert_number)
        
        context = {
            'is_valid': True,
            'certificate': certificate,
            'student': certificate.student,
        }
    except StudentCertificate.DoesNotExist:
        context = {
            'is_valid': False,
            'certificate_number': cert_number,
        }
    return render(request, 'certificate/verify_certificate.html', context)


@require_GET
@cache_control(max_age=86400)
def certificate_qr_code(request, cert_number):
    """
    Generate QR code dynamically without saving to disk
    """
    try:
        from django.urls import reverse  # Import here if not at top
        certificate = StudentCertificate.objects.get(certificate_number=cert_number)
        
        # Build verification URL
        verification_url = request.build_absolute_uri(
            reverse('certificate:verify_certificate', args=[certificate.certificate_number])
        )
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO buffer
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Return as HTTP response
        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="qr_{certificate.certificate_number}.png"'
        buffer.close()
        
        return response
        
    except StudentCertificate.DoesNotExist:
        return HttpResponse(status=404)


# ==================== ADMIN VIEWS ====================

@user_passes_test(is_admin)
def design_list(request):
    """List all certificate designs"""
    designs = CertificateDesign.objects.all()
    return render(request, 'certificate/admin/design_list.html', {'designs': designs})


@user_passes_test(is_admin)
def design_create(request):
    """Create new certificate design"""
    if request.method == 'POST':
        form = CertificateDesignForm(request.POST, request.FILES)
        if form.is_valid():
            design = form.save()
            messages.success(request, f'Certificate design "{design.certificate_title}" created successfully!')
            return redirect('certificate:design_list')
    else:
        form = CertificateDesignForm()
    
    return render(request, 'certificate/admin/design_form.html', {
        'form': form,
        'title': 'Create Certificate Design',
    })


@user_passes_test(is_admin)
def design_edit(request, pk):
    """Edit certificate design"""
    design = get_object_or_404(CertificateDesign, pk=pk)
    
    if request.method == 'POST':
        form = CertificateDesignForm(request.POST, request.FILES, instance=design)
        if form.is_valid():
            form.save()
            messages.success(request, f'Certificate design "{design.certificate_title}" updated successfully!')
            return redirect('certificate:design_list')
    else:
        form = CertificateDesignForm(instance=design)
    
    return render(request, 'certificate/admin/design_form.html', {
        'form': form,
        'title': 'Edit Certificate Design',
        'design': design
    })


@user_passes_test(is_admin)
def design_preview(request, pk):
    """Preview certificate design"""
    design = get_object_or_404(CertificateDesign, pk=pk)
    return render(request, 'certificate/admin/design_preview.html', {'design': design})


@user_passes_test(is_admin)
def design_delete(request, pk):
    """Delete certificate design"""
    design = get_object_or_404(CertificateDesign, pk=pk)
    
    if request.method == 'POST':
        design_name = design.certificate_title
        design.delete()
        messages.success(request, f'Certificate design "{design_name}" deleted successfully!')
        return redirect('certificate:design_list')
    
    return render(request, 'certificate/admin/design_confirm_delete.html', {'design': design})


@user_passes_test(is_admin)
def issue_certificate(request, student_id):
    """Manually issue certificate for a student"""
    student = get_object_or_404(Student, id=student_id)
    design = CertificateDesign.objects.filter(is_active=True).first()
    
    if request.method == 'POST':
        form = IssueCertificateForm(request.POST)
        if form.is_valid():
            certificate, created = StudentCertificate.objects.update_or_create(
                student=student,
                defaults={
                    'design': design,
                    'issue_date': form.cleaned_data['issue_date'],
                    'issued_by': form.cleaned_data['issued_by'] or 'NIELIT Administration',
                    'remarks': form.cleaned_data['remarks'],
                }
            )
            
            # Update student status
            student.is_approved = True
            student.status = 'completed'
            student.save()
            
            messages.success(request, f'Certificate issued to {student.name}! Certificate No: {certificate.certificate_number}')
            return redirect('dashboard:students_list')
    else:
        form = IssueCertificateForm(initial={
            'issue_date': timezone.now().date(),
            'issued_by': request.user.get_full_name() or 'NIELIT Administration'
        })
    
    return render(request, 'certificate/admin/issue_certificate.html', {
        'form': form,
        'student': student,
        'design': design
    })



@user_passes_test(is_admin)
def issued_certificates_list(request):
    """List all issued certificates"""
    from certificate.models import StudentCertificate

    certificates = StudentCertificate.objects.select_related(
        'student',
        'student__course_enrolled',
        'student__preferred_centre',
        'design'
    ).all().order_by('-issue_date')

    search = request.GET.get('search')
    if search:
        certificates = certificates.filter(
            Q(certificate_number__icontains=search) |
            Q(student__name__icontains=search) |
            Q(student__registration_number__icontains=search) |
            Q(student__mobile_number__icontains=search)
        )

    paginator = Paginator(certificates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'certificate/admin/issued_list.html', {
        'page_obj': page_obj,
        'search': search or '',
    })