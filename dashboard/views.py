from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from registration.models import Student, Certificate
from course.models import Course, Centre
from datetime import datetime, timedelta
import json
import pandas as pd
from io import BytesIO

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def dashboard_index(request):
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_centres = Centre.objects.count()
    approved_students = Student.objects.filter(is_approved=True).count()
    pending_approvals = Student.objects.filter(is_approved=False, status='confirmed').count()
    
    recent_registrations = Student.objects.all().select_related('course_enrolled', 'preferred_centre')[:10]
    
    course_enrollment_stats = Course.objects.annotate(
        student_count=Count('students')
    ).order_by('-student_count')[:5]
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_centres': total_centres,
        'approved_students': approved_students,
        'pending_approvals': pending_approvals,
        'pending_approvals_count': pending_approvals,
        'recent_registrations': recent_registrations,
        'course_enrollment_stats': course_enrollment_stats,
        'now': datetime.now(),
    }
    return render(request, 'dashboard/index.html', context)

@user_passes_test(is_admin)
def students_list(request):
    students = Student.objects.select_related('course_enrolled', 'preferred_centre').all()
    
    course_filter = request.GET.get('course')
    center_filter = request.GET.get('center')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')
    
    if course_filter and course_filter != '':
        students = students.filter(course_enrolled_id=course_filter)
    if center_filter and center_filter != '':
        students = students.filter(preferred_centre_id=center_filter)
    if status_filter and status_filter != '':
        students = students.filter(status=status_filter)
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(email_id__icontains=search_query) |
            Q(registration_number__icontains=search_query)
        )
    
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    courses = Course.objects.all()
    centres = Centre.objects.all()
    
    context = {
        'page_obj': page_obj,
        'courses': courses,
        'centres': centres,
        'selected_course': course_filter,
        'selected_center': center_filter,
        'selected_status': status_filter,
        'search_query': search_query,
    }
    return render(request, 'dashboard/students_list.html', context)

@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'dashboard/student_detail.html', {'student': student})

@user_passes_test(is_admin)
def approve_certificate(request):
    students = Student.objects.filter(
        status='confirmed', 
        is_approved=False
    ).select_related('course_enrolled', 'preferred_centre')
    
    context = {
        'students': students,
        'pending_approvals_count': students.count(),
    }
    return render(request, 'dashboard/approve_certificate.html', context)

@user_passes_test(is_admin)
def approve_bulk(request):
    """Bulk approve students for certificate"""
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        if student_ids:
            count = 0
            for student_id in student_ids:
                try:
                    student = Student.objects.get(id=student_id)
                    if student.status == 'confirmed' and not student.is_approved:
                        student.is_approved = True
                        student.status = 'completed'
                        student.save()
                        Certificate.objects.get_or_create(student=student)
                        count += 1
                except Student.DoesNotExist:
                    continue
            messages.success(request, f'{count} student(s) have been approved for certification!')
        else:
            messages.warning(request, 'No students selected for approval.')
        return redirect('dashboard:students_list')
    return redirect('dashboard:students_list')

@user_passes_test(is_admin)
def update_status_bulk(request):
    """Bulk update student status"""
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        new_status = request.POST.get('status')
        
        if student_ids and new_status:
            count = 0
            for student_id in student_ids:
                try:
                    student = Student.objects.get(id=student_id)
                    student.status = new_status
                    student.save()
                    count += 1
                except Student.DoesNotExist:
                    continue
            messages.success(request, f'{count} student(s) status updated to {new_status}!')
        else:
            messages.warning(request, 'Please select students and a status.')
        return redirect('dashboard:students_list')
    return redirect('dashboard:students_list')

@user_passes_test(is_admin)
def delete_bulk(request):
    """Bulk delete students"""
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        if student_ids:
            # Delete certificates first (due to foreign key)
            Certificate.objects.filter(student_id__in=student_ids).delete()
            # Delete students
            count = Student.objects.filter(id__in=student_ids).delete()[0]
            messages.success(request, f'{count} student(s) have been deleted successfully!')
        else:
            messages.warning(request, 'No students selected for deletion.')
        return redirect('dashboard:students_list')
    return redirect('dashboard:students_list')

@user_passes_test(is_admin)
def update_status(request):
    """Single student status update via AJAX"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        new_status = request.POST.get('status')
        try:
            student = Student.objects.get(id=student_id)
            student.status = new_status
            student.save()
            return JsonResponse({'success': True, 'message': f'Status updated to {new_status}!'})
        except Student.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Student not found!'})
    return JsonResponse({'success': False, 'message': 'Invalid request!'})

@user_passes_test(is_admin)
def reports(request):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    dates = []
    counts = []
    current_date = start_date
    while current_date <= end_date:
        count = Student.objects.filter(registration_date__date=current_date).count()
        dates.append(current_date.strftime('%Y-%m-%d'))
        counts.append(count)
        current_date += timedelta(days=1)
    
    categories = Student.objects.values('category').annotate(count=Count('id'))
    category_labels = []
    category_data = []
    category_map = dict(Student.CATEGORY_CHOICES)
    for c in categories:
        category_labels.append(category_map.get(c['category'], c['category']))
        category_data.append(c['count'])
    
    course_stats = Course.objects.annotate(student_count=Count('students')).filter(student_count__gt=0)
    course_labels = [course.course_name for course in course_stats]
    course_data = [course.student_count for course in course_stats]
    
    context = {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'course_labels': json.dumps(course_labels),
        'course_data': json.dumps(course_data),
        'total_students': Student.objects.count(),
        'approved_count': Student.objects.filter(is_approved=True).count(),
        'pending_count': Student.objects.filter(is_approved=False, status='confirmed').count(),
    }
    return render(request, 'dashboard/reports.html', context)

@user_passes_test(is_admin)
def export_students_excel(request):
    """Export students data to Excel"""
    students = Student.objects.select_related('course_enrolled', 'preferred_centre').all().values(
        'registration_number', 'name', 'mobile_number', 'email_id', 'date_of_birth', 
        'category', 'father_name', 'course_enrolled__course_name', 'preferred_centre__centre_name',
        'is_approved', 'status', 'registration_date'
    )
    
    df = pd.DataFrame(list(students))
    df.columns = ['Registration Number', 'Name', 'Mobile Number', 'Email', 'Date of Birth', 
                  'Category', 'Father Name', 'Course Enrolled', 'Preferred Centre', 
                  'Certificate Status', 'Registration Status', 'Registration Date']
    
    df['Certificate Status'] = df['Certificate Status'].apply(lambda x: 'Issued' if x else 'Pending')
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Students Report', index=False)
    
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=students_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response

@user_passes_test(is_admin)
def export_students_pdf(request):
    """Export students data to PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    students = Student.objects.select_related('course_enrolled', 'preferred_centre').all()[:100]
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=students_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=30)
    
    elements.append(Paragraph("NIELIT Students Registration Report", title_style))
    elements.append(Spacer(1, 20))
    
    data = [['Reg Number', 'Name', 'Mobile', 'Email', 'Course', 'Center', 'Status']]
    for student in students:
        data.append([
            student.registration_number,
            student.name,
            student.mobile_number,
            student.email_id[:20],
            student.course_enrolled.course_name[:25],
            student.preferred_centre.centre_name[:20],
            'Approved' if student.is_approved else 'Pending'
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
    ]))
    
    elements.append(table)
    doc.build(elements)
    return response