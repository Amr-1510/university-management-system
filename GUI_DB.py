from customtkinter import *
from tkinter import ttk, messagebox
from PIL import Image
import mysql.connector

# -------------------- DB CONFIG --------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456@Amory",
    "database": "university_db"
}

def connect_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"{err}")
        return None

# -------------------- MAIN WINDOW --------------------
window = CTk()
window.geometry("1000x750")
window.title("University Management System")
window.resizable(False, False)

# -------------------- Global state --------------------
main_menu_frame = None
manage_frame = None
table_frame = None
form_area = None

window.current_tree = None
window.selected_row = None
current_form_entries = {}
current_fields = []
current_table = ""
current_cfg = {}

# -------------------- Helpers --------------------
def clear_window():
    for w in window.winfo_children():
        w.destroy()

def sql_fetch_list(query, params=()):
    conn = connect_db()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("SQL Error", str(e))
        return []
    finally:
        cur.close()
        conn.close()

def insert_dynamic(table_name, fields, values_map, auto_pk=False):
    cols = []
    vals = []
    start_index = 1 if auto_pk else 0
    
    for f in fields[start_index:]:
        v = values_map.get(f, "")
        if v is None:
            continue
        v = v.strip() if isinstance(v, str) else v
        if v == "" or v == "Select":
            continue
        cols.append(f)
        vals.append(v)
    
    if not cols:
        messagebox.showwarning("No data", "No values to insert.")
        return False
    
    placeholders = ", ".join(["%s"] * len(cols))
    sql_cols = ", ".join(cols)
    sql = f"INSERT INTO {table_name} ({sql_cols}) VALUES ({placeholders})"
    conn = connect_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute(sql, vals)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("SQL Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def update_record(table_name, fields, values_map):
    pk = fields[0]
    pk_val = values_map.get(pk, "").strip()
    if not pk_val:
        messagebox.showwarning("Missing PK", f"Please provide/select {pk}.")
        return False
    set_clause = ", ".join([f"{f}=%s" for f in fields[1:]])
    vals = [values_map.get(f, "").strip() or None for f in fields[1:]] + [pk_val]
    sql = f"UPDATE {table_name} SET {set_clause} WHERE {pk}=%s"
    conn = connect_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute(sql, vals)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("SQL Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

def delete_by_pk(table_name, pk_field, pk_value):
    conn = connect_db()
    if conn is None:
        return False
    cur = conn.cursor()
    try:
        cur.execute(f"DELETE FROM {table_name} WHERE {pk_field}=%s", (pk_value,))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        messagebox.showerror("SQL Error", str(e))
        return False
    finally:
        cur.close()
        conn.close()

# -------------------- UI helpers --------------------
def label_with_req(text, required=False):
    return text + (" *" if required else "")

# -------------------- MAIN MENU --------------------
def show_main_menu():
    clear_window()
    global main_menu_frame
    main_menu_frame = CTkFrame(window)
    main_menu_frame.pack(fill="both", expand=True, padx=20, pady=20)

    CTkLabel(main_menu_frame, text="Main Menu", font=("Arial", 30)).pack(pady=12)

    button_info = [
        ("Manage Students", "Students", "Student",
         ["S_ID","Dep_ID","Fname","Lname","Email","std_level"],
         {"mandatory":["Dep_ID","Fname","Lname"], 
          "combobox":{"Dep_ID":"Department","std_level":["1","2","3","4"]}, 
          "auto_pk": True}),

        ("Manage Courses", "Courses", "Course",
         ["C_ID","Cname","Credits","Dep_ID"],
         {"mandatory":["C_ID","Cname","Credits","Dep_ID"], 
          "combobox":{"Credits":["0","1","2","3"], "Dep_ID":"Department"}, 
          "auto_pk": False}),

        ("Manage Instructors", "Instructors", "Instructor",
         ["I_ID","Dep_ID","Iname","Email","Salary"], 
         {"mandatory":["Iname"], "combobox":{"Dep_ID":"Department"}, "auto_pk": True}),

        ("Manage Departments", "Departments", "Department",
         ["Dep_ID","Dname","Room","Floor"],
         {"mandatory":["Dep_ID"], "combobox":{}, "auto_pk": False}),

        ("Manage Sections", "Sections", "Section",
         ["Sec_ID","C_ID","Sec_name","Hall","I_ID"],
         {"mandatory":["Sec_ID","C_ID"], "combobox":{"C_ID":"Course","I_ID":"Instructor"}, "auto_pk": False}),

        ("Manage Student Phones", "Student Phones", "Student_Phone",
         ["Phone_number","S_ID"],
         {"mandatory":["Phone_number","S_ID"], "combobox":{"S_ID":"Student"}, "auto_pk": False}),

        ("Manage Enrollments", "Enrollments", "Enrollment",
         ["S_ID","Sec_ID","C_ID","grade"],
         {"mandatory":["S_ID","C_ID"], 
          "combobox":{"S_ID":"Student","C_ID":"Course","grade":["A+","A","A-","B+","B","B-","C+","C","C-","D+","D","D-","F"]},
          "composite_fk": {"Sec_ID": ("Section", ["Sec_ID", "C_ID"], "C_ID")},
          "auto_pk": False})
    ]

    for txt, disp, tbl, fields, cfg in button_info:
        CTkButton(main_menu_frame, text=txt, width=700, height=60,
                  command=lambda d=disp, t=tbl, f=fields, c=cfg: open_manage_screen(d,t,f,c)).pack(pady=8)

# -------------------- Manage Screen --------------------
def open_manage_screen(display_name, table_name, fields, cfg):
    clear_window()
    global manage_frame, table_frame, form_area, current_fields, current_table, current_cfg, current_form_entries
    current_fields = fields
    current_table = table_name
    current_cfg = cfg
    current_form_entries = {}

    top = CTkFrame(window)
    top.pack(fill="x")
    CTkButton(top, text="← Back to Main Menu", width=150, command=show_main_menu).pack(side="left", padx=8, pady=8)
    CTkLabel(top, text=f"Manage {display_name}", font=("Arial", 24)).pack(pady=6)

    manage_frame = CTkFrame(window, width=320)
    manage_frame.pack(side="left", fill="y", padx=10, pady=10)

    table_frame = CTkFrame(window)
    table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    CTkButton(manage_frame, text="Add Record", width=260,
              command=lambda: show_add_panel(display_name, table_name, fields, cfg)).pack(pady=6)
    CTkButton(manage_frame, text="Update Record", width=260,
              command=lambda: show_update_panel(display_name, table_name, fields, cfg)).pack(pady=6)
    CTkButton(manage_frame, text="Delete Selected", width=260,
              command=lambda: delete_selected_row(table_name, fields)).pack(pady=6)

    refresh_table(table_name, fields)

# -------------------- Table (Treeview) --------------------
def refresh_table(table_name, fields):
    for w in table_frame.winfo_children():
        w.destroy()

    cols = fields
    tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    table_frame.grid_rowconfigure(0, weight=1)
    table_frame.grid_columnconfigure(0, weight=1)

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120, anchor="center")

    conn = connect_db()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT {', '.join(cols)} FROM {table_name}")
        rows = cur.fetchall()
        for r in rows:
            tree.insert("", "end", values=r)
    except mysql.connector.Error as e:
        messagebox.showerror("SQL Error", str(e))
    finally:
        cur.close()
        conn.close()

    def on_select(evt):
        sel = tree.focus()
        if not sel:
            return
        window.selected_row = tree.item(sel, "values")
        fill_update_fields_from_selection()

    tree.bind("<<TreeviewSelect>>", on_select)
    window.current_tree = tree

# -------------------- Form utilities --------------------
def clear_form_area():
    for child in list(manage_frame.winfo_children()):
        if isinstance(child, CTkFrame):
            child.destroy()

def build_widget_for_field(parent, field, cfg, for_add=True):
    mandatory = cfg.get("mandatory", [])
    comboconf = cfg.get("combobox", {})
    composite_fk = cfg.get("composite_fk", {})
    auto_pk = cfg.get("auto_pk", False)

    row = CTkFrame(parent)
    row.pack(fill="x", pady=3)
    required = (field in mandatory)
    CTkLabel(row, text=label_with_req(field, required), width=14, anchor="w").pack(side="left", padx=4)

    if auto_pk and for_add and field == current_fields[0]:
        ent = CTkEntry(row, width=180)
        ent.insert(0, "Auto")
        ent.configure(state="disabled")
        ent.pack(side="right", padx=4)
        return ent

    # Handle composite foreign key (Sec_ID depends on C_ID)
    if field in composite_fk:
        table_ref, composite_cols, depends_on = composite_fk[field]
        cb = CTkComboBox(row, values=["Select"], width=180, state="readonly")
        cb.set("Select")
        cb.pack(side="right", padx=4)
        
        # Store reference for dynamic update
        cb._composite_ref = (table_ref, composite_cols, depends_on)
        cb._depends_on = depends_on
        return cb

    if field in comboconf:
        conf = comboconf[field]
        if isinstance(conf, list):
            values = [str(v) for v in conf]
        else:
            pk_mapping = {
                "Student": "S_ID",
                "Course": "C_ID",
                "Instructor": "I_ID",
                "Department": "Dep_ID",
                "Section": "Sec_ID"
            }
            pk_field = pk_mapping.get(conf, f"{conf}_ID")
            rows = sql_fetch_list(f"SELECT {pk_field} FROM {conf}")
            values = [str(r[0]) for r in rows]
        cb = CTkComboBox(row, values=values, width=180)
        cb.set("Select")
        cb.pack(side="right", padx=4)
        
        # If this field affects composite FK, bind update
        composite_fk_cfg = cfg.get("composite_fk", {})
        for fk_field, (tbl, cols, dep) in composite_fk_cfg.items():
            if dep == field:
                def on_change(choice, fk=fk_field):
                    update_composite_fk_options(fk)
                cb.configure(command=on_change)
        
        return cb
    else:
        ent = CTkEntry(row, width=180)
        ent.pack(side="right", padx=4)
        return ent

def update_composite_fk_options(fk_field):
    """Update Sec_ID options based on selected C_ID"""
    if fk_field not in current_form_entries:
        return
    
    fk_widget = current_form_entries[fk_field]
    if not hasattr(fk_widget, '_composite_ref'):
        return
    
    table_ref, composite_cols, depends_on = fk_widget._composite_ref
    
    # Get the value of the dependent field (C_ID)
    if depends_on not in current_form_entries:
        return
    
    dep_widget = current_form_entries[depends_on]
    try:
        dep_value = dep_widget.get().strip()
    except:
        dep_value = ""
    
    if not dep_value or dep_value == "Select":
        fk_widget.configure(values=["Select"])
        fk_widget.set("Select")
        return
    
    # Query sections for this course
    query = f"SELECT {composite_cols[0]} FROM {table_ref} WHERE {composite_cols[1]}=%s"
    rows = sql_fetch_list(query, (dep_value,))
    values = [str(r[0]) for r in rows]
    
    if not values:
        values = ["Select"]
    
    fk_widget.configure(values=values)
    fk_widget.set("Select")

# -------------------- Add Panel --------------------
def show_add_panel(display_name, table_name, fields, cfg):
    clear_form_area()
    global form_area, current_form_entries
    form_area = CTkFrame(manage_frame)
    form_area.pack(pady=6, fill="x")
    CTkLabel(form_area, text=f"Add {display_name}", font=("Arial", 16)).pack(pady=6)

    current_form_entries = {}
    for f in fields:
        w = build_widget_for_field(form_area, f, cfg, for_add=True)
        current_form_entries[f] = w

    def validate_and_add():
        values_map = {}
        for f, w in current_form_entries.items():
            try:
                v = w.get().strip()
            except Exception:
                v = ""
            values_map[f] = v
        for req in cfg.get("mandatory", []):
            if not values_map.get(req) or values_map.get(req) == "Select":
                messagebox.showwarning("Missing", f"{req} is required.")
                return
        
        # Validate composite FK
        composite_fk = cfg.get("composite_fk", {})
        for fk_field, (tbl, cols, dep) in composite_fk.items():
            fk_val = values_map.get(fk_field, "")
            dep_val = values_map.get(dep, "")
            if fk_val and fk_val != "Select" and dep_val and dep_val != "Select":
                # Check if this Sec_ID exists for this C_ID
                check_query = f"SELECT COUNT(*) FROM {tbl} WHERE {cols[0]}=%s AND {cols[1]}=%s"
                result = sql_fetch_list(check_query, (fk_val, dep_val))
                if result and result[0][0] == 0:
                    messagebox.showerror("Invalid", f"Section {fk_val} does not exist for Course {dep_val}")
                    return
        
        ok = insert_dynamic(table_name, fields, values_map, auto_pk=cfg.get("auto_pk", False))
        if ok:
            messagebox.showinfo("Added", "Record added successfully.")
            refresh_table(table_name, fields)
            clear_form_area()

    CTkButton(form_area, text="Add", width=160, command=validate_and_add).pack(pady=8)

# -------------------- Update Panel --------------------
def show_update_panel(display_name, table_name, fields, cfg):
    clear_form_area()
    global form_area, current_form_entries
    form_area = CTkFrame(manage_frame)
    form_area.pack(pady=6, fill="x")
    CTkLabel(form_area, text=f"Update {display_name}  (select a row)", font=("Arial", 14)).pack(pady=6)

    current_form_entries = {}
    for f in fields:
        w = build_widget_for_field(form_area, f, cfg, for_add=False)
        current_form_entries[f] = w

    selected = getattr(window, "selected_row", None)
    if selected:
        fill_form_with_values(selected, fields)

    def validate_and_update():
        values_map = {}
        for f, w in current_form_entries.items():
            try:
                v = w.get().strip()
            except Exception:
                v = ""
            values_map[f] = v
        for req in cfg.get("mandatory", []):
            if not values_map.get(req) or values_map.get(req) == "Select":
                messagebox.showwarning("Missing", f"{req} is required.")
                return
        
        # Validate composite FK
        composite_fk = cfg.get("composite_fk", {})
        for fk_field, (tbl, cols, dep) in composite_fk.items():
            fk_val = values_map.get(fk_field, "")
            dep_val = values_map.get(dep, "")
            if fk_val and fk_val != "Select" and dep_val and dep_val != "Select":
                check_query = f"SELECT COUNT(*) FROM {tbl} WHERE {cols[0]}=%s AND {cols[1]}=%s"
                result = sql_fetch_list(check_query, (fk_val, dep_val))
                if result and result[0][0] == 0:
                    messagebox.showerror("Invalid", f"Section {fk_val} does not exist for Course {dep_val}")
                    return
        
        ok = update_record(table_name, fields, values_map)
        if ok:
            messagebox.showinfo("Updated", "Record updated successfully.")
            refresh_table(table_name, fields)
            clear_form_area()

    CTkButton(form_area, text="Update", width=160, command=validate_and_update).pack(pady=8)

def fill_form_with_values(selected, fields):
    """Fill form with selected row values"""
    for i, f in enumerate(fields):
        w = current_form_entries.get(f)
        if not w:
            continue
        val = str(selected[i]) if selected[i] is not None else ""
        
        try:
            if isinstance(w, CTkComboBox):
                # For composite FK, update options first
                if hasattr(w, '_depends_on'):
                    dep_field = w._depends_on
                    if dep_field in current_form_entries:
                        dep_widget = current_form_entries[dep_field]
                        dep_val = str(selected[fields.index(dep_field)])
                        if isinstance(dep_widget, CTkComboBox):
                            dep_widget.set(dep_val)
                        update_composite_fk_options(f)
                
                if val in w._values:
                    w.set(val)
                else:
                    w.set("Select")
            else:
                w.delete(0, "end")
                w.insert(0, val)
        except Exception as e:
            pass

def fill_update_fields_from_selection():
    selected = getattr(window, "selected_row", None)
    if not selected or not current_form_entries:
        return
    fill_form_with_values(selected, current_fields)

# -------------------- Delete Selected --------------------
def delete_selected_row(table_name, fields):
    tree = getattr(window, "current_tree", None)
    if tree is None:
        messagebox.showwarning("No table", "No table available.")
        return
    sel = tree.focus()
    if not sel:
        messagebox.showwarning("No selection", "Please select a row to delete.")
        return
    vals = tree.item(sel, "values")
    pk_field = fields[0]
    pk_val = vals[0]
    if messagebox.askyesno("Confirm Delete", f"Delete record {pk_val}?"):
        ok = delete_by_pk(table_name, pk_field, pk_val)
        if ok:
            messagebox.showinfo("Deleted", "Record deleted.")
            refresh_table(table_name, fields)
            clear_form_area()

# -------------------- Start --------------------
show_main_menu()
window.mainloop()