import cv2
import numpy as np
import torch
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from ultralytics import YOLO

from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
import ssl

# Fixed -> RuntimeError: It looks like there is no internet connection and the repo could not be found in the cache
ssl._create_default_https_context = ssl._create_unverified_context

# Global variables for class IDs
BOOK_CLASS_ID = 73
BILLBOARD_CLASS_ID = 80

# Load the models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
custom_model_path = os.path.join(BASE_DIR, 'billboard_weights', 'best.pt')
default_book_model_path = os.path.join(BASE_DIR, 'default_weights', 'yolov5mu.pt')

# Load the default YOLOv8 model for books
book_model = YOLO(default_book_model_path)  # Adjust path to your local model

# Load the custom YOLOv5 model for billboards
billboard_model = torch.hub.load('ultralytics/yolov5', 'custom', path=custom_model_path)

def load_image_into_numpy_array(path):
    return np.array(cv2.imread(path))

def calculate_scale_factor(book_box, known_width, known_height, image_np, unit='mm'):
    if unit == 'cm':
        known_width *= 10  # convert cm to mm
        known_height *= 10  # convert cm to mm

    (startY, startX, endY, endX) = book_box
    (h, w) = image_np.shape[:2]
    (startX, startY, endX, endY) = (startX * w, startY * h, endX * w, endY * h)

    book_width_pixels = endX - startX
    book_height_pixels = endY - startY

    scale_width = known_width / book_width_pixels
    scale_height = known_height / book_height_pixels

    # Take the average scale factor for width and height
    scale = (scale_width + scale_height) / 2

    return scale

