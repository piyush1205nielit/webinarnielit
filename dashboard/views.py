from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count,Sum, Q
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from registration.models import Student, Certificate
from course.models import Course, Centre
from datetime import datetime, timedelta
import json
import pandas as pd
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from public.models import Announcement, CarouselImage
from .forms import AnnouncementForm, CarouselImageForm
from datetime import datetime, timedelta, date
import pandas as pd
from django.template.loader import get_template

from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.platypus import ( SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer )
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet



def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def dashboard_index(request):
    total_students = Student.objects.count()
    total_courses = Course.objects.count()
    total_centres = Centre.objects.count()
    approved_students = Student.objects.filter(is_approved=True).count()
    pending_approvals = Student.objects.filter(is_approved=False, status='confirmed').count()
    
    # Today's and Yesterday's Registrations
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    today_registrations = Student.objects.filter(registration_date__date=today).count()
    yesterday_registrations = Student.objects.filter(registration_date__date=yesterday).count()
    weekly_registrations = Student.objects.filter(registration_date__date__gte=week_ago).count()
    monthly_registrations = Student.objects.filter(registration_date__date__gte=month_ago).count()
    

     # Active Courses with enrollment counts
    active_courses = Course.objects.filter(is_active=True, course_status__in=['open', 'active', 'ongoing']).annotate(
        student_count=Count('students', filter=Q(students__status__in=['pending', 'confirmed']))
    ).order_by('-student_count')[:10]

    # Add fill_rate to each course
    for course in active_courses:
        if course.max_seats and course.max_seats > 0:
            course.fill_rate = min(int((course.student_count / course.max_seats) * 100), 100)
        else:
            course.fill_rate = 0

    # Weekly data for mini chart
    weekly_dates = []
    weekly_counts = []
    for i in range(7, 0, -1):
        day = today - timedelta(days=i)
        count = Student.objects.filter(registration_date__date=day).count()
        weekly_dates.append(day.strftime('%d/%m'))
        weekly_counts.append(count)
    
    # Active Centres with course and student data
    active_centres = []
    for centre in Centre.objects.all():
        courses = centre.available_courses.filter(is_active=True)
        total_students = Student.objects.filter(preferred_centre=centre, status__in=['pending', 'confirmed']).count()
        max_capacity = sum([c.max_seats for c in courses if c.max_seats]) or 1
        occupancy_rate = int((total_students / max_capacity) * 100) if max_capacity else 0
        
        active_centres.append({
            'centre_name': centre.centre_name,
            'centre_contact': centre.centre_contact,
            'courses': courses[:3],  # Limit to 3 courses
            'total_students': total_students,
            'occupancy_rate': min(occupancy_rate, 100)
        })
    
    # Course Mode Statistics
    course_mode_stats = Course.objects.values('mode').annotate(count=Count('id'))
    mode_labels = []
    mode_counts = []
    mode_map = dict(Course.MODE_CHOICES)
    for stat in course_mode_stats:
        mode_labels.append(mode_map.get(stat['mode'], stat['mode']))
        mode_counts.append(stat['count'])
    
    # Registration trends for last 30 days
    dates = []
    registration_counts = []
    for i in range(30):
        day = today - timedelta(days=i)
        count = Student.objects.filter(registration_date__date=day).count()
        dates.append(day.strftime('%d %b'))
        registration_counts.append(count)
    
    dates.reverse()
    registration_counts.reverse()
    
    # Recent registrations
    recent_registrations = Student.objects.all().select_related('course_enrolled', 'preferred_centre')[:10]
    
    # Course enrollment stats for chart
    course_enrollment_stats = Course.objects.annotate(student_count=Count('students')).order_by('-student_count')[:5]
    
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
        'approved_count': approved_students,

        # New data
        'today_registrations': today_registrations,
        'yesterday_registrations': yesterday_registrations,
        'weekly_registrations': weekly_registrations,
        'monthly_registrations': monthly_registrations,
        'active_courses': active_courses,
        'active_courses_count': active_courses.count(),
        'active_centres': active_centres,
        'recent_students_count': monthly_registrations,
        'course_mode_stats': course_mode_stats,
        'mode_labels': mode_labels,
        'mode_counts': mode_counts,
        'dates': dates,
        'registration_counts': registration_counts,
        'weekly_dates': weekly_dates,
        'weekly_counts': weekly_counts,
    }
    return render(request, 'dashboard/index.html', context)




