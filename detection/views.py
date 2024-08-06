import cv2
import numpy as np
import torch
import base64
import os
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
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


def load_image_into_numpy_array(base64_string):
    # Decode the base64 string
    image_data = base64.b64decode(base64_string)
    # Convert the image data to a numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    # Decode the numpy array into an image
    image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image_np


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
        'application/json': {
            'type': 'object',
            'properties': {
                'book_width': {'type': 'integer', 'description': 'Enter the book width'},
                'book_height': {'type': 'integer', 'description': 'Enter the book height'},
                'book_unit': {'type': 'string', 'description': 'Enter the book unit'},
                'book_image': {'type': 'string', 'format': 'base64', 'description': 'Upload book reference image as base64 string'},
                'billboard_image': {'type': 'string', 'format': 'base64', 'description': 'Upload billboard image as base64 string'},
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
@parser_classes([JSONParser])
def process_images(request):
    if request.method == 'POST':
        book_image_base64 = request.data.get('book_image')
        billboard_image_base64 = request.data.get('billboard_image')
        book_width = float(request.data.get('book_width', ''))
        book_height = float(request.data.get('book_height', ''))
        book_unit = request.data.get('book_unit', 'mm')

        if not book_image_base64 or not billboard_image_base64:
            return JsonResponse({'error': 'Images not provided'}, status=400)

        try:
            book_image_np = load_image_into_numpy_array(book_image_base64)
            billboard_image_np = load_image_into_numpy_array(billboard_image_base64)

            if book_image_np is None:
                return JsonResponse({'error': 'Book image not readable'}, status=500)
            if billboard_image_np is None:
                return JsonResponse({'error': 'Billboard image not readable'}, status=500)

            # Process the book image to find the reference object
            book_results = book_model(book_image_np)
            if isinstance(book_results, list):
                book_results = book_results[0]

            book_detections = []
            for box, cls, score in zip(book_results.boxes.xyxy.cpu().numpy(), book_results.boxes.cls.cpu().numpy().astype(int), book_results.boxes.conf.cpu().numpy()):
                if cls == BOOK_CLASS_ID and score > 0.5:
                    book_detections.append((box, cls, score))

            if not book_detections:
                return JsonResponse({'error': 'Book not detected'}, status=400)

            book_box = book_detections[0][0]
            scale = calculate_scale_factor(book_box, book_width, book_height, book_image_np, book_unit)

            # Process the billboard image
            billboard_results = billboard_model(billboard_image_np)
            if isinstance(billboard_results, torch.Tensor):
                billboard_results = billboard_results.pandas().xyxy[0].to_dict(orient="records")
            else:
                billboard_results = billboard_results.xyxy[0].cpu().numpy()

            billboard_detections = []
            for detection in billboard_results:
                if isinstance(detection, dict):
                    cls = int(detection['class'])
                    score = detection['confidence']
                    if cls == BILLBOARD_CLASS_ID and score > 0.5:
                        box = [detection['xmin'], detection['ymin'], detection['xmax'], detection['ymax']]
                        billboard_detections.append((box, cls, score))
                else:
                    box = detection[:4]
                    cls = int(detection[5])
                    score = detection[4]
                    if cls == BILLBOARD_CLASS_ID and score > 0.5:
                        billboard_detections.append((box, cls, score))

            if not billboard_detections:
                return JsonResponse({'error': 'Billboard not detected'}, status=400)

            billboard_box = billboard_detections[0][0]
            (startX, startY, endX, endY) = billboard_box
            (h, w) = billboard_image_np.shape[:2]
            (startX, startY, endX, endY) = (startX * w, startY * h, endX * w, endY * h)

            billboard_width_pixels = endX - startX
            billboard_height_pixels = endY - startY

            billboard_width_mm = billboard_width_pixels * scale
            billboard_height_mm = billboard_height_pixels * scale

            # Convert dimensions from square millimeters to square meters
            billboard_width_m = billboard_width_mm / 1000
            billboard_height_m = billboard_height_mm / 1000

            result_data = {
                'width': round(billboard_width_m, 2),
                'height': round(billboard_height_m, 2),
                'x': round(startX, 2),
                'y': round(startY, 2)
            }

            return JsonResponse(result_data)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@extend_schema(
    description="The endpoint is used to detect and validate reference images (image should contain a book).",
    summary='Validate Reference (Book) endpoint',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'file': {'type': 'string', 'format': 'base64', 'description': 'Upload book image'},
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
@parser_classes([JSONParser])
def detect_book_in_image(request):
    if request.method == 'POST':
        book_image_base64 = request.data.get('file')
        
        if not book_image_base64:
            return JsonResponse({'error': 'No image provided'}, status=400)

        try:
            book_image_np = load_image_into_numpy_array(book_image_base64)
            
            if book_image_np is None:
                return JsonResponse({'error': 'Image not readable'}, status=500)

            # Process the book image to find the reference object
            book_results = book_model(book_image_np)
            if isinstance(book_results, list):
                book_results = book_results[0]

            book_detections = []
            for box, cls, score in zip(book_results.boxes.xyxy.cpu().numpy(), book_results.boxes.cls.cpu().numpy().astype(int), book_results.boxes.conf.cpu().numpy()):
                if cls == BOOK_CLASS_ID and score > 0.5:
                    book_detections.append((box, cls, score))

            if not book_detections:
                return JsonResponse({'message': 'Book not detected', 'is_valid': False}, status=200)

            return JsonResponse({'message': 'Book detected', 'is_valid': True}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
