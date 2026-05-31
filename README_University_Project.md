# University Management System

A full-stack university database project combining a relational MySQL database with a desktop GUI application. The SQL schema defines and populates the entire university data model, and the GUI provides a complete CRUD interface on top of it — no SQL knowledge required to operate the system.

---

## Project Files

| File | Role |
|---|---|
| `university_db.sql` | Creates the database, all tables, constraints, triggers, and inserts sample data |
| `GUI_DB.py` | Desktop GUI app that connects to the database and provides full CRUD management |

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

A 1000×750 desktop window built with **CustomTkinter**. Connects directly to `university_db` on localhost and provides a point-and-click interface for all 7 tables — no SQL needed.

### Application Structure

```
GUI_DB.py
│
├── DB Config & connect_db()            # MySQL connection handler
│
├── CRUD Helpers
│   ├── sql_fetch_list()                # Generic SELECT
│   ├── insert_dynamic()                # Dynamic INSERT (builds SQL from field config)
│   ├── update_record()                 # Dynamic UPDATE by primary key
│   └── delete_by_pk()                 # DELETE by primary key
│
├── show_main_menu()                    # 7-button main navigation screen
├── open_manage_screen()                # Splits view: left panel + right data table
├── refresh_table()                     # Reloads Treeview from DB after every operation
│
├── Form Builders
│   ├── build_widget_for_field()        # Renders Entry or ComboBox per field type
│   └── update_composite_fk_options()  # Filters Sec_ID dropdown based on selected C_ID
│
├── show_add_panel()                    # Add form with mandatory field validation
├── show_update_panel()                 # Update form (auto-fills from selected row)
└── delete_selected_row()              # Delete with confirmation dialog
```

### Screens

| Screen | Table | Auto PK | Special Behavior |
|---|---|---|---|
| Manage Students | `Student` | Yes (`S_ID`) | Department & level dropdowns |
| Manage Courses | `Course` | No | Credits dropdown (0–3) |
| Manage Instructors | `Instructor` | Yes (`I_ID`) | Department dropdown |
| Manage Departments | `Department` | No | — |
| Manage Sections | `Section` | No | Course dropdown; Sec_ID auto-filtered by selected Course |
| Manage Student Phones | `Student_Phone` | No | Student dropdown |
| Manage Enrollments | `Enrollment` | No | Student/Course/Grade dropdowns; composite FK validation |

### Composite FK Logic
When managing **Enrollments** or **Sections**, selecting a `C_ID` (Course) dynamically updates the `Sec_ID` dropdown to show only sections that belong to that course — prevents invalid FK combinations before they hit the database.

---

## Setup & How to Run

### Step 1 — Create the Database
Open MySQL Workbench or the MySQL CLI and run:
```sql
source university_db.sql;
```
This creates the `university_db` database, all tables, inserts sample data, and creates the triggers.

### Step 2 — Configure DB Credentials
Open `GUI_DB.py` and update:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",   # ← change this
    "database": "university_db"
}
```

### Step 3 — Install Python Dependencies
```bash
pip install customtkinter mysql-connector-python Pillow
```

### Step 4 — Run the App
```bash
python GUI_DB.py
```

---

## Requirements

- MySQL Server (running locally)
- Python 3.8+

```
customtkinter
mysql-connector-python
Pillow
```
