# MessOn Backend

**MessOn Backend** is the centralized backend infrastructure powering the MessOn ecosystem. Built with **FastAPI, PostgreSQL, and Alembic**, it provides RESTful APIs and database services for MessOn Student, MessOn Admin, and MessOn Faculty.

The backend handles core mess operations, including student management, meal preferences, QR-based coupon generation and validation, menu management, ratings, complaints, notifications, and administrative operations across multiple mess establishments.

It acts as the central source of truth, ensuring consistent data and communication between all three applications.

---

## MessOn Ecosystem

MessOn consists of three interconnected applications powered by a shared backend.

| Application | Responsibilities |
|---|---|
| **MessOn Student** | Meal coupons, menu, meal preferences, ratings, complaints, billing, and notifications |
| **MessOn Admin** | Coupon scanning, menu management, preference analytics, meal ratings, complaints, mess timings, and meal compulsion settings |
| **MessOn Faculty** | Student and mess manager management, multi-mess administration, billing, holidays, complaints, and notifications |

### System Architecture

```mermaid
flowchart TD
    S["MessOn Student<br/>Compose Multiplatform"]
    A["MessOn Admin<br/>Compose Multiplatform"]
    F["MessOn Faculty<br/>Compose Multiplatform"]

    API["MessOn Backend<br/>FastAPI REST APIs"]

    AUTH["Authentication & Authorization"]
    SERVICES["Business Logic & Services"]
    DB[("PostgreSQL Database")]
    ALEMBIC["Alembic<br/>Database Migrations"]
    FCM["Firebase Cloud Messaging"]

    S <--> API
    A <--> API
    F <--> API

    API --> AUTH
    API --> SERVICES
    SERVICES <--> DB
    ALEMBIC --> DB
    SERVICES --> FCM
    FCM --> S
```

---

## Key Features

### 1. Student Management
- Manage student records and profiles.
- Maintain student identifiers and associated mess information.
- Support administrative student operations.
- Provide student data to authorized applications.

### 2. Meal Preference Management
- Store student meal preferences.
- Maintain preferences for different days and meal slots.
- Retrieve preference data for mess-side analytics.
- Help mess administrators understand student meal demand.

### 3. QR-Based Meal Coupon System
- Generate meal coupons for students.
- Support breakfast, lunch, and dinner.
- Manage coupon validity and expiry.
- Validate coupons during QR scanning.
- Prevent duplicate coupon redemption.
- Maintain coupon redemption records.

### 4. Automated Coupon Scheduling
- Generate upcoming meal coupons through scheduled background tasks.
- Support next-day coupon generation.
- Apply meal-specific expiry rules.
- Maintain automated coupon lifecycle management.

### 5. Mess Menu Management
- Store and manage daily mess menus.
- Support different meal slots.
- Provide menu data to student and mess-side applications.
- Support menu updates and notification workflows.

### 6. Meal Ratings & Analytics
- Store student ratings for individual meals.
- Retrieve meal-wise ratings.
- Provide rating information to mess administrators.
- Support meal quality monitoring and analysis.

### 7. Complaint Management
- Store complaints submitted by students.
- Support complaint status tracking.
- Allow authorized administrators to view and manage complaints.
- Support complaint reactions such as likes and dislikes.

### 8. Mess Administration
- Support multiple mess establishments.
- Associate students and mess managers with relevant mess establishments.
- Manage mess-related operational information.
- Support mess holidays and closing-time configurations.
- Manage compulsory and optional meal settings for different days.

### 9. Billing Management
- Support billing-related operations.
- Provide billing data to the relevant applications.
- Maintain centralized billing information.

### 10. Push Notifications
- Integrate Firebase Cloud Messaging (FCM).
- Register and manage device tokens.
- Support topic-based notifications.
- Send menu updates and administrative announcements.
- Support notifications to registered devices.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Primary programming language |
| FastAPI | Backend framework and REST API development |
| PostgreSQL | Relational database |
| SQLAlchemy | Database ORM |
| Alembic | Database schema migrations |
| Pydantic | Request validation and data serialization |
| Firebase Admin SDK | Firebase Cloud Messaging |
| Uvicorn | ASGI application server |
| APScheduler / Scheduler | Automated scheduled tasks, where configured |
| Git | Version control |

---

## Architecture

The backend follows a modular structure that separates API routes, business logic, database operations, and data models.

```mermaid
flowchart TD
    CLIENT["Mobile Applications"]
    ROUTER["API Routes"]
    SCHEMA["Pydantic Schemas"]
    SERVICE["Service Layer"]
    MODEL["SQLAlchemy Models"]
    REPO["Database Operations"]
    DB[("PostgreSQL")]

    CLIENT --> ROUTER
    ROUTER --> SCHEMA
    SCHEMA --> SERVICE
    SERVICE --> MODEL
    SERVICE --> REPO
    REPO <--> DB
```

### Architectural Principles