@user_passes_test(is_admin)
def students_list(request):

    students = Student.objects.select_related(
        'course_enrolled',
        'preferred_centre'
    ).all().order_by('-registration_date')

    # ───────────────── Filters ───────────────── #

    course_filter = request.GET.get('course')
    center_filter = request.GET.get('center')
    status_filter = request.GET.get('status')
    search_query = request.GET.get('search')

    if course_filter:
        students = students.filter(course_enrolled_id=course_filter)

    if center_filter:
        students = students.filter(preferred_centre_id=center_filter)

    if status_filter:
        students = students.filter(status=status_filter)

    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(email_id__icontains=search_query) |
            Q(registration_number__icontains=search_query)
        )

    # ───────────────── Export ───────────────── #

    export_type = request.GET.get("export")

    # ================= EXCEL EXPORT ================= #

    if export_type == "excel":

        wb = Workbook()
        ws = wb.active
        ws.title = "Students"

        headers = [
            "Registration No", "Student Name", "Father Name", "Mobile", "Email", "Course", "Center", "Status", "Certificate", "Registration Date",
        ]
        ws.append(headers)

        # Header Styling
        for cell in ws[1]:
            cell.font = Font(bold=True)

        # Data Rows
        for student in students:

            ws.append([
                student.registration_number,
                student.name,
                student.father_name,
                student.mobile_number,
                student.email_id,
                student.course_enrolled.course_name if student.course_enrolled else "",
                student.preferred_centre.centre_name if student.preferred_centre else "",
                student.get_status_display(),
                "Issued" if student.is_approved else "Pending",
                student.registration_date.strftime("%d-%m-%Y"),
            ])

        # Column Widths
        column_widths = {
            "A": 22, "B": 28, "C": 28, "D": 18, "E": 35, "F": 30, "G": 25, "H": 18, "I": 18, "J": 18,
        }

        for column, width in column_widths.items():
            ws.column_dimensions[column].width = width

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = (
            'attachment; filename="students.xlsx"'
        )

        wb.save(response)
        return response

    # ================= PDF EXPORT ================= #

    if export_type == "pdf":

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="students.pdf"'

        buffer = BytesIO()

        doc = SimpleDocTemplate( buffer, pagesize=landscape(A4), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph(
            "<b>Students Report</b>",
            styles['Title']
        )

        elements.append(title)
        elements.append(Spacer(1, 12))

        data = [[
            "Reg No", "Student", "Mobile", "Email", "Course", "Center", "Status", "Certificate", "Date",
        ]]

        for student in students:

            data.append([
                student.registration_number,
                student.name,
                student.mobile_number,
                student.email_id,
                student.course_enrolled.course_name if student.course_enrolled else "",
                student.preferred_centre.centre_name if student.preferred_centre else "",
                student.get_status_display(),
                "Issued" if student.is_approved else "Pending",
                student.registration_date.strftime("%d-%m-%Y"),
            ])

        table = Table(
            data,
            repeatRows=1,
            colWidths=[ 80, 100, 75, 130, 110, 90, 60, 70, 70 ]
        )

        table.setStyle(TableStyle([

            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),

            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),

            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                colors.whitesmoke,
                colors.HexColor("#f8fafc")
            ]),

            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),

        ]))

        elements.append(table)

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        response.write(pdf)

        return response

    # ───────────────── Pagination ───────────────── #

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


@user_passes_test(is_admin)
def announcement_list(request):
    """List all announcements with drag-drop ordering"""
    announcements = Announcement.objects.all()
    return render(request, 'dashboard/announcement_list.html', {'announcements': announcements})

@user_passes_test(is_admin)
def announcement_create(request):
    """Create new announcement"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('dashboard:announcement_list')
    else:
        form = AnnouncementForm()
    
    return render(request, 'dashboard/announcement_form.html', {'form': form, 'title': 'Create Announcement'})

@user_passes_test(is_admin)
def announcement_edit(request, pk):
    """Edit announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('dashboard:announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'dashboard/announcement_form.html', {'form': form, 'title': 'Edit Announcement'})

@user_passes_test(is_admin)
def announcement_delete(request, pk):
    """Delete announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully!')
        return redirect('dashboard:announcement_list')
    
    return render(request, 'dashboard/announcement_confirm_delete.html', {'object': announcement})

@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_admin)
def announcement_reorder(request):
    """Reorder announcements via drag and drop"""
    try:
        data = json.loads(request.body)
        for item in data.get('items', []):
            Announcement.objects.filter(id=item['id']).update(order=item['order'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ==================== CAROUSEL VIEWS ====================

@user_passes_test(is_admin)
def carousel_list(request):
    """List all carousel images with drag-drop ordering"""
    images = CarouselImage.objects.all()
    return render(request, 'dashboard/carousel_list.html', {'images': images})

@user_passes_test(is_admin)
def carousel_create(request):
    """Add new carousel image"""
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            messages.success(request, 'Carousel image added successfully!')
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm()
    
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'title': 'Add Carousel Image'})

@user_passes_test(is_admin)
def carousel_edit(request, pk):
    """Edit carousel image"""
    image = get_object_or_404(CarouselImage, pk=pk)
    
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carousel image updated successfully!')
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm(instance=image)
    
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'title': 'Edit Carousel Image'})

@user_passes_test(is_admin)
def carousel_delete(request, pk):
    """Delete carousel image"""
    image = get_object_or_404(CarouselImage, pk=pk)
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Carousel image deleted successfully!')
        return redirect('dashboard:carousel_list')
    
    return render(request, 'dashboard/carousel_confirm_delete.html', {'object': image})

@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_admin)
def carousel_reorder(request):
    """Reorder carousel images via drag and drop"""
    try:
        data = json.loads(request.body)
        for item in data.get('items', []):
            CarouselImage.objects.filter(id=item['id']).update(order=item['order'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})