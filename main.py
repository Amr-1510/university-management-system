"""University REST API. Run: uvicorn main:app --reload"""
from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException, Response, status
from mysql.connector import Error as MySQLError
from pydantic import BaseModel, ConfigDict, Field

from database import get_db

app = FastAPI(title="University Management API", version="1.0.0")


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Department(Model):
    Dep_ID: str = Field(min_length=1, max_length=30)
    Dname: str = Field(min_length=1, max_length=30)
    Room: str | None = Field(default=None, max_length=20)
    Floor: int = Field(ge=0)


class StudentCreate(Model):
    Dep_ID: str
    Fname: str
    Lname: str
    Email: str | None = None
    std_level: int = Field(default=1, ge=1, le=4)


class StudentUpdate(Model):
    Dep_ID: str | None = None
    Fname: str | None = None
    Lname: str | None = None
    Email: str | None = None
    std_level: int | None = Field(default=None, ge=1, le=4)


class InstructorCreate(Model):
    Dep_ID: str
    Iname: str
    Email: str | None = None
    Salary: Decimal | None = Field(default=None, gt=0)


class InstructorUpdate(InstructorCreate):
    Dep_ID: str | None = None
    Iname: str | None = None


class Course(Model):
    C_ID: str
    Cname: str
    Credits: int = Field(ge=0, le=3)
    Dep_ID: str


class Section(Model):
    Sec_ID: int = Field(gt=0)
    C_ID: str
    Sec_name: str | None = None
    Hall: str | None = None
    I_ID: int | None = None


class StudentPhone(Model):
    Phone_number: str = Field(pattern=r"^(010|011|012|015)[0-9]{8}$")
    S_ID: int


class Enrollment(Model):
    S_ID: int
    Sec_ID: int = Field(gt=0)
    C_ID: str
    grade: str | None = Field(default=None, pattern=r"^(A\+|A|A-|B\+|B|B-|C\+|C|C-|D\+|D|D-|F)$")

class EnrollmentUpdate(Model):
    grade: str | None = Field(default=None, pattern=r"^(A\+|A|A-|B\+|B|B-|C\+|C|C-|D\+|D|D-|F)$")

def db_error(error: MySQLError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(error))


def rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    try:
        with get_db() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(sql, params)
                return cursor.fetchall()
            finally:
                cursor.close()
    except MySQLError as error:
        raise db_error(error) from error


def row(sql: str, params: tuple[Any, ...]) -> dict[str, Any]:
    result = rows(sql, params)
    if not result:
        raise HTTPException(status_code=404, detail="Record not found")
    return result[0]


def add(table: str, values: dict[str, Any]) -> int | None:
    columns = list(values)
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    try:
        with get_db() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(sql, tuple(values.values()))
                connection.commit()
                return cursor.lastrowid or None
            finally:
                cursor.close()
    except MySQLError as error:
        raise db_error(error) from error


def edit(table: str, values: dict[str, Any], where: str, params: tuple[Any, ...]) -> None:
    if not values:
        raise HTTPException(status_code=400, detail="No fields were supplied")
    assignments = ", ".join(f"{key} = %s" for key in values)
    try:
        with get_db() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(f"UPDATE {table} SET {assignments} WHERE {where}", tuple(values.values()) + params)
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Record not found")
                connection.commit()
            finally:
                cursor.close()
    except MySQLError as error:
        raise db_error(error) from error


def remove(table: str, where: str, params: tuple[Any, ...]) -> Response:
    try:
        with get_db() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(f"DELETE FROM {table} WHERE {where}", params)
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Record not found")
                connection.commit()
            finally:
                cursor.close()
    except MySQLError as error:
        raise db_error(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/health")
def health():
    rows("SELECT 1")
    return {"status": "ok"}


@app.get("/departments")
def list_departments(): return rows("SELECT * FROM Department ORDER BY Dep_ID")
@app.get("/departments/{dep_id}")
def get_department(dep_id: str): return row("SELECT * FROM Department WHERE Dep_ID=%s", (dep_id,))
@app.post("/departments", status_code=201)
def create_department(item: Department):
    add("Department", item.model_dump()); return get_department(item.Dep_ID)
@app.put("/departments/{dep_id}")
def update_department(dep_id: str, item: Department):
    edit("Department", item.model_dump(), "Dep_ID=%s", (dep_id,)); return get_department(item.Dep_ID)
@app.delete("/departments/{dep_id}", status_code=204)
def delete_department(dep_id: str): return remove("Department", "Dep_ID=%s", (dep_id,))


@app.get("/students")
def list_students(): return rows("SELECT * FROM Student ORDER BY S_ID")
@app.get("/students/{student_id}")
def get_student(student_id: int): return row("SELECT * FROM Student WHERE S_ID=%s", (student_id,))
@app.post("/students", status_code=201)
def create_student(item: StudentCreate):
    return get_student(add("Student", item.model_dump()))
@app.patch("/students/{student_id}")
def update_student(student_id: int, item: StudentUpdate):
    edit("Student", item.model_dump(exclude_unset=True), "S_ID=%s", (student_id,)); return get_student(student_id)
@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int): return remove("Student", "S_ID=%s", (student_id,))


