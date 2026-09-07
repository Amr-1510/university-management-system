# University Management System

A university database project built with MySQL and Python. It provides two ways to manage the same university data:

- A desktop application built with CustomTkinter
- A REST API built with FastAPI

Both interfaces work with the same MySQL database, so any change made through one interface appears in the other.

## Features

- Manage departments, students, instructors, courses, sections, phone numbers, and enrollments
- Add, view, update, and delete records
- Validate foreign keys, unique values, grades, phone numbers, and student levels
- Enforce database rules using MySQL constraints and triggers
- Prevent a student from registering for more than 19 active credit hours
- Limit each section to 5 active students
- Automatically generate API documentation with Swagger UI

## Project Structure

| File | Description |
|---|---|
| `university_db.sql` | Creates the database, tables, constraints, triggers, sample data, and example queries |
| `GUI_DB.py` | Desktop GUI application for managing university records |
| `main.py` | FastAPI application that exposes the database through HTTP endpoints |
| `database.py` | Shared MySQL connection configuration for the API |
| `requirements.txt` | Required Python packages |

## Database Design

```text
Department ──< Course ──< Section ──< Enrollment >── Student
     │                        │                          │
     └──< Instructor ─────────┘                 Student_Phone
```

### Main Tables

| Table | Description |
|---|---|
| `Department` | Academic departments |
| `Student` | Student information and academic level |
| `Student_Phone` | Student phone numbers |
| `Instructor` | Instructor information and salary |
| `Course` | Courses offered by each department |
| `Section` | Course sections, halls, and instructors |
| `Enrollment` | Student registrations and grades |

### Important Database Rules

- Student email addresses are unique.
- Phone numbers are unique and must use a valid Egyptian mobile format.
- A student level must be between 1 and 4.
- Course credits must be between 0 and 3.
- A student cannot register for the same course twice.
- A department cannot be deleted while related records still exist.
- A student cannot register for more than 19 active credit hours.
- A section cannot contain more than 5 active students.

## Desktop GUI

The desktop application is implemented in `GUI_DB.py` using CustomTkinter.

It includes management screens for:

- Students
- Courses
- Instructors
- Departments
- Sections
- Student phones
- Enrollments

The GUI provides dropdown lists for foreign keys such as department, course, instructor, and student. When adding an enrollment, selecting a course filters the available sections to prevent invalid section-course combinations.

Run the desktop application:

```bash
python GUI_DB.py
```

Before running it, make sure the database credentials inside `GUI_DB.py` match your MySQL configuration.

## REST API

The API is implemented in `main.py` using FastAPI.

It gives other applications—such as a website, mobile app, or another desktop program—a way to access the same database through HTTP requests.

### Available Endpoints

| Resource | Base Endpoint |
|---|---|
| Health check | `GET /health` |
| Departments | `/departments` |
| Students | `/students` |
| Instructors | `/instructors` |
| Courses | `/courses` |
| Sections | `/sections` |
| Student phones | `/student-phones` |
| Enrollments | `/enrollments` |

Examples:

```text
GET    /students
POST   /students
PATCH  /students/{student_id}
DELETE /students/{student_id}

GET    /courses
POST   /courses
PUT    /courses/{course_id}
DELETE /courses/{course_id}
```

FastAPI automatically provides an interactive testing interface at:

```text
http://127.0.0.1:8000/docs
```

Run the API:

```bash
uvicorn main:app --reload
```

## Setup

### 1. Create the Database

Open MySQL Workbench or MySQL CLI and run:

```sql
source university_db.sql;
```

This creates the `university_db` database, tables, sample data, constraints, and triggers.

### 2. Configure API Credentials

Create a file named `.env` in the project folder using `.env.example` as a guide:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=university_db
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Project

Desktop GUI:

```bash
python GUI_DB.py
```

REST API:

```bash
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Technologies Used

- Python
- MySQL
- FastAPI
- Pydantic
- CustomTkinter
- MySQL Connector
- Python Dotenv

## Notes

The GUI and API are independent interfaces, but they use the same `university_db` database.

```text
Desktop GUI  ───────┐
                    ├── MySQL Database
FastAPI REST API ───┘
```