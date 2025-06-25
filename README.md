# ANSAA - Anambra State Signage and Advertisement Authority

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [API Documentation](#api-documentation)
7. [Database Models](#database-models)
8. [Authentication](#authentication)
9. [Deployment](#deployment)
10. [Contributing](#contributing)

## Project Overview

ANSAA (Anambra State Signage and Advertisement Authority) is a comprehensive Django-based web application designed to assist the Anambra State government in compiling comprehensive data on all billboards within the state and generating actionable insights for state improvement initiatives.

### Key Objectives
- **Billboard Management**: Comprehensive tracking and management of all billboards in Anambra State
- **Data Collection**: Systematic collection of billboard data including location, dimensions, ownership, and compliance
- **Payment Tracking**: Monitor payment status and compliance for billboard operations
- **Reporting**: Generate detailed reports for government decision-making
- **User Management**: Role-based access control for different stakeholders

## Features

### 🔐 Authentication & User Management
- **Custom User Model**: Extended user model with phone number and profile management
- **JWT Authentication**: Secure token-based authentication
- **Password Reset**: Email-based password reset functionality
- **Profile Management**: User profile updates with picture upload

### 📊 Media Asset Management
- **Billboard Registration**: Complete billboard registration with detailed information
- **QR Code Generation**: Automatic QR code generation for each billboard
- **Image Upload**: Multiple image upload support for billboards
- **Location Tracking**: GPS coordinates and address management
- **Payment Status**: Track payment status and due dates

### 🎯 Target Management
- **Monthly Targets**: Set and track monthly billboard registration targets
- **Progress Monitoring**: Real-time progress tracking against targets
- **Performance Analytics**: User performance metrics and reporting

### 📋 Task Management
- **Default Tasks**: Automatic task assignment for new users
- **Task Completion**: Track user onboarding and compliance tasks
- **Device Management**: Device registration and verification system

### 📈 Reporting System
- **Asset Reports**: Comprehensive billboard inventory reports
- **Count Reports**: Statistical reports on billboard distribution
- **Export Functionality**: Download reports in various formats

### 🔍 Search & Filter
- **Advanced Search**: Filter billboards by type, zone, status, and vacancy
- **Zone Management**: Geographic zone-based organization
- **Status Tracking**: Track billboard status (pending, completed, vacant, occupied)

## Technology Stack

### Backend
- **Django 5.0.4**: Web framework
- **Django REST Framework 3.15.1**: API development
- **PostgreSQL**: Database
- **JWT Authentication**: Token-based security
- **Pillow**: Image processing
- **qrcode**: QR code generation

### Frontend & Documentation
- **DRF Spectacular**: API documentation
- **Swagger UI**: Interactive API documentation

### Deployment & Infrastructure
- **Gunicorn**: WSGI server
- **WhiteNoise**: Static file serving
- **Supabase**: Database hosting
- **Nginx**: Web server (production)

### Development Tools
- **django-crontab**: Scheduled tasks
- **python-dotenv**: Environment management
- **django-phonenumber-field**: Phone number validation

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip
- virtualenv (recommended)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd test-ansa
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=your-database-url
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
API_KEY=your-api-key
```

### Step 5: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

## Configuration

### Database Configuration
The project uses PostgreSQL with Supabase hosting:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.fpojttjeesqxlygboell',
        'PASSWORD': 'your-password',
        'HOST': 'aws-0-eu-central-1.pooler.supabase.com',
        'PORT': '5432',
    }
}
```

### Email Configuration
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "support@cedarsprohub.com"
EMAIL_HOST_PASSWORD = "your-app-password"
EMAIL_USE_TLS = True
```

### JWT Configuration
```python
SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

## API Documentation

### Base URL
```
https://your-domain.com/api/
```

### Authentication Endpoints

#### 1. User Login
- **URL**: `/auth/login/`
- **Method**: `POST`
- **Description**: Authenticate user with email and password
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "refresh": "refresh-token",
    "access": "access-token"
  }
  ```

#### 2. User Logout
- **URL**: `/auth/logout/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access-token>`
- **Request Body**:
  ```json
  {
    "refresh_token": "refresh-token"
  }
  ```

#### 3. User Profile
- **URL**: `/auth/profile/`
- **Method**: `GET/PUT`
- **Headers**: `Authorization: Bearer <access-token>`
- **GET Response**:
  ```json
  {
    "user_id": "ansa123456",
    "email": "user@example.com",
    "phone_number": "+2341234567890",
    "fullname": "John Doe",
    "gender": "male",
    "picture": "profile-picture-url"
  }
  ```

#### 4. Password Reset Request
- **URL**: `/auth/request-password-reset/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```

### Media Asset Endpoints

#### 1. Create Billboard
- **URL**: `/asset/post-assets/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access-token>`
- **Request Body**:
  ```json
  {
    "signage_type": "First Party",
    "sign_type": "Unipoles",
    "sign_format": "Portrait",
    "no_of_faces": "Single",
    "illumination_type": "External",
    "length": 10.5,
    "breadth": 5.2,
    "zone": "normal_zone",
    "asset_street_address": "123 Main Street",
    "asset_lga": "Awka South",
    "company_name": "ABC Company",
    "company_phone": "+2341234567890",
    "asin": "ASIN123456",
    "business_type": "Commercial Business",
    "business_category": "Office or Shops",
    "longitude": 7.123456,
    "latitude": 5.123456,
    "image1": "image-url-1",
    "image2": "image-url-2",
    "image3": "image-url-3"
  }
  ```

#### 2. List User's Billboards
- **URL**: `/asset/list-assets/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

#### 3. Update Billboard
- **URL**: `/asset/<id>/`
- **Method**: `PUT`
- **Headers**: `Authorization: Bearer <access-token>`

#### 4. Delete Billboard
- **URL**: `/asset/<id>/delete/`
- **Method**: `DELETE`
- **Headers**: `Authorization: Bearer <access-token>`

#### 5. Search Billboards
- **URL**: `/asset/search/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`
- **Query Parameters**:
  - `sign_type`: Filter by sign type
  - `zone`: Filter by zone
  - `vacancy`: Filter by vacancy status
  - `status`: Filter by completion status

#### 6. Get Zones
- **URL**: `/asset/zones/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

#### 7. Get Dimensions
- **URL**: `/asset/dimensions/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

#### 8. Get Amount Per Square Foot
- **URL**: `/asset/amount-per-sq-ft/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

### Target Management Endpoints

#### 1. Monthly Statistics
- **URL**: `/monthly-stats`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`
- **Response**:
  ```json
  {
    "month": 12,
    "year": 2024,
    "target": 50,
    "target_count": 25,
    "progress_percentage": 50.0
  }
  ```

### Task Management Endpoints

#### 1. List User Tasks
- **URL**: `/task/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

#### 2. Device Management
- **URL**: `/task/devices/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

#### 3. Register Device
- **URL**: `/devices/verify/`
- **Method**: `POST`
- **Headers**: `Authorization: Bearer <access-token>`
- **Request Body**:
  ```json
  {
    "device_name": "iPhone 12",
    "device_id": "unique-device-id",
    "os": "iOS 15.0"
  }
  ```

### Reporting Endpoints

#### 1. Download Report
- **URL**: `/download-report/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

#### 2. Count Assets Report
- **URL**: `/count-assets/`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <access-token>`

### Oasis Integration Endpoints

#### 1. Update Payment Status
- **URL**: `/billboards/<unique_id>/update-payment/`
- **Method**: `POST`
- **Headers**: `X-API-Key: your-api-key`
- **Request Body**:
  ```json
  {
    "payment_status": "paid",
    "payment_date": "2024-12-01T10:00:00Z"
  }
  ```

#### 2. Assets List (Oasis)
- **URL**: `/asset/assets-list/`
- **Method**: `GET`
- **Headers**: `X-API-Key: your-api-key`

## Database Models

### Authentication Models

#### AnsaaUser
- Custom user model extending Django's AbstractBaseUser
- Fields: user_id, email, phone_number, fullname, gender, picture, etc.
- Automatic user_id generation with 'ansa' prefix

#### OTP
- One-time password for verification
- Fields: email, phone_number, otp, expiration_time, verified

### Media Asset Models

#### Billboards
- Core billboard information
- Fields: unique_id, signage_type, sign_type, dimensions, location, payment_status, etc.
- Automatic QR code generation
- Integration with Oasis system

#### Zones
- Geographic zones in Anambra State
- Fields: name

#### Dimensions
- Standard billboard dimensions and pricing
- Fields: name, min_width, max_width, unit, category, zone, price

#### AmountPerSqFt
- Pricing configuration per square foot
- Fields: amount_per_sq_ft

### Target Management Models

#### Target
- Monthly targets for users
- Fields: user, month, year, target, target_count, date
- Automatic target creation and counting

### Task Management Models

#### Task
- User tasks and onboarding
- Fields: title, description, is_completed, user
- Automatic default task creation

#### DeviceDetail
- User device registration
- Fields: user, device_name, device_id, os, created_at

## Authentication

### JWT Token Authentication
- Access tokens valid for 5 days
- Refresh tokens valid for 7 days
- Token blacklisting on logout

### Custom User Backend
- Email-based authentication
- Phone number validation
- Custom user manager with automatic password generation

### API Key Authentication
- Required for Oasis integration endpoints
- Header: `X-API-Key: your-api-key`

## Deployment

### Production Setup

#### 1. Environment Variables
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-production-database-url
```

#### 2. Static Files
```bash
python manage.py collectstatic
```

#### 3. Database Migration
```bash
python manage.py migrate
```

#### 4. Gunicorn Configuration
```bash
gunicorn ansaa_server.wsgi:application --bind 0.0.0.0:8000
```

#### 5. Nginx Configuration
```nginx
server {
    server_name your-domain.com;
    
    location /static/ {
        root /path/to/your/project;
    }
    
    location /media/ {
        root /path/to/your/project;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/gunicorn.sock;
    }
}
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "ansaa_server.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## API Documentation Access

### Swagger UI
- **URL**: `/api/schema/docs/`
- **Description**: Interactive API documentation

### OpenAPI Schema
- **URL**: `/api/schema/`
- **Description**: Raw OpenAPI schema in JSON format

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions and classes
- Include type hints where appropriate

### Testing
```bash
python manage.py test
```

## Support

For support and questions:
- Email: support@cedarsprohub.com (to be updated)
- Documentation: `/api/schema/docs/`

## License

This project is proprietary software developed for the Anambra State government.


