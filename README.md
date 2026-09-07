```markdown
# University Management System

A full-stack university database project combining a relational MySQL database with **two interfaces on top of it**: a desktop GUI application and a REST API. The SQL schema defines and populates the entire university data model; the GUI and the API both provide full CRUD access to it independently.

---

## Project Files

| File | Role |
|---|---|
| `university_db.sql` | Creates the database, all tables, constraints, triggers, and inserts sample data |
| `GUI_DB.py` | Desktop GUI app that connects to the database and provides full CRUD management |
| `main.py` | FastAPI REST API exposing the same database operations over HTTP |
| `database.py` | Shared DB connection helper used by the API (reads credentials from `.env`) |
| `requirements.txt` | Python dependencies for the API |

---

## Database Design (`university_db.sql`)

### Schema Overview

```
Department ──< Course ──< Section ──< Enrollment >── Student
     │                        │                          │
     └──< Instructor ─────────┘                 Student_Phone
```

### Tables

#### `Department`
| Column | Type | Constraints |
|---|---|---|
| `Dep_ID` | VARCHAR(30) | PRIMARY KEY |
| `Dname` | VARCHAR(30) | NOT NULL |
| `Room` | VARCHAR(20) | — |
| `Floor` | INT | CHECK >= 0 |

#### `Student`
| Column | Type | Constraints |
|---|---|---|
| `S_ID` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `Dep_ID` | VARCHAR(30) | FK → Department (RESTRICT delete, CASCADE update) |
| `Fname` | VARCHAR(30) | NOT NULL |
| `Lname` | VARCHAR(30) | NOT NULL |
| `Email` | VARCHAR(100) | UNIQUE |
| `std_level` | INT | DEFAULT 1, CHECK 1–4 |

#### `Student_Phone`
| Column | Type | Constraints |
|---|---|---|
| `Phone_number` | VARCHAR(20) | Part of PK, UNIQUE, REGEX: `^(010\|011\|012\|015)[0-9]{8}$` |
| `S_ID` | INT | Part of PK, FK → Student (CASCADE delete & update) |

#### `Instructor`
| Column | Type | Constraints |
|---|---|---|
| `I_ID` | INT | PRIMARY KEY, AUTO_INCREMENT |
| `Dep_ID` | VARCHAR(30) | FK → Department (RESTRICT delete, CASCADE update) |
| `Iname` | VARCHAR(30) | NOT NULL |
| `Email` | VARCHAR(100) | UNIQUE |
| `Salary` | DECIMAL(10,2) | CHECK > 0 |

#### `Course`
| Column | Type | Constraints |
|---|---|---|
| `C_ID` | VARCHAR(30) | PRIMARY KEY |
| `Cname` | VARCHAR(30) | NOT NULL |
| `Credits` | INT | CHECK 0–3 |
| `Dep_ID` | VARCHAR(30) | FK → Department (RESTRICT delete, CASCADE update) |

#### `Section`
| Column | Type | Constraints |
|---|---|---|
| `Sec_ID` | INT | Part of PK, CHECK > 0 |
| `C_ID` | VARCHAR(30) | Part of PK, FK → Course (CASCADE delete & update) |
| `Sec_name` | VARCHAR(30) | — |
| `Hall` | VARCHAR(30) | — |
| `I_ID` | INT | FK → Instructor (SET NULL on delete, CASCADE update) |

#### `Enrollment`
| Column | Type | Constraints |
|---|---|---|
| `S_ID` | INT | Part of PK, FK → Student (CASCADE) |
| `Sec_ID` | INT | Part of PK, FK → Section (CASCADE) |
| `C_ID` | VARCHAR(30) | Part of PK, FK → Section (CASCADE) |
| `grade` | VARCHAR(20) | CHECK: A+/A/A−/B+/B/B−/C+/C/C−/D+/D/D−/F |

UNIQUE constraint on `(S_ID, C_ID)` — a student can only enroll in a course once.

---

### Sample Data Inserted

| Table | Records |
|---|---|
| Department | 4 (CS, DS, CY, AI) |
| Student | 10 students across all departments |
| Student_Phone | 14 phone numbers (some students have 2) |
| Instructor | 8 instructors (2 per department) |
| Course | 12 courses (3 per department) |
| Section | 14 sections across all courses |
| Enrollment | 21 enrollment records |

---

### Triggers

#### `check_credit_limit`
Fires **BEFORE INSERT** on `Enrollment`. Calculates the student's current registered credit hours (where grade IS NULL = active enrollment). If adding the new course would exceed **19 credit hours**, the insert is blocked with:
> `Error: Student cannot register more than 19 credit hours.`

#### `section_capacity`
Fires **BEFORE INSERT** on `Enrollment`. Counts active enrollments in the target section. If the section already has **5 students**, the insert is blocked with:
> `Section is full. Maximum 5 students allowed.`

Both triggers fire regardless of which interface (GUI or API) performs the insert, since they live at the database layer.

---

### Key Queries Included

- Students with their enrolled courses and grades
- Sections with instructor names
- Students at a specific level with their department
- Average instructor salary per department
- Students with grade 'A'
- Highest and lowest instructor salary
- Enrollment count per section
- Students with more than one phone number
- Course count per department
- Instructors ordered by salary

---

### Constraint Violation Tests (included in SQL file)

The file includes intentional bad inserts to verify all constraints work correctly:

| Test | Expected Result |
|---|---|
| `std_level = 10` | Fails CHECK constraint |
| Duplicate email | Fails UNIQUE constraint |
| Non-existent `Dep_ID` | Fails FOREIGN KEY |
| DELETE a department with students | Fails RESTRICT |
| Invalid phone format `010ABC123` | Fails REGEX CHECK |
| Duplicate `(Sec_ID, C_ID)` | Fails PRIMARY KEY |
| Enroll same student in same course twice | Fails UNIQUE `(S_ID, C_ID)` |
| Wrong `S_ID` in enrollment | Fails FOREIGN KEY |

---

## GUI Application (`GUI_DB.py`)

### Overview

A 1000×750 desktop window built with **CustomTkinter**. Connects directly to `university_db` (credentials loaded from `.env`) and provides a point-and-click interface for all 7 tables — no SQL needed.

### Application Structure

```
GUI_DB.py
│
├── DB Config & connect_db()            # MySQL connection handler (reads .env)
│
├── CRUD Helpers
│   ├── sql_fetch_list()                # Generic SELECT
│   ├── insert_dynamic()                # Dynamic INSERT (builds SQL from field config)
│   ├── update_record()                 # Dynamic UPDATE, supports composite primary keys
│   └── delete_by_pk()                  # DELETE, supports composite primary keys
│
├── show_main_menu()                    # 7-button main navigation screen
├── open_manage_screen()                # Splits view: left panel + right data table
├── refresh_table()                     # Reloads Treeview from DB after every operation
│
├── Form Builders
│   ├── build_widget_for_field()        # Renders Entry or ComboBox per field type
│   └── update_composite_fk_options()   # Filters Sec_ID dropdown based on selected C_ID
│
├── show_add_panel()                    # Add form with mandatory field validation
├── show_update_panel()                 # Update form (auto-fills from selected row)
└── delete_selected_row()               # Delete with confirmation dialog
```

### Screens

| Screen | Table | Primary Key | Special Behavior |
|---|---|---|---|
| Manage Students | `Student` | `S_ID` (auto) | Department & level dropdowns |
| Manage Courses | `Course` | `C_ID` | Credits dropdown (0–3) |
| Manage Instructors | `Instructor` | `I_ID` (auto) | Department dropdown |
| Manage Departments | `Department` | `Dep_ID` | — |
| Manage Sections | `Section` | `Sec_ID, C_ID` (composite) | Course dropdown; Sec_ID auto-filtered by selected Course |
| Manage Student Phones | `Student_Phone` | `S_ID, Phone_number` (composite) | Student dropdown |
| Manage Enrollments | `Enrollment` | `S_ID, Sec_ID, C_ID` (composite) | Student/Course/Grade dropdowns; composite FK validation |

### Composite FK Logic
When managing **Enrollments** or **Sections**, selecting a `C_ID` (Course) dynamically updates the `Sec_ID` dropdown to show only sections that belong to that course — prevents invalid FK combinations before they hit the database.

### Composite Primary Key Handling
`update_record()` and `delete_by_pk()` operate on the full set of primary-key columns for each table (declared per-table in the `pk` config), rather than assuming a single leading column. This matters for tables like `Enrollment`, whose primary key spans three columns (`S_ID, Sec_ID, C_ID`) — updating or deleting one enrollment row correctly leaves a student's other enrollments untouched.

---

## REST API (`main.py`)

A FastAPI service exposing the same database as a set of HTTP endpoints, independent of the GUI. Both interfaces share the same underlying tables, constraints, and triggers.

### Endpoints

Full CRUD (`GET` / `POST` / `PUT` or `PATCH` / `DELETE`) for:
- `/departments`
- `/students`
- `/instructors`
- `/courses`
- `/sections`
- `/student-phones`
- `/enrollments`

Plus `GET /health` for a basic connectivity check.

Interactive documentation (Swagger UI) is auto-generated by FastAPI at `/docs`, where every endpoint can be tried directly from the browser.

### Design Notes

- **Validation at the request boundary** — Pydantic models mirror the database's own constraints (e.g. `grade` is restricted to the same set of letter grades as the SQL `CHECK`, phone numbers follow the same regex). Invalid requests are rejected with `422` before touching the database.
- **Database errors surfaced as HTTP errors** — constraint violations and trigger failures (duplicate enrollment, credit-hour limit, section capacity) raise MySQL errors that are caught and returned as `400` responses with the original message, instead of crashing the server.
- **Partial updates** — `PATCH` endpoints (e.g. `/students/{id}`, `/enrollments/{student_id}/{course_id}`) only require the fields being changed. For `Enrollment` specifically, only `grade` can be patched; the key columns (`S_ID`, `Sec_ID`, `C_ID`) are treated as identity, not as editable fields — changing them means deleting and recreating the enrollment.
- **Credentials** — the API never hardcodes database credentials; `database.py` loads them from a local `.env` file (not committed to the repo).

---

## Setup & How to Run

### Step 1 — Create the Database
Open MySQL Workbench or the MySQL CLI and run:
```sql
source university_db.sql;
```
This creates the `university_db` database, all tables, inserts sample data, and creates the triggers.

### Step 2 — Configure Credentials
Create a `.env` file in the project root (not committed to git):
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=university_db
```

### Step 3 — Install Dependencies

For the GUI:
```bash
pip install customtkinter mysql-connector-python Pillow python-dotenv
```

For the API:
```bash
pip install -r requirements.txt
```

### Step 4 — Run

GUI:
```bash
python GUI_DB.py
```

API:
```bash
uvicorn main:app --reload
```
Then open `http://127.0.0.1:8000/docs` to explore and test the endpoints.

---

## Requirements

- MySQL Server (running locally)
- Python 3.8+

GUI:
```
customtkinter
mysql-connector-python
Pillow
python-dotenv
```

API (`requirements.txt`):
```
fastapi
uvicorn
mysql-connector-python
python-dotenv
pydantic
```
```