@extend_schema(
    description="The endpoint is used to detect and measure billboards and return dimensions.",
    summary='Detect and measure billboard endpoint',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'book_width': {'type': 'integer', 'description': 'Enter the book width'},
                'book_height': {'type': 'integer', 'description': 'Enter the book height'},
                'book_unit': {'type': 'string', 'description': 'Enter the book unit'},
                'book_image': {'type': 'string', 'format': 'binary', 'description': 'Upload book reference image'},
                'billboard_image': {'type': 'string', 'format': 'binary', 'description': 'Upload billboard image'},
            },
            'required': ['book_width', 'book_height', 'book_image', 'billboard_image']
        }
    },
    responses={
        200: OpenApiResponse(
            description="JSON response containing billboard dimension and position information",
            examples={
                "application/json": {
                    "message": "File uploaded successfully.",
                    "data": {
                        "width": 200,
                        "height": 182,
                        "x": 26.50,
                        "y": 10.75
                    }
                }
            },
        )
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
def process_images(request):
    if request.method == 'POST' and request.FILES.get('book_image') and request.FILES.get('billboard_image'):
        book_image_file = request.FILES['book_image']
        billboard_image_file = request.FILES['billboard_image']
        book_width = float(request.POST.get('book_width', ''))
        book_height = float(request.POST.get('book_height', ''))
        book_unit = request.POST.get('book_unit', 'mm')

        book_image_path = default_storage.save('book.jpg', ContentFile(book_image_file.read()))
        billboard_image_path = default_storage.save('billboard.jpg', ContentFile(billboard_image_file.read()))
        book_image_full_path = os.path.join(default_storage.location, book_image_path)
        billboard_image_full_path = os.path.join(default_storage.location, billboard_image_path)

        # Process the book image to find the reference object
        book_image_np = load_image_into_numpy_array(book_image_full_path)
        results = book_model(book_image_full_path)

        # Debugging: Print all detection results
        print(f"Results object for book image: {results}")

        # YOLOv8 specific handling
        if isinstance(results, list):
            results = results[0]  # Assume single image

        # Get detection results for the book
        book_detections = []
        for box, cls, score in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy().astype(int), results.boxes.conf.cpu().numpy()):
            if cls == BOOK_CLASS_ID and score > 0.3:  # Adjust the threshold if needed
                book_detections.append((box, cls, score))

        # Print all detected class IDs
        for box, cls, score in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy().astype(int), results.boxes.conf.cpu().numpy()):
            print(f"Detected class ID: {cls}, Score: {score}")

        if not book_detections:
            os.remove(book_image_full_path)
            os.remove(billboard_image_full_path)
            return JsonResponse({'error': 'Book not detected'}, status=400)

        book_box = book_detections[0][0]
        scale = calculate_scale_factor(book_box, book_width, book_height, book_image_np, book_unit)

        # Process the billboard image
        billboard_image_np = load_image_into_numpy_array(billboard_image_full_path)
        results = billboard_model(billboard_image_full_path)

        # Debugging: Print all detection results
        print(f"Results object for billboard image: {results}")

        # YOLOv5 specific handling
        if isinstance(results, torch.Tensor):
            results = results.pandas().xyxy[0].to_dict(orient="records")
        else:
            results = results.xyxy[0].cpu().numpy()  # Get the results in a numpy array

        # Get detection results for the billboard
        billboard_detections = []
        for detection in results:
            if isinstance(detection, dict):  # YOLOv5 handling
                cls = int(detection['class'])
                score = detection['confidence']
                if cls == BILLBOARD_CLASS_ID and score > 0.3:  # Adjust the threshold if needed
                    box = [detection['xmin'], detection['ymin'], detection['xmax'], detection['ymax']]
                    billboard_detections.append((box, cls, score))
            else:  # YOLOv8 handling
                box = detection[:4]
                cls = int(detection[5])
                score = detection[4]
                if cls == BILLBOARD_CLASS_ID and score > 0.3:
                    billboard_detections.append((box, cls, score))

        if not billboard_detections:
            os.remove(book_image_full_path)
            os.remove(billboard_image_full_path)
            return JsonResponse({'error': 'Billboard not detected'}, status=400)

        billboard_box = billboard_detections[0][0]
        (startY, startX, endY, endX) = billboard_box
        (h, w) = billboard_image_np.shape[:2]
        (startX, startY, endX, endY) = (startX * w, startY * h, endX * w, endY * h)

        width_pixels = endX - startX
        height_pixels = endY - startY

        width_real = width_pixels * scale
        height_real = height_pixels * scale

        os.remove(book_image_full_path)
        os.remove(billboard_image_full_path)

        return JsonResponse({'width': width_real, 'height': height_real, 'x': startX, 'y': startY})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@extend_schema(
    description="The endpoint is used to detect and validate reference images (image should contain a book).",
    summary='Validate Reference (Book) endpoint',
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {'type': 'string', 'format': 'binary', 'description': 'Upload book image'},
            },
            'required': ['file']
        }
    },
    responses={
        200: OpenApiResponse(
            description="JSON response containing billboard dimension and position information",
            examples={
                "application/json": {
                    "message": "File uploaded successfully.",
                    "data": {
                        "message": 'string',
                        "is_valid": True
                    }
                }
            },
        )
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser])
def detect_book_in_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        book_image_file = request.FILES['file']

        book_image_path = default_storage.save('book.jpg', ContentFile(book_image_file.read()))
        book_image_full_path = os.path.join(default_storage.location, book_image_path)

        # Process the book image to find the reference object
        book_image_np = load_image_into_numpy_array(book_image_full_path)
        results = book_model(book_image_full_path)

        # Debugging: Print all detection results
        print(f"Results object for book image: {results}")

        # YOLOv8 specific handling
        if isinstance(results, list):
            results = results[0]  # Assume single image

        # Get detection results for the book
        book_detections = []
        for box, cls, score in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy().astype(int), results.boxes.conf.cpu().numpy()):
            if cls == BOOK_CLASS_ID and score > 0.3:  # Adjust the threshold if needed
                book_detections.append((box, cls, score))

        # Print all detected class IDs
        for box, cls, score in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy().astype(int), results.boxes.conf.cpu().numpy()):
            print(f"Detected class ID: {cls}, Score: {score}")

        if not book_detections:
            os.remove(book_image_full_path)
            return JsonResponse({'message': 'Book not detected', "is_valid": False}, status=400)
        else:
            os.remove(book_image_full_path)
            return JsonResponse({'message': 'Book detected', "is_valid": True})
        
    return JsonResponse({'error': 'Invalid request'}, status=400)
        