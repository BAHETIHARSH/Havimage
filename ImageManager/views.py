import os
from django.conf import settings
from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from django.contrib.staticfiles import finders

from .forms import ImageUploadForm,ImageEditForm
from .models import UploadedImage
import qrcode
import io
import base64

def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('image_list')
    else:
        form = ImageUploadForm()
    return render(request, 'upload_image.html', {'form': form})

from django.core.paginator import Paginator
from django.db.models import Q

def image_list(request):
    query = request.GET.get('q', '')
    filter_by = request.GET.get('filter', '')
    print(query,filter_by)
    images = UploadedImage.objects.all().order_by('-uploaded_at')
    print(images)
    if query:
        if filter_by == 'name':
            images = images.filter(title__icontains=query)
        elif filter_by == 'phone':
            images = images.filter(phone__icontains=query)
        elif filter_by == 'details':
            images = images.filter(details__icontains=query)
        elif filter_by == 'date':
            images = images.filter(uploaded_at__date=query)  # expects YYYY-MM-DD
        else:
            images = images.filter(
                Q(title__icontains=query) |
                Q(phone__icontains=query) |
                Q(details__icontains=query)
            )
    print(images)
    # paginator = Paginator(images, 6)  # 6 items per page
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    return render(request, 'image_list.html', {'images': images})


def image_detail(request, pk):
    image = get_object_or_404(UploadedImage, pk=pk)

    # Generate QR Code (URL to this detail page)
    url = request.build_absolute_uri()
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert QR image to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'image_detail.html', {
        'image': image,
        'qr_code': qr_code_base64
    })



def edit_image(request, pk):
    image = get_object_or_404(UploadedImage, pk=pk)
    if request.method == 'POST':
        form = ImageEditForm(request.POST, instance=image)
        if form.is_valid():
            form.save()
            return redirect('image_detail', pk=image.pk)
    else:
        form = ImageEditForm(instance=image)
    return render(request, 'edit_image.html', {'form': form, 'image': image})

def delete_image(request, pk):
    image = get_object_or_404(UploadedImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        return redirect('image_list')
    return render(request, 'delete_image.html', {'image': image})



# def download_image_with_details(request, pk):
#     obj = get_object_or_404(UploadedImage, pk=pk)

#     # Load the original image
#     img_path = obj.image.path
#     original_img = Image.open(img_path).convert("RGB")

#     # Generate QR Code (ID only)
#     qr = qrcode.QRCode(box_size=10, border=2)
#     qr.add_data(str(obj.id))
#     qr.make(fit=True)
#     qr_img = qr.make_image(fill_color="black", back_color="white")

#     # Create a new image (white background)
#     width = original_img.width + 400
#     height = max(original_img.height, 300)
#     new_img = Image.new("RGB", (width, height), "white")

#     # Paste original image
#     new_img.paste(original_img, (0, 0))

#     # Paste QR code on right side
#     qr_img = qr_img.resize((200, 200))
#     new_img.paste(qr_img, (original_img.width + 100, 50))

#     # Draw text (ID, Name, Date)
#     draw = ImageDraw.Draw(new_img)
#     font = ImageFont.load_default()
#     text_x = original_img.width + 50
#     text_y = 270

#     draw.text((text_x, text_y), f"ID: {obj.id}", fill="black", font=font)
#     draw.text((text_x, text_y + 20), f"Name: {obj.title or 'N/A'}", fill="black", font=font)
#     draw.text((text_x, text_y + 40), f"Date: {obj.uploaded_at.strftime('%Y-%m-%d')}", fill="black", font=font)

#     # Save to buffer
#     buffer = io.BytesIO()
#     new_img.save(buffer, format="JPEG")
#     buffer.seek(0)

#     # Return response
#     response = HttpResponse(buffer, content_type="image/jpeg")
#     response['Content-Disposition'] = f'attachment; filename="image_{obj.id}.jpg"'
#     return response



def download_image(request, pk):
    image_obj = get_object_or_404(UploadedImage, pk=pk)

    # Find background image from static
    bg_path = finders.find('images/poja_digital_bg.jpeg')

    # Open background image
    bg_image = Image.open(bg_path).convert("RGBA")

    # Create draw object
    draw = ImageDraw.Draw(bg_image)

    # Use default font
    font = ImageFont.load_default()

    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Roboto-Regular.ttf')

    font = ImageFont.truetype(font_path, 36)
    
    # Add text on left side
    draw.text((50, 50), f"ID: {image_obj.id}", font=font, fill="black")
    draw.text((50, 100), f"Title: {image_obj.title}", font=font, fill="black")
    draw.text((50, 150), f"Phone: {image_obj.phone}", font=font, fill="black")

    # Add QR on the right
    qr_data = f"{request.build_absolute_uri()}"  # Current page URL
    qr_img = qrcode.make(qr_data)
    qr_img = qr_img.resize((200, 200))  # Resize QR
    bg_image.paste(qr_img, (bg_image.width - 250, 50))

    final_image = bg_image.convert("RGB")

    # Save to memory
    buffer = io.BytesIO()
    final_image.save(buffer, format="JPEG")
    buffer.seek(0)

    # Return as downloadable file
    response = HttpResponse(buffer, content_type="image/jpeg")
    response['Content-Disposition'] = f'attachment; filename="image_{pk}.jpg"'
    return response