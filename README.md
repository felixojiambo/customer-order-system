# Customer Order Management System API

This is a Django-based REST API for managing customer orders, including Firebase Authentication for secure access and Africa's Talking integration for sending SMS notifications. It provides CRUD operations on orders, user authentication via Firebase tokens, and automatic SMS alerts for order placements.

---

## **Overview**

The **Customer Order Management System** allows users to:
- Register and log in via Firebase Authentication.
- Create, view, update, and delete their orders.
- Receive SMS alerts via Africa's Talking API when new orders are placed.
- View API documentation via Swagger and ReDoc.
- Use JWT tokens for securing endpoints.

This API is designed for multi-user environments where authenticated users can manage their own orders while ensuring secure access and notifications.

---

## **Features**

- **Firebase Authentication**: Secures user registration and login using OpenID Connect (OIDC) and Firebase tokens.
- **Order Management**: Full CRUD support for managing customer orders.
- **SMS Alerts**: Sends order confirmation SMS to customers using Africa's Talking API.
- **Swagger API Documentation**: Interactive documentation and testing using Swagger UI and ReDoc.
- **OAuth2 Support**: For OpenID Connect (OIDC) authentication.
- **JWT Token Authentication**: For securing endpoints after login.

---

## **Setup and Installation**

### **Prerequisites**

To run this project, you will need the following:

- **Docker** & **Docker Compose** (For containerized setup)
- **Python 3.12**
- **Django 5.x**
- **PostgreSQL** (If not using Docker)
- **Africa's Talking API Credentials** (For sending SMS)
- **Firebase Project** (For Authentication)

---

## **Clone the Repository**

```bash
git clone https://github.com/felixojiambo/customer-order-system.git
cd customer-order-system
```

---

## **Environment Variables**

Create a `.env` file in the root of your project and populate it with the following environment variables:

```bash
# Django settings
SECRET_KEY=your-django-secret-key
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# Firebase configuration
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_AUTH_DOMAIN=your-firebase-auth-domain
FIREBASE_DATABASE_URL=your-firebase-database-url
FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket
FIREBASE_MESSAGING_SENDER_ID=your-firebase-messaging-sender-id
FIREBASE_APP_ID=your-firebase-app-id
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-client-email

# Africa's Talking API credentials
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-africastalking-api-key
```

---

## **Docker Setup**

The easiest way to get the application up and running is via Docker.

### **Build and Start the Application**

```bash
docker-compose up --build
```

This command will:
- Build and start the Django app on `http://localhost:8000`.
- Set up a PostgreSQL database in a Docker container.

### **Stopping the Application**

```bash
docker-compose down
```

### **Optional Local Setup (Without Docker)**

If you prefer to run the application locally without Docker:

1. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

4. **Start the development server**:
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://localhost:8000`.

---

## **API Endpoints Documentation**

### **1. User Registration**
Permissions: Open to all users. No authentication required.

#### **Request**:
- **POST** `/api/register/`
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "strongpassword123",
  "phone_number": "+254700000000"
}
```

#### **Response**:
- **201 Created**
```json
{
  "uid": "firebase_uid",
  "email": "user@example.com"
}
```
- **400 Bad Request**: If the user already exists or if input validation fails.

---

### **2. User Login**
Permissions: Open to all users. No authentication required.

#### **Request**:
- **POST** `/api/login/`
```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

#### **Response**:
- **200 OK**
```json
{
  "token": "firebase_id_token"
}
```
- **401 Unauthorized**: If the email/password is incorrect.

---

### **3. Create an Order**
Permissions: Requires JWT authentication.

#### **Request**:
- **POST** `/api/orders/create/`
```json
{
  "item": "Laptop",
  "amount": 1200.00
}
```

#### **Response**:
- **201 Created**
```json
{
  "id": 1,
  "item": "Laptop",
  "amount": "1200.00",
  "order_number": "LA20240921123000"
}
```
- **400 Bad Request**: If the input data is invalid.
- **401 Unauthorized**: If the user is not authenticated.

---

### **4. List Orders**
Permissions: Requires JWT authentication.

#### **Request**:
- **GET** `/api/orders/`
#### **Response**:
- **200 OK**
```json
[
  {
    "id": 1,
    "item": "Laptop",
    "amount": "1200.00",
    "order_number": "LA20240921123000",
    "status": "Pending"
  }
]
```
- **401 Unauthorized**: If the user is not authenticated.

---

### **5. Retrieve Order Details**
Permissions: Requires JWT authentication.

#### **Request**:
- **GET** `/api/orders/{id}/`

#### **Response**:
- **200 OK**
```json
{
  "id": 1,
  "item": "Laptop",
  "amount": "1200.00",
  "order_number": "LA20240921123000",
  "status": "Pending"
}
```
- **404 Not Found**: If the order is not found or does not belong to the authenticated user.
- **401 Unauthorized**: If the user is not authenticated.

---

### **6. Update Order**
Permissions: Requires JWT authentication.

#### **Request**:
- **PUT** `/api/orders/{id}/`
```json
{
  "item": "Gaming Laptop",
  "amount": 1500.00
}
```

#### **Response**:
- **200 OK**
```json
{
  "id": 1,
  "item": "Gaming Laptop",
  "amount": "1500.00",
  "order_number": "LA20240921123000",
  "status": "Pending"
}
```
- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If the order does not exist or does not belong to the authenticated user.

---

### **7. Delete Order**
Permissions: Requires JWT authentication.

#### **Request**:
- **DELETE** `/api/orders/{id}/`

#### **Response**:
- **204 No Content**

- **401 Unauthorized**: If the user is not authenticated.
- **404 Not Found**: If the order does not exist or does not belong to the authenticated user.

---

## **Testing**

This project uses **Pytest** for unit and integration testing. Firebase authentication and Africa's Talking API calls are mocked for testing purposes.

### **Running Tests**

```bash
pytest
```

### **Mocked Test Scenarios**:
- **User Registration**: Simulates Firebase user creation.
- **Order Creation**: Tests if authenticated users can create orders and send SMS alerts.
- **User Login**: Simulates Firebase login and JWT generation.

---

## **Folder Structure**

```
customer_order_service/
│
├── customerorder/                # Main application
│   ├── migrations/               # Django migrations
│   ├── models.py                 # Data models (User, Order)
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API views (Register, Login, Order CRUD)
│   ├── africastalking_utils.py   # Africa's Talking SMS integration
│   └── authentication.py         # Firebase authentication
│
├── customer_order_service/
│   ├── settings.py               # Project settings
│   └── urls.py                   # URL routing
│
├── templates/                    # Django templates (optional)
├── .env                          # Environment variables
├── docker-compose.yml            # Docker setup
├── Dockerfile                    # Docker image configuration
├── requirements.txt              # Python dependencies
└── manage.py                     # Django management commands
```

---

## **License**

This project is licensed under the MIT License.

