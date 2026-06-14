from django.core.cache import cache
import qrcode
from io import BytesIO
from django.views.decorators.http import require_GET

def get_or_generate_qr_code(certificate_number, verification_url):
    """
    Get QR code from cache or generate new one
    Cache expires after 7 days
    """
    cache_key = f'qr_code_{certificate_number}'
    qr_data = cache.get(cache_key)
    
    if not qr_data:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_data = buffer.getvalue()
        buffer.close()
        
        # Cache for 7 days
        cache.set(cache_key, qr_data, 60 * 60 * 24 * 7)
    
    return qr_data


@require_GET
def certificate_qr_code(request, cert_number):
    """Generate QR code with caching"""
    try:
        certificate = StudentCertificate.objects.get(certificate_number=cert_number)
        
        verification_url = request.build_absolute_uri(
            reverse('certificate:verify_certificate', args=[certificate.certificate_number])
        )
        
        qr_data = get_or_generate_qr_code(certificate.certificate_number, verification_url)
        
        response = HttpResponse(qr_data, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="qr_{certificate.certificate_number}.png"'
        response['Cache-Control'] = 'public, max-age=604800'  # Browser cache for 7 days
        
        return response
        
    except StudentCertificate.DoesNotExist:
        return HttpResponse(status=404)