@app.get("/instructors")
def list_instructors(): return rows("SELECT * FROM Instructor ORDER BY I_ID")
@app.get("/instructors/{instructor_id}")
def get_instructor(instructor_id: int): return row("SELECT * FROM Instructor WHERE I_ID=%s", (instructor_id,))
@app.post("/instructors", status_code=201)
def create_instructor(item: InstructorCreate): return get_instructor(add("Instructor", item.model_dump()))
@app.patch("/instructors/{instructor_id}")
def update_instructor(instructor_id: int, item: InstructorUpdate):
    edit("Instructor", item.model_dump(exclude_unset=True), "I_ID=%s", (instructor_id,)); return get_instructor(instructor_id)
@app.delete("/instructors/{instructor_id}", status_code=204)
def delete_instructor(instructor_id: int): return remove("Instructor", "I_ID=%s", (instructor_id,))


@app.get("/courses")
def list_courses(): return rows("SELECT * FROM Course ORDER BY C_ID")
@app.post("/courses", status_code=201)
def create_course(item: Course):
    add("Course", item.model_dump()); return row("SELECT * FROM Course WHERE C_ID=%s", (item.C_ID,))
@app.put("/courses/{course_id}")
def update_course(course_id: str, item: Course):
    edit("Course", item.model_dump(), "C_ID=%s", (course_id,)); return row("SELECT * FROM Course WHERE C_ID=%s", (item.C_ID,))
@app.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: str): return remove("Course", "C_ID=%s", (course_id,))


@app.get("/sections")
def list_sections(): return rows("SELECT * FROM Section ORDER BY C_ID, Sec_ID")
@app.post("/sections", status_code=201)
def create_section(item: Section):
    add("Section", item.model_dump()); return item
@app.put("/sections/{course_id}/{section_id}")
def update_section(course_id: str, section_id: int, item: Section):
    edit("Section", item.model_dump(), "C_ID=%s AND Sec_ID=%s", (course_id, section_id)); return item
@app.delete("/sections/{course_id}/{section_id}", status_code=204)
def delete_section(course_id: str, section_id: int): return remove("Section", "C_ID=%s AND Sec_ID=%s", (course_id, section_id))


@app.get("/student-phones")
def list_phones(): return rows("SELECT * FROM Student_Phone ORDER BY S_ID, Phone_number")
@app.post("/student-phones", status_code=201)
def create_phone(item: StudentPhone): add("Student_Phone", item.model_dump()); return item
@app.put("/student-phones/{phone_number}")
def update_phone(phone_number: str, item: StudentPhone):
    edit("Student_Phone", item.model_dump(), "Phone_number=%s", (phone_number,)); return item
@app.delete("/student-phones/{phone_number}", status_code=204)
def delete_phone(phone_number: str): return remove("Student_Phone", "Phone_number=%s", (phone_number,))


@app.get("/enrollments")
def list_enrollments(): return rows("SELECT * FROM Enrollment ORDER BY S_ID, C_ID")
@app.post("/enrollments", status_code=201)
def create_enrollment(item: Enrollment): add("Enrollment", item.model_dump()); return item
@app.patch("/enrollments/{student_id}/{course_id}")
def update_enrollment(student_id: int, course_id: str, item: EnrollmentUpdate):
    edit("Enrollment", item.model_dump(exclude_unset=True), "S_ID=%s AND C_ID=%s", (student_id, course_id))
    return row("SELECT * FROM Enrollment WHERE S_ID=%s AND C_ID=%s", (student_id, course_id))
@app.delete("/enrollments/{student_id}/{course_id}", status_code=204)
def delete_enrollment(student_id: int, course_id: str): return remove("Enrollment", "S_ID=%s AND C_ID=%s", (student_id, course_id))
