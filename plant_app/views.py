import os
import google.generativeai as genai
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import base64

genai.configure(api_key=settings.GEMINI_API_KEY)

def get_plant_info(image_path):
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode('utf-8')
            }
        ]
    
    prompt = """
    Analyze this plant image and provide the following information:
    1. Plant Name (Common and Scientific)
    2. Plant Type
    3. Growing Conditions
    4. Care Instructions
    5. Interesting Facts
    Format the response in a structured way.
    """
    
    response = model.generate_content([prompt, image_parts[0]])
    return response.text

def home(request):
    context = {
        'plant_info': None,
        'image_url': None
    }
    
    if request.method == 'POST' and request.FILES.get('plant_image'):
        plant_image = request.FILES['plant_image']
        fs = FileSystemStorage()
        filename = fs.save(plant_image.name, plant_image)
        image_path = fs.path(filename)
        
        try:
            plant_info = get_plant_info(image_path)
            context['plant_info'] = plant_info
            context['image_url'] = fs.url(filename)
        except Exception as e:
            context['error'] = str(e)
            
    return render(request, 'plant_app/home.html', context)