- **Modular Design:** Organizes functionality into independent business modules.
- **RESTful APIs:** Provides structured HTTP endpoints for mobile applications.
- **ORM-Based Database Access:** Uses SQLAlchemy for database interaction.
- **Schema Validation:** Uses Pydantic for request and response validation.
- **Database Versioning:** Uses Alembic to manage schema changes.
- **Separation of Concerns:** Separates routing, business logic, schemas, and database operations.
- **Centralized Data Management:** Maintains a shared backend for all MessOn applications.

---

## Database Management

MessOn uses PostgreSQL as its primary relational database.

The database stores information related to:

- Students
- Mess establishments
- Mess managers
- Meal preferences
- Meal coupons
- Coupon redemption records
- Daily menus
- Meal ratings
- Complaints
- Device registrations
- Notifications
- Billing and operational configurations

### Database Migrations with Alembic

Alembic is used to manage database schema changes and maintain migration history.

**Create a migration:**

```bash
alembic revision --autogenerate -m "describe your changes"
```

**Apply migrations:**

```bash
alembic upgrade head
```

**Rollback the latest migration:**

```bash
alembic downgrade -1
```

**Check current migration:**

```bash
alembic current
```

**View migration history:**

```bash
alembic history
```

Alembic helps keep database schema changes organized across development and deployment environments.

---

## Multi-Tenant Architecture

MessOn supports multiple mess establishments through a centralized backend.

Each mess establishment can have its own operational data, including:

- Students associated with the establishment.
- Mess managers and their permissions.
- Menus and meal configurations.
- Meal preferences and ratings.
- Complaints and operational settings.

The backend should enforce tenant-level authorization and data isolation so that users can access only the mess data they are authorized to manage.

---

## Automated Coupon Lifecycle

The coupon system supports scheduled generation and backend-controlled validation.

```mermaid
flowchart TD
    A["Scheduled Coupon Generation"]
    B["Generate Next-Day Meal Coupons"]
    C["Store Coupons in PostgreSQL"]
    D["Student Views QR Coupon"]
    E["Mess Admin Scans QR"]
    F["Backend Validates Coupon"]
    G{"Valid and Unredeemed?"}
    H["Mark Coupon as Redeemed"]
    I["Reject Redemption"]

    A --> B --> C --> D --> E --> F --> G
    G -->|Yes| H
    G -->|No| I
```

The backend is responsible for validating coupon status, expiry, and redemption state.

Coupon redemption should be handled atomically to prevent duplicate scans, including simultaneous redemption attempts from multiple devices.

---

## Project Structure

The following is a representative modular structure. Adjust it to match the actual repository.

```text
MessOn2.0-Backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   └── base.py
│   │
│   ├── students/
│   ├── meal_preferences/
│   ├── coupons/
│   ├── mess_admin/
│   ├── menu/
│   ├── complaint/
│   ├── notifications/
│   ├── coupon_analytics/
│   │
│   └── services/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10+
- PostgreSQL
- pip
- Git

### 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd MessOn2.0-Backend
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Example configuration:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/messon

SECRET_KEY=your_secret_key

FIREBASE_CREDENTIALS_PATH=path/to/firebase-service-account.json
```

Use the actual environment variable names expected by your application. Keep secrets and Firebase service account credentials out of version control.

### 5. Apply Database Migrations

```bash
alembic upgrade head
```

### 6. Start the Development Server

```bash
uvicorn app.main:app --reload
```

The API should now be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL |
|---|---|
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |
| OpenAPI Schema | `/openapi.json` |

You can use Swagger UI to explore endpoints, inspect request and response schemas, and test API operations.

---

## Environment & Deployment

The backend can be deployed to a cloud hosting platform with:

- A Python-compatible runtime.
- A PostgreSQL database.
- Environment-based configuration.
- Firebase service account credentials.
- Database migrations executed during deployment.

For production deployments:

- Keep secrets in environment variables or a secure secrets manager.
- Use HTTPS.
- Configure CORS for trusted clients.
- Enforce authentication and role-based authorization.
- Validate tenant access on every relevant operation.
- Run Alembic migrations as part of a controlled deployment process.
- Configure database backups and monitoring.

---

## Future Scope

Potential improvements to the MessOn ecosystem include:

- Advanced meal demand forecasting.
- Detailed mess performance analytics.
- Improved billing and financial reports.
- Automated operational insights.
- More granular administrative permissions.
- Enhanced monitoring and audit logs.

---

## Part of the MessOn Project

| Component | Technology |
|---|---|
| MessOn Student | Kotlin + Compose Multiplatform |
| MessOn Admin | Kotlin + Compose Multiplatform |
| MessOn Faculty | Kotlin + Compose Multiplatform |
| MessOn Backend | FastAPI + PostgreSQL + Alembic |

**MessOn aims to build a connected, transparent, and efficient digital ecosystem for campus mess management.**

---

**Built with Python, FastAPI, PostgreSQL, and Alembic.**
