import cv2
import numpy as np
import torch
import base64
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
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

def save_base64_image(base64_string, filename):
    try:
        # Split the base64 string to remove metadata
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        # Decode the base64 string
        image_data = base64.b64decode(base64_string)
        
        # Create a ContentFile from the decoded data
        image_file = ContentFile(image_data, name=filename)
        
        # Save the file to default storage
        saved_path = default_storage.save(filename, image_file)
        
        return saved_path
    except Exception as e:
        print(f"Error saving base64 image: {e}")
        return None

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

        book_image_path = save_base64_image(book_image_base64, 'book.jpg')
        billboard_image_path = save_base64_image(billboard_image_base64, 'billboard.jpg')

        if not book_image_path or not billboard_image_path:
            return JsonResponse({'error': 'Failed to save images'}, status=500)

        book_image_full_path = os.path.join(default_storage.location, book_image_path)
        billboard_image_full_path = os.path.join(default_storage.location, billboard_image_path)

        # Check if the images are readable by OpenCV
        book_image_np = cv2.imread(book_image_full_path)
        billboard_image_np = cv2.imread(billboard_image_full_path)

        if book_image_np is None:
            return JsonResponse({'error': 'Book image not readable'}, status=500)
        if billboard_image_np is None:
            return JsonResponse({'error': 'Billboard image not readable'}, status=500)

        try:
            # Process the book image to find the reference object
            results = book_model(book_image_full_path)

            # Debugging: Print all detection results
            print(f"Results object for book image: {results}")

            # YOLOv8 specific handling
            if isinstance(results, list):
                results = results[0]  # Assume single image

            # Get detection results for the book
            book_detections = []
            for box, cls, score in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy().astype(int), results.boxes.conf.cpu().numpy()):
                if cls == BOOK_CLASS_ID and score > 0.5:  # Increased threshold for better accuracy
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
                    if cls == BILLBOARD_CLASS_ID and score > 0.5:  # Increased threshold for better accuracy
                        box = [detection['xmin'], detection['ymin'], detection['xmax'], detection['ymax']]
                        billboard_detections.append((box, cls, score))
                else:  # YOLOv8 handling
                    box = detection[:4]
                    cls = int(detection[5])
                    score = detection[4]
                    if cls == BILLBOARD_CLASS_ID and score > 0.5:
                        billboard_detections.append((box, cls, score))

            if not billboard_detections:
                os.remove(book_image_full_path)
                os.remove(billboard_image_full_path)
                return JsonResponse({'error': 'Billboard not detected'}, status=400)

            billboard_box = billboard_detections[0][0]
            (startX, startY, endX, endY) = billboard_box
            (h, w) = billboard_image_np.shape[:2]
            (startX, startY, endX, endY) = (startX * w, startY * h, endX * w, endY * h)

            billboard_width_pixels = endX - startX
            billboard_height_pixels = endY - startY

            billboard_width_mm = billboard_width_pixels * scale
            billboard_height_mm = billboard_height_pixels * scale

            result_data = {
                'width': round(billboard_width_mm, 2),
                'height': round(billboard_height_mm, 2),
                'x': round(startX, 2),
                'y': round(startY, 2)
            }

            os.remove(book_image_full_path)
            os.remove(billboard_image_full_path)

            return JsonResponse({'width': round(billboard_width_mm, 2),
                'height': round(billboard_height_mm, 2),
                'x': round(startX, 2),
                'y': round(startY, 2)})

        except Exception as e:
            os.remove(book_image_full_path)
            os.remove(billboard_image_full_path)
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            if os.path.exists(book_image_full_path):
                os.remove(book_image_full_path)
            if os.path.exists(billboard_image_full_path):
                os.remove(billboard_image_full_path)

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

        book_image_path = save_base64_image(book_image_base64, 'book.jpg')
        
        if not book_image_path:
            return JsonResponse({'error': 'Failed to save image'}, status=500)
        
        book_image_full_path = os.path.join(default_storage.location, book_image_path)

        # Check if the image is saved correctly
        if not os.path.exists(book_image_full_path):
            return JsonResponse({'error': 'Image not saved correctly'}, status=500)

        # Check if the image is readable by OpenCV
        image = cv2.imread(book_image_full_path)
        if image is None:
            return JsonResponse({'error': 'Image not readable'}, status=500)

        try:
            # Process the book image to find the reference object
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

            os.remove(book_image_full_path)

            if not book_detections:
                return JsonResponse({'message': 'Book not detected', 'is_valid': False}, status=200)

            return JsonResponse({'message': 'Book detected', 'is_valid': True}, status=200)

        except Exception as e:
            os.remove(book_image_full_path)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)