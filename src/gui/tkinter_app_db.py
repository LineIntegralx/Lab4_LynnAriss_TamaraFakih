#!/usr/bin/env python3
"""
.. module:: src.gui.tkinter_app_db
   :synopsis: tkinter app for a small school management system (db-backed). i use it to create/update/delete students, instructors, and courses; register students; search; and export/import json/csv. also a quick sqlite backup.

:author: tamara fakih
:project: ece/eece435l – software tools lab (fall 2025–2026)
:version: 1.0.0
:license: educational / course use

**why this file exists (short honest note)**
   documentation gets ignored when deadlines are close, but we still need to understand our own code later.
   so i’m adding module docs in sphinx style now, and i’ll let sphinx build a clean website from it.

**what this module wires together**
   - tkinter/ttk ui (tabs for students, instructors, courses, relations, records/search, json/io)
   - sqlite repository adapter (single instance), with basic validators and json helpers
   - a light aub-ish theme so the tables don’t look painful

**how i run it**
   >>> python -m src.gui.tkinter_app_db
   (or run the file directly if imports resolve)

**notes**
   this is lab-level code: clarity > clever tricks. i keep the sql readable and the handlers explicit.
"""

from __future__ import annotations  # keep type hints without breaking runtime

import sys
import pathlib
from typing import Iterable, List, Dict
from datetime import datetime
import csv

# ensure project root is importable when running this file directly
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# ui stack
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

# small theme (aub-ish, nothing too fancy)
PRIMARY = '#7b002c'
PRIMARY_DARK = '#5a001f'
PRIMARY_LIGHT = '#b34c73'
SURFACE = '#ffffff'
BG = '#fbf8f7'
STRIPE = '#f4eaee'
SELECT_BG = '#ead6df'
TEXT = '#222222'

# app layers: db repo, json i/o, validators, domain models
from db.sqlite_repo import SQLiteRepository
from src.persistence.json_store import save_to_json, load_from_json

from src.validation.validators import (
    is_valid_person_name, is_non_negative_int, is_valid_email,
    is_valid_student_id, is_valid_instructor_id,
    is_valid_course_id, is_valid_course_name,
    norm_name, norm_email, norm_id
)

from src.models import Student, Instructor, Course


class App(tk.Tk):
    """
    a tkinter main window for the small school management system. not trying to be super abstract;
    this is basically the gui shell that wires the db repo + validators + json helpers into tabs.

    :param args: nothing special for now (no external args expected)
    :type args: None

    :ivar repo: sqlite repository the whole app uses to talk to the db
    :vartype repo: SQLiteRepository
    :ivar logo_img: optional app logo if found on disk, otherwise None (no problem)
    :vartype logo_img: tkinter.PhotoImage or None
    :ivar tree_students: table widget that lists students (id, name, age, email, courses)
    :vartype tree_students: ttk.Treeview
    :ivar tree_instructors: table widget for instructors
    :vartype tree_instructors: ttk.Treeview
    :ivar tree_courses: table widget for courses
    :vartype tree_courses: ttk.Treeview
    :ivar rec_students: small dict with a frame and a tree for the search view (students)
    :vartype rec_students: dict
    :ivar rec_instructors: same idea as above but for instructors
    :vartype rec_instructors: dict
    :ivar rec_courses: same idea as above but for courses
    :vartype rec_courses: dict

    :notes: tabs are: students / instructors / courses / register-assign / records-search / json.
            theme is mild aub-ish. i keep handlers explicit and sql readable because… future me will thank me.
    """
    def __init__(self) -> None:
        """
        sets up the main window and the bare essentials: title/size/scaling, a small ttk theme,
        opens the sqlite repo, tries to load a logo if available, builds all tabs, then refreshes so
        tables don’t look empty. kind of the boot sequence, nothing too dramatic.

        :return: nothing; just prepares ui + state
        :rtype: None
        :raises RuntimeError: if tkinter/init goes really wrong or repo setup bubbles a hard error (rare)
        """
        super().__init__()
        # basic window config so the ui has room to breathe
        self.title("School Management System (DB)")
        self.geometry("1180x740")
        self.minsize(1000, 640)
        try:
            # some platforms ignore this, that’s fine
            self.tk.call('tk', 'scaling', 1.2)
        except Exception:
            pass

        self._setup_theme()              # set ttk styles, fonts, colors
        self.repo = SQLiteRepository()   # single db adapter for the whole app
        self.logo_img = self._load_logo()  # optional logo if found
        self._build_ui()                 # create all tabs and widgets
        self._refresh_all_views()        # initial data load into tables

    def _setup_theme(self) -> None:
        """
        sets up a small ttk theme so the ui stays readable and a bit “ours”. i try 'clam' if it exists,
        set base fonts/colors, and tweak tables/buttons (zebra rows, bold headings, a light accent).

        :return: nothing; just mutates ttk styles + window look
        :rtype: None
        :notes: choices are practical for lab machines; if the theme isn’t there it’s ok, it silently falls back.
        """
        # small ttk styling to keep things readable and a bit branded
        style = ttk.Style(self)
        try:
            style.theme_use('clam')  # decent cross-platform base
        except Exception:
            pass

        # fonts: segoue ui reads well on windows; acceptable elsewhere
        tkfont.nametofont('TkDefaultFont').configure(family='Segoe UI', size=10)
        tree_font = tkfont.Font(family='Segoe UI', size=10)
        heading_font = tkfont.Font(family='Segoe UI', size=11, weight='bold')

        # background on common containers
        self.configure(bg=BG)
        for n in ('TFrame', 'TLabelframe', 'TLabel'):
            style.configure(n, background=BG)

        # notebook tabs and labels
        style.configure('TLabelframe.Label', background=BG, foreground=PRIMARY)
        style.configure('TLabel', foreground=TEXT)
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', padding=(14, 8), font=('Segoe UI', 11))
        style.map('TNotebook.Tab',
                  background=[('selected', SURFACE)],
                  foreground=[('selected', PRIMARY)])

        # buttons with a mild accent for primary actions
        style.configure('TButton', padding=6)
        style.configure('Accent.TButton', background=PRIMARY, foreground='white')
        style.map('Accent.TButton',
                  background=[('active', PRIMARY_DARK), ('pressed', PRIMARY_DARK)])

        # treeview tables: zebra rows and bold headers
        style.configure('Treeview', background=SURFACE, fieldbackground=SURFACE,
                        foreground=TEXT, rowheight=26, font=tree_font,
                        bordercolor=PRIMARY_LIGHT, borderwidth=0)
        style.map('Treeview', background=[('selected', SELECT_BG)])
        style.configure('Treeview.Heading', font=heading_font,
                        background=PRIMARY, foreground='white')
        style.map('Treeview.Heading', background=[('active', PRIMARY_DARK)])

    def _load_logo(self):
        """
        tries to load a small logo from a few usual places; if it exists, i scale it down
        to around 320px width so it doesn’t take over the header, then return it. if loading
        complains, i just skip it and move on.

        :return: photo image you can drop in a ttk.Label, or None if not found/failed
        :rtype: tkinter.PhotoImage or None
        :notes: checks these paths (in order): 'logo.png', 'data/logo.png', 'assets/logo.png', 'resources/logo.png'
        """
        # look for a logo in a few common places, scale if too wide
        for rel in ('logo.png', 'data/logo.png', 'assets/logo.png', 'resources/logo.png'):
            p = ROOT / rel
            if p.exists():
                try:
                    img = tk.PhotoImage(file=str(p))
                    if img.width() > 320:
                        # subsample keeps proportions without extra math
                        factor = max(1, img.width() // 320)
                        img = img.subsample(factor, factor)
                    return img
                except Exception:
                    # if it fails to load, simply skip it
                    pass
        return None

    def _add_header(self, parent: tk.Widget, title: str) -> None:
        """
        adds a tiny header bar to a container: optional logo on the left and the given title next to it.
        keeps spacing light and lets the title stretch so it aligns nicely.

        :param parent: the tk/ttk container where the header should be placed
        :type parent: tkinter.Widget
        :param title: the text to show as the section title
        :type title: str

        :return: nothing; it just builds and grids the header widgets
        :rtype: None
        :notes: if logo_img is None we just render the text label, no problem.
        """
        # small header row with optional logo + section title
        bar = ttk.Frame(parent)
        bar.grid(row=0, column=0, columnspan=8, sticky='ew', padx=10, pady=(8, 2))
        bar.columnconfigure(1, weight=1)
        if self.logo_img is not None:
            ttk.Label(bar, image=self.logo_img, background=BG).grid(row=0, column=0, sticky='w')
        ttk.Label(bar, text=title, font=('Segoe UI Semibold', 16),
                  foreground=PRIMARY, background=BG).grid(row=0, column=1, sticky='w', padx=10)

    def _build_ui(self) -> None:
        """
        builds the main notebook ui: creates the tabs (students, instructors, courses,
        register/assign, records/search, json) and mounts them on the window. then it calls
        the per-tab builders to fill each page. straightforward layout, no tricks.

        :return: nothing; just mutates the window by adding widgets
        :rtype: None
        :notes: grid config lets the notebook stretch; tabs are created first then populated,
                which keeps the flow easier to follow when reading the code.
        """
        # create the notebook and the six tabs
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        nb = ttk.Notebook(self)
        nb.grid(row=0, column=0, sticky="nsew")

        # tabs
        self.tab_students = ttk.Frame(nb)
        self.tab_instructors = ttk.Frame(nb)
        self.tab_courses = ttk.Frame(nb)
        self.tab_relations = ttk.Frame(nb)
        self.tab_records = ttk.Frame(nb)
        self.tab_io = ttk.Frame(nb)

        # attach to notebook
        nb.add(self.tab_students, text="Students")
        nb.add(self.tab_instructors, text="Instructors")
        nb.add(self.tab_courses, text="Courses")
        nb.add(self.tab_relations, text="Register / Assign")
        nb.add(self.tab_records, text="Records & Search")
        nb.add(self.tab_io, text="JSON")

        # build the content of each tab
        self._build_students_tab()
        self._build_instructors_tab()
        self._build_courses_tab()
        self._build_relations_tab()
        self._build_records_tab()
        self._build_io_tab()

    def _error(self, msg: str) -> None:
        """
        small helper to pop up an error dialog with a given message. saves me from
        writing the full messagebox call every time.

        :param msg: the text to show inside the error box
        :type msg: str

        :return: nothing; it just shows the dialog
        :rtype: None
        """
        # wrapper so calls are shorter
        messagebox.showerror("Error", msg, parent=self)

    def _info(self, msg: str) -> None:
        """
        quick helper for showing an info dialog, so i don’t repeat the long
        messagebox line each time. mostly for confirmations or status messages.

        :param msg: the text content to display in the info window
        :type msg: str

        :return: nothing; just opens a simple ok dialog
        :rtype: None
        """
        # wrapper so calls are shorter
        messagebox.showinfo("Info", msg, parent=self)

    def _confirm(self, msg: str) -> bool:
        """
        shows a yes/no confirm dialog with the given message. handy so i don’t
        rewrite the full messagebox.askyesno every time.

        :param msg: the question or warning text to show
        :type msg: str

        :return: True if user clicked yes, False otherwise
        :rtype: bool
        """
        # small yes/no helper
        return messagebox.askyesno("Confirm", msg, parent=self)

    def _refresh_all_views(self) -> None:
        """
        refreshes all the main tables/trees (students, instructors, courses, records).
        i call this after inserts/updates/deletes so the ui always shows the latest db state.

        :return: nothing; it just re-populates the treeviews
        :rtype: None
        """
        # reload all tables so the ui stays in sync
        self._refresh_student_tree()
        self._refresh_instructor_tree()
        self._refresh_course_tree()
        self._refresh_records_views()

    # ---------- students tab ----------
    def _build_students_tab(self) -> None:
        """
        builds the whole “students” page: header, a small form to add/edit a student
        (id, name, age, email), action buttons, and the table that lists students with
        their registered courses. layout is simple: form on top, table below.

        :return: nothing; it just creates widgets and wires basic events
        :rtype: None
        :notes: the table binds selection so i can click a row and the form fills up for quick edits.
        """
        f = self.tab_students
        for i in range(4):
            f.columnconfigure(i, weight=1)
        f.rowconfigure(3, weight=1)

        self._add_header(f, "Students")

        # top form for add/edit student
        frm = ttk.LabelFrame(f, text="Add / Edit Student")
        frm.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=10, ipady=5)
        for i in range(8):
            frm.columnconfigure(i, weight=1)

        ttk.Label(frm, text="Student ID").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.ent_sid = ttk.Entry(frm)
        self.ent_sid.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Name").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.ent_sname = ttk.Entry(frm)
        self.ent_sname.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Age").grid(row=0, column=4, padx=6, pady=6, sticky="e")
        self.ent_sage = ttk.Entry(frm)
        self.ent_sage.grid(row=0, column=5, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Email").grid(row=0, column=6, padx=6, pady=6, sticky="e")
        self.ent_semail = ttk.Entry(frm)
        self.ent_semail.grid(row=0, column=7, padx=6, pady=6, sticky="ew")

        # actions
        ttk.Button(frm, text="Add / Update", style='Accent.TButton',
                   command=self._on_add_or_update_student)\
            .grid(row=1, column=0, columnspan=2, padx=6, pady=8, sticky="ew")
        ttk.Button(frm, text="Delete Selected", command=self._on_delete_selected_student)\
            .grid(row=1, column=2, columnspan=2, padx=6, pady=8, sticky="ew")
        ttk.Button(frm, text="Clear Form", command=self._clear_student_form)\
            .grid(row=1, column=4, columnspan=2, padx=6, pady=8, sticky="ew")

        # table with zebra rows
        tree = ttk.Treeview(f, columns=("id", "name", "age", "email", "courses"),
                            show="headings", height=14, style='Treeview')
        for c, w in zip(("id", "name", "age", "email", "courses"), (100, 200, 60, 220, 300)):
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=w, stretch=True)
        tree.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        ysb = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ysb.set)
        ysb.grid(row=3, column=4, sticky="ns", pady=10)
        tree.bind("<<TreeviewSelect>>", self._on_select_student_row)
        self.tree_students = tree

    def _clear_student_form(self) -> None:
        """
        clears the student form fields and drops any table selection, so i start fresh.
        useful after add/update, or if i just want to reset before typing.

        :return: nothing; just mutates entry widgets + selection
        :rtype: None
        """
        # reset fields and deselect rows
        for e in (self.ent_sid, self.ent_sname, self.ent_sage, self.ent_semail):
            e.delete(0, tk.END)
        self.tree_students.selection_remove(self.tree_students.selection())

    def _on_add_or_update_student(self) -> None:
        """
        handles saving a student from the form: i validate fields first, then try to insert;
        if the id already exists i just update instead. finally i refresh the tables and show a
        small info message so it feels responsive.

        :return: nothing; updates the db and refreshes the ui
        :rtype: None
        :raises: none here on purpose; validation errors show as dialogs and the insert→update path is handled
        :notes: validation uses the helpers (id/name/age/email). ids/emails/names are normalized before db ops.
        """
        # validate inputs, try insert, if exists then update, then refresh
        sid = self.ent_sid.get().strip()
        name = self.ent_sname.get().strip()
        age_s = self.ent_sage.get().strip()
        email = self.ent_semail.get().strip()

        if not is_valid_student_id(sid):
            return self._error("Invalid student ID.")
        if not is_valid_person_name(name):
            return self._error("Invalid name.")
        if not is_non_negative_int(age_s):
            return self._error("Age must be a non-negative integer.")
        if not is_valid_email(email):
            return self._error("Invalid email.")

        sid_n = norm_id(sid)
        name_n = norm_name(name)
        age = int(age_s)
        email_n = norm_email(email)
        try:
            self.repo.add_student(sid_n, name_n, age, email_n)
        except Exception:
            self.repo.update_student(sid_n, name_n, age, email_n)
        self._refresh_all_views()
        self._info("Student saved.")

    def _on_delete_selected_student(self) -> None:
        """
        deletes the currently selected student after a quick confirm. if i say yes,
        it removes the student and any course registrations tied to them, then refreshes
        the views so the table matches reality.

        :return: nothing; mutates the db and reloads the tables
        :rtype: None
        :notes: selection is taken from the students tree; if nothing is selected, it just exits quietly.
        """
        # delete selected student, warn that registrations will be removed
        sel = self.tree_students.selection()
        if not sel:
            return
        sid = self.tree_students.item(sel[0], "values")[0]
        if not self._confirm(f"Delete student {sid}? This will also remove registrations."):
            return
        self.repo.delete_student(sid)
        self._refresh_all_views()

    def _on_select_student_row(self, _evt=None) -> None:
        """
        when i click a row in the students table, this copies the values into the form
        so i can edit fast (id, name, age, email). if nothing is selected, it just does nothing.

        :param _evt: optional tk event from the treeview binding (not really used)
        :type _evt: object or None

        :return: nothing; just updates the entry widgets
        :rtype: None
        """
        # move selected row values into the form for quick edits
        sel = self.tree_students.selection()
        if not sel:
            return
        sid, name, age, email, _ = self.tree_students.item(sel[0], "values")
        self.ent_sid.delete(0, tk.END); self.ent_sid.insert(0, sid)
        self.ent_sname.delete(0, tk.END); self.ent_sname.insert(0, name)
        self.ent_sage.delete(0, tk.END); self.ent_sage.insert(0, age)
        self.ent_semail.delete(0, tk.END); self.ent_semail.insert(0, email)

    def _refresh_student_tree(self) -> None:
        """
        reloads the students table from the db and pushes rows into the treeview.
        simple pull → fill flow so the ui always shows current data.

        :return: nothing; just repopulates the students tree
        :rtype: None
        """
        # reload student rows from db
        rows = self._q_students("", False)
        self._fill_tree(self.tree_students, rows, ("student_id", "name", "age", "email", "courses"))

    # ---------- instructors tab ----------
    def _build_instructors_tab(self) -> None:
        """
        builds the whole “instructors” page: header, a small form for id/name/age/email,
        action buttons (add/update, delete, clear), and the table that lists instructors
        plus the courses they own. layout mirrors the students tab so it feels consistent.

        :return: nothing; it just creates widgets and hooks up the selection handler
        :rtype: None
        :notes: clicking a row fills the form for quick edits; columns are sized to stay readable.
        """
        f = self.tab_instructors
        for i in range(4):
            f.columnconfigure(i, weight=1)
        f.rowconfigure(3, weight=1)

        self._add_header(f, "Instructors")

        frm = ttk.LabelFrame(f, text="Add / Edit Instructor")
        frm.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        for i in range(8):
            frm.columnconfigure(i, weight=1)

        ttk.Label(frm, text="Instructor ID").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.ent_iid = ttk.Entry(frm)
        self.ent_iid.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Name").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.ent_iname = ttk.Entry(frm)
        self.ent_iname.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Age").grid(row=0, column=4, padx=6, pady=6, sticky="e")
        self.ent_iage = ttk.Entry(frm)
        self.ent_iage.grid(row=0, column=5, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Email").grid(row=0, column=6, padx=6, pady=6, sticky="e")
        self.ent_iemail = ttk.Entry(frm)
        self.ent_iemail.grid(row=0, column=7, padx=6, pady=6, sticky="ew")

        ttk.Button(frm, text="Add / Update", style='Accent.TButton',
                   command=self._on_add_or_update_instructor)\
            .grid(row=1, column=0, columnspan=2, padx=6, pady=8, sticky="ew")
        ttk.Button(frm, text="Delete Selected",
                   command=self._on_delete_selected_instructor)\
            .grid(row=1, column=2, columnspan=2, padx=6, pady=8, sticky="ew")
        ttk.Button(frm, text="Clear Form",
                   command=self._clear_instructor_form)\
            .grid(row=1, column=4, columnspan=2, padx=6, pady=8, sticky="ew")

        tree = ttk.Treeview(f, columns=("id", "name", "age", "email", "courses"),
                            show="headings", height=14, style='Treeview')
        for c, w in zip(("id", "name", "age", "email", "courses"), (110, 200, 60, 220, 300)):
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=w, stretch=True)
        tree.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        ysb = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ysb.set)
        ysb.grid(row=3, column=4, sticky="ns", pady=10)
        tree.bind("<<TreeviewSelect>>", self._on_select_instructor_row)
        self.tree_instructors = tree

    def _clear_instructor_form(self) -> None:
        """
        clears the instructor form inputs and drops any current selection in the table,
        so i can start clean before adding or editing.

        :return: nothing; just resets entries + selection
        :rtype: None
        """
        # reset fields and clear selection
        for e in (self.ent_iid, self.ent_iname, self.ent_iage, self.ent_iemail):
            e.delete(0, tk.END)
        self.tree_instructors.selection_remove(self.tree_instructors.selection())

    def _on_add_or_update_instructor(self) -> None:
        """
        saves an instructor from the form: validate fields first, try to insert,
        and if the id already exists then i just update it. afterwards i refresh
        the tables and show a small info toast so it feels responsive.

        :return: nothing; mutates the db and refreshes the ui
        :rtype: None
        :raises: none here; validation errors are shown in dialogs and insert→update is handled
        :notes: i normalize id/name/email before writing, and cast age to int after checking it’s non-negative.
        """
        # validate, try insert, else update
        iid = self.ent_iid.get().strip()
        name = self.ent_iname.get().strip()
        age_s = self.ent_iage.get().strip()
        email = self.ent_iemail.get().strip()

        if not is_valid_instructor_id(iid):
            return self._error("Invalid instructor ID.")
        if not is_valid_person_name(name):
            return self._error("Invalid name.")
        if not is_non_negative_int(age_s):
            return self._error("Age must be a non-negative integer.")
        if not is_valid_email(email):
            return self._error("Invalid email.")

        iid_n = norm_id(iid)
        name_n = norm_name(name)
        age = int(age_s)
        email_n = norm_email(email)
        try:
            self.repo.add_instructor(iid_n, name_n, age, email_n)
        except Exception:
            self.repo.update_instructor(iid_n, name_n, age, email_n)
        self._refresh_all_views()
        self._info("Instructor saved.")

    def _on_delete_selected_instructor(self) -> None:
        """
        deletes the selected instructor after a quick confirm. if i accept, the instructor
        is removed and any courses pointing to them become unassigned, then i refresh the ui.

        :return: nothing; updates db and reloads the instructors table
        :rtype: None
        :notes: if no row is selected, it just exits quietly (no dialog).
        """
        # delete and warn that courses will be unassigned
        sel = self.tree_instructors.selection()
        if not sel:
            return
        iid = self.tree_instructors.item(sel[0], "values")[0]
        if not self._confirm(f"Delete instructor {iid}? This will unassign their courses."):
            return
        self.repo.delete_instructor(iid)
        self._refresh_all_views()

    def _on_select_instructor_row(self, _evt=None) -> None:
        """
        when i click an instructor row, this copies the row values into the form
        so editing is quick (id, name, age, email). if nothing is selected, it just returns.

        :param _evt: optional treeview event object from the binding (unused here)
        :type _evt: object or None

        :return: nothing; it just updates the entry widgets
        :rtype: None
        """
        # move selected instructor into form fields
        sel = self.tree_instructors.selection()
        if not sel:
            return
        iid, name, age, email, _ = self.tree_instructors.item(sel[0], "values")
        self.ent_iid.delete(0, tk.END); self.ent_iid.insert(0, iid)
        self.ent_iname.delete(0, tk.END); self.ent_iname.insert(0, name)
        self.ent_iage.delete(0, tk.END); self.ent_iage.insert(0, age)
        self.ent_iemail.delete(0, tk.END); self.ent_iemail.insert(0, email)

    def _refresh_instructor_tree(self) -> None:
        """
        pulls fresh instructor rows from the db and refills the instructors treeview.
        keeps the ui in sync after any add/update/delete.

        :return: nothing; just repopulates the table
        :rtype: None
        """
        # reload instructors from db
        rows = self._q_instructors("", False)
        self._fill_tree(self.tree_instructors, rows, ("instructor_id", "name", "age", "email", "courses"))

    # ---------- courses tab ----------
    def _build_courses_tab(self) -> None:
        """
        builds the “courses” page: header, a form for course id / name / optional instructor id,
        a few action buttons, and the table that lists courses with their instructor (if any)
        and enrolled students. layout mirrors the other tabs on purpose.

        :return: nothing; just creates widgets and wires the selection handler
        :rtype: None
        :notes: selecting a row fills the form so editing is quicker; instructor field can stay empty.
        """
        f = self.tab_courses
        for i in range(4):
            f.columnconfigure(i, weight=1)
        f.rowconfigure(3, weight=1)

        self._add_header(f, "Courses")

        frm = ttk.LabelFrame(f, text="Add / Edit Course")
        frm.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        for i in range(6):
            frm.columnconfigure(i, weight=1)

        ttk.Label(frm, text="Course ID").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.ent_cid = ttk.Entry(frm)
        self.ent_cid.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Course Name").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.ent_cname = ttk.Entry(frm)
        self.ent_cname.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        ttk.Label(frm, text="Instructor ID (optional)").grid(row=0, column=4, padx=6, pady=6, sticky="e")
        self.ent_ci = ttk.Entry(frm)
        self.ent_ci.grid(row=0, column=5, padx=6, pady=6, sticky="ew")

        ttk.Button(frm, text="Add / Update", style='Accent.TButton',
                   command=self._on_add_or_update_course)\
            .grid(row=1, column=0, columnspan=2, padx=6, pady=8, sticky="ew")
        ttk.Button(frm, text="Delete Selected",
                   command=self._on_delete_selected_course)\
            .grid(row=1, column=2, columnspan=2, padx=6, pady=8, sticky="ew")
        ttk.Button(frm, text="Clear Form",
                   command=self._clear_course_form)\
            .grid(row=1, column=4, padx=6, pady=8, sticky="ew")

        tree = ttk.Treeview(f, columns=("id", "name", "instructor", "students"),
                            show="headings", height=14, style='Treeview')
        for c, w in zip(("id", "name", "instructor", "students"), (110, 260, 180, 360)):
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=w, stretch=True)
        tree.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        ysb = ttk.Scrollbar(f, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ysb.set)
        ysb.grid(row=3, column=4, sticky="ns", pady=10)
        tree.bind("<<TreeviewSelect>>", self._on_select_course_row)
        self.tree_courses = tree

    def _clear_course_form(self) -> None:
        """
        clears the course form inputs (id, name, instructor id) and removes any selection
        from the courses table, so i can start clean before adding/editing.

        :return: nothing; just resets entries + selection
        :rtype: None
        """
        # reset the three fields and drop selection
        for e in (self.ent_cid, self.ent_cname, self.ent_ci):
            e.delete(0, tk.END)
        self.tree_courses.selection_remove(self.tree_courses.selection())

    def _on_add_or_update_course(self) -> None:
        """
        saves a course from the form: i validate id/name first, then try to insert;
        if it already exists i update it instead (including optional instructor id).
        after that i refresh the ui and show a small info message.

        :return: nothing; writes to the db and refreshes tables
        :rtype: None
        :raises: none here; validation errors go to dialogs and insert→update is handled inside
        :notes: instructor id can be empty; when present i normalize it (same for course id/name).
        """
        # validate, try insert, else update
        cid = self.ent_cid.get().strip()
        cname = self.ent_cname.get().strip()
        ci = self.ent_ci.get().strip()

        if not is_valid_course_id(cid):
            return self._error("Invalid course ID (e.g., EECE435 or MATH201A).")
        if not is_valid_course_name(cname):
            return self._error("Invalid course name (3-60 chars).")

        cid_n = norm_id(cid)
        cname_n = norm_name(cname)
        i_id = norm_id(ci) if ci else None
        try:
            self.repo.add_course(cid_n, cname_n, i_id)
        except Exception:
            self.repo.update_course(cid_n, cname_n, i_id)
        self._refresh_all_views()
        self._info("Course saved.")

    def _on_delete_selected_course(self) -> None:
        """
        deletes the selected course after a quick confirm. if i say yes, the course goes
        away and any links to students/instructor are removed too. then i refresh the views.

        :return: nothing; updates the db and reloads the courses table
        :rtype: None
        :notes: if no row is selected, it just returns quietly (no popup).
        """
        # delete course and warn that links will be removed
        sel = self.tree_courses.selection()
        if not sel:
            return
        cid = self.tree_courses.item(sel[0], "values")[0]
        if not self._confirm(f"Delete course {cid}? This will unlink students and instructor."):
            return
        self.repo.delete_course(cid)
        self._refresh_all_views()

    def _on_select_course_row(self, _evt=None) -> None:
        """
        when i click a course row, this copies the values into the form
        (id, name, instructor id). if instructor shows as "—", i leave the field empty.

        :param _evt: optional treeview event object from the binding (unused here)
        :type _evt: object or None

        :return: nothing; just updates the three entry widgets
        :rtype: None
        """
        # move selected course into form fields
        sel = self.tree_courses.selection()
        if not sel:
            return
        cid, cname, instr, _ = self.tree_courses.item(sel[0], "values")
        self.ent_cid.delete(0, tk.END); self.ent_cid.insert(0, cid)
        self.ent_cname.delete(0, tk.END); self.ent_cname.insert(0, cname)
        self.ent_ci.delete(0, tk.END); self.ent_ci.insert(0, "" if instr == "—" else instr)

    def _refresh_course_tree(self) -> None:
        """
        pulls fresh course rows from the db and refills the courses treeview
        (id, name, instructor, students). simple reload so the ui stays current.

        :return: nothing; just repopulates the courses table
        :rtype: None
        """
        # reload courses grid
        rows = self._q_courses("", False)
        self._fill_tree(self.tree_courses, rows, ("course_id", "course_name", "instructor", "students"))

    # ---------- register / assign tab ----------
    def _build_relations_tab(self) -> None:
        """
        builds the “register & assign” page. it’s a tiny form with two entries (student id, course id)
        and one button to register the student into the course. kept minimal on purpose.

        :return: nothing; just creates widgets and hooks the register button
        :rtype: None
        :notes: validation/actual linking happens in _on_register_student; this tab is just the ui shell.
        """
        f = self.tab_relations
        for i in range(4):
            f.columnconfigure(i, weight=1)
        self._add_header(f, "Register & Assign")

        # keep it minimal: two entries and one button
        reg = ttk.LabelFrame(f, text="Register Student to Course")
        reg.grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        for i in range(6):
            reg.columnconfigure(i, weight=1)

        ttk.Label(reg, text="Student ID").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.cb_reg_student = ttk.Entry(reg)
        self.cb_reg_student.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        ttk.Label(reg, text="Course ID").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.cb_reg_course = ttk.Entry(reg)
        self.cb_reg_course.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        ttk.Button(reg, text="Register", style='Accent.TButton',
                   command=self._on_register_student).grid(row=0, column=4, padx=6, pady=6, sticky="ew")

    def _on_register_student(self) -> None:
        """
        registers a student into a course using the two entry fields. i check both ids exist in the form,
        normalize them, and ask the repo to link. if repo complains, i just show the message.

        :return: nothing; updates db and refreshes all tables
        :rtype: None
        :raises: none directly here; any repo exception is caught and shown as an error dialog
        :notes: if either id is missing i bail early with a friendly error; success shows a tiny info popup.
        """
        # call repo to link the student to the course; any errors bubble up
        sid = self.cb_reg_student.get().strip()
        cid = self.cb_reg_course.get().strip()
        if not sid or not cid:
            return self._error("Enter both student ID and course ID.")
        try:
            self.repo.register_student(norm_id(sid), norm_id(cid))
            self._info("Student registered.")
        except Exception as e:
            self._error(str(e))
        self._refresh_all_views()

    # ---------- records & search tab ----------
    def _build_records_tab(self) -> None:
        """
        builds the “records & search” page: a tiny search bar + scope dropdown on top,
        and three read-only tables below (students, instructors, courses). pretty much a dashboard.

        :return: nothing; it just creates widgets and wires the buttons
        :rtype: None
        :notes: apply triggers filtered queries; clear resets scope to “All” and empties the search box.
        """
        f = self.tab_records
        for i in range(6):
            f.columnconfigure(i, weight=1)
        f.rowconfigure(2, weight=1)

        self._add_header(f, "Records & Search")

        # simple search row
        ttk.Label(f, text="Search:").grid(row=1, column=0, padx=8, pady=10, sticky="e")
        self.ent_search = ttk.Entry(f)
        self.ent_search.grid(row=1, column=1, padx=8, pady=10, sticky="ew")

        self.cb_scope = ttk.Combobox(f, state="readonly", values=["All", "Students", "Instructors", "Courses"], width=14)
        self.cb_scope.set("All")
        self.cb_scope.grid(row=1, column=2, padx=8, pady=10)

        ttk.Button(f, text="Apply", style='Accent.TButton', command=self._on_apply_search).grid(row=1, column=3, padx=8, pady=10)
        ttk.Button(f, text="Clear", command=self._on_clear_search).grid(row=1, column=4, padx=8, pady=10)

        # three read-only tables side-by-side
        self.rec_students = self._make_tree(f, ("id", "name", "age", "email", "courses"), (110, 200, 60, 220, 260))
        self.rec_instructors = self._make_tree(f, ("id", "name", "age", "email", "courses"), (110, 200, 60, 220, 260))
        self.rec_courses = self._make_tree(f, ("id", "name", "instructor", "students"), (120, 240, 160, 260))

        self.rec_students["frame"].grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        self.rec_instructors["frame"].grid(row=2, column=2, columnspan=2, sticky="nsew", padx=6, pady=6)
        self.rec_courses["frame"].grid(row=2, column=4, columnspan=2, sticky="nsew", padx=6, pady=6)

    def _make_tree(self, parent, cols, widths):
        """
        small helper that builds a treeview inside a frame with a vertical scrollbar.
        i pass the columns and their widths, it returns a tiny dict so i can grid the frame
        and keep a handle on the tree.

        :param parent: the container where this frame (with the tree) will live
        :type parent: tkinter.Widget
        :param cols: column names to create in the tree (shown as headings)
        :type cols: list or tuple
        :param widths: pixel widths for each column (same order as cols)
        :type widths: list or tuple

        :return: a dict with {"frame": the outer frame, "tree": the ttk.Treeview}
        :rtype: dict
        :notes: headings get cased with .capitalize(); rows are added elsewhere via _fill_tree.
        """
        # helper to create a tree with a scrollbar inside a frame
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=14, style='Treeview')
        for c, w in zip(cols, widths):
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=w, stretch=True)
        ysb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=ysb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        return {"frame": frame, "tree": tree}

    def _refresh_records_views(self) -> None:
        """
        reloads the three records/search tables with no filters (students, instructors, courses).
        basically a full reset so the dashboard shows everything again.

        :return: nothing; it just repopulates all three trees
        :rtype: None
        """
        # reload all three search tables without filters
        self._fill_tree(self.rec_students["tree"], self._q_students("", False),
                        ("student_id", "name", "age", "email", "courses"))
        self._fill_tree(self.rec_instructors["tree"], self._q_instructors("", False),
                        ("instructor_id", "name", "age", "email", "courses"))
        self._fill_tree(self.rec_courses["tree"], self._q_courses("", False),
                        ("course_id", "course_name", "instructor", "students"))

    def _on_apply_search(self) -> None:
        """
        applies the search: grabs the text + scope, runs simple like-based queries,
        and fills only the trees that match the chosen scope. others get cleared.

        :return: nothing; just updates the three result tables
        :rtype: None
        :notes: scope can be “All”, “Students”, “Instructors”, or “Courses”. empty query means “show all”.
        """
        # apply scope + keyword filter using simple like queries
        q = self.ent_search.get().strip()
        scope = self.cb_scope.get()

        if scope in ("All", "Students"):
            self._fill_tree(self.rec_students["tree"], self._q_students(q, True),
                            ("student_id", "name", "age", "email", "courses"))
        else:
            self._fill_tree(self.rec_students["tree"], [], ("student_id", "name", "age", "email", "courses"))

        if scope in ("All", "Instructors"):
            self._fill_tree(self.rec_instructors["tree"], self._q_instructors(q, True),
                            ("instructor_id", "name", "age", "email", "courses"))
        else:
            self._fill_tree(self.rec_instructors["tree"], [], ("instructor_id", "name", "age", "email", "courses"))

        if scope in ("All", "Courses"):
            self._fill_tree(self.rec_courses["tree"], self._q_courses(q, True),
                            ("course_id", "course_name", "instructor", "students"))
        else:
            self._fill_tree(self.rec_courses["tree"], [], ("course_id", "course_name", "instructor", "students"))

    def _on_clear_search(self) -> None:
        """
        clears the search box and resets scope to “All”, then reloads the records view.
        basically a quick reset to see everything again.

        :return: nothing; just resets inputs and repopulates tables
        :rtype: None
        """
        # reset search and scope back to defaults
        self.ent_search.delete(0, tk.END)
        self.cb_scope.set("All")
        self._refresh_records_views()

    # ---------- json / csv / backup tab ----------
    def _build_io_tab(self) -> None:
        """
        builds the “save / load json” page (plus backup and csv export). it’s basically
        the utility corner: export/import json using the existing layer, make a sqlite backup,
        and dump students/instructors/courses to csv.

        :return: nothing; just creates buttons/labels/separators and wires handlers
        :rtype: None
        :notes: the db itself isn’t cleared here; “clear all” only resets views/forms. backup writes a copy to a path you choose.
        """
        f = self.tab_io
        for i in range(3):
            f.columnconfigure(i, weight=1)

        self._add_header(f, "Save / Load JSON")

        ttk.Label(f, text="Export/Import using the existing JSON persistence layer.").grid(row=1, column=0, columnspan=3, padx=12, pady=12)

        ttk.Button(f, text="Export JSON…", style='Accent.TButton', command=self._on_save_json)\
            .grid(row=2, column=0, padx=12, pady=12, sticky="ew")
        ttk.Button(f, text="Import JSON…", command=self._on_load_json)\
            .grid(row=2, column=1, padx=12, pady=12, sticky="ew")
        ttk.Button(f, text="Clear All (DB remains)", command=self._on_clear_ui)\
            .grid(row=2, column=2, padx=12, pady=12, sticky="ew")

        ttk.Separator(f, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew", padx=12, pady=(8, 12))

        ttk.Label(f, text="Database Backup").grid(row=4, column=0, columnspan=3, padx=12, pady=(0, 6))
        ttk.Button(f, text="Backup DB…", style='Accent.TButton', command=self._on_backup_db)\
            .grid(row=5, column=0, columnspan=3, padx=12, pady=12, sticky="ew")

        ttk.Separator(f, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", padx=12, pady=(8, 12))

        ttk.Label(f, text="Export to CSV").grid(row=7, column=0, columnspan=3, padx=12, pady=(0, 6))
        ttk.Button(f, text="Export Students CSV…", command=lambda: self._on_export_csv('students'))\
            .grid(row=8, column=0, padx=12, pady=8, sticky="ew")
        ttk.Button(f, text="Export Instructors CSV…", command=lambda: self._on_export_csv('instructors'))\
            .grid(row=8, column=1, padx=12, pady=8, sticky="ew")
        ttk.Button(f, text="Export Courses CSV…", command=lambda: self._on_export_csv('courses'))\
            .grid(row=8, column=2, padx=12, pady=8, sticky="ew")

    def _on_backup_db(self) -> None:
        """
        makes a sqlite backup file with a timestamped name. i open a save dialog,
        then ask the repo to write a copy there. if it works i show the path, if not i show the error.

        :return: nothing; just writes a backup file if you confirm a path
        :rtype: None
        :raises: none directly here; any repo/file issue is caught and shown as an error dialog
        :notes: default filename looks like db-backup-YYYYMMDD-HHMMSS.sqlite so it’s easy to sort.
        """
        # create a timestamped sqlite copy using repo.backup
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        default_name = f"db-backup-{ts}.sqlite"
        path = filedialog.asksaveasfilename(
            title="Backup Database",
            defaultextension=".sqlite",
            initialfile=default_name,
            filetypes=[("SQLite DB", "*.sqlite *.db"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            out_path = self.repo.backup(path)
            self._info(f"Database backup created:\n{out_path}")
        except Exception as e:
            self._error(f"Backup failed:\n{e}")

    def _on_export_csv(self, kind: str) -> None:
        """
        exports the current rows to a csv file. i pick which dataset based on `kind`
        (students/instructors/courses), suggest a timestamped filename, and write headers+rows.

        :param kind: which table to export; accepts 'students', 'instructors', or 'courses'
        :type kind: str

        :return: nothing; writes a csv to the chosen path if you confirm the dialog
        :rtype: None
        :raises: none directly; any file i/o error gets caught and shown as an error dialog
        :notes: values are stringified on write so the csv stays simple and consistent.
        """
        # export current view rows to a csv
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        if kind == 'students':
            rows = self._q_students("", False)
            headers = ["student_id", "name", "age", "email", "courses"]
            default_name = f"students-{ts}.csv"
        elif kind == 'instructors':
            rows = self._q_instructors("", False)
            headers = ["instructor_id", "name", "age", "email", "courses"]
            default_name = f"instructors-{ts}.csv"
        else:
            rows = self._q_courses("", False)
            headers = ["course_id", "course_name", "instructor", "students"]
            default_name = f"courses-{ts}.csv"

        path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for r in rows:
                    writer.writerow({h: str(r.get(h, "")) for h in headers})
            self._info(f"Exported {len(rows)} {kind} record(s) to:\n{path}")
        except Exception as e:
            self._error(f"CSV export failed:\n{e}")

    def _on_save_json(self) -> None:
        """
        builds python objects from the current db rows (students, instructors, courses),
        reconnects relationships (instructor on course + enrolled students), then dumps everything
        to a single json file using the existing persistence helpers.

        :return: nothing; just writes a json file if you pick a path
        :rtype: None
        :raises: none here; any file/db hiccup is handled and shown via a dialog
        :notes: i query courses twice on purpose: first to create them, then to attach instructor;
                registrations come from the REGISTRATION table and get mapped to course objects.
        """
        # rebuild domain objects from db rows then dump to json (keeps relationships)
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                            filetypes=[("JSON", "*.json"), ("All Files", "*.*")])
        if not path:
            return

        students = []
        for r in self._q_students("", False):
            students.append(Student(r["name"], int(r["age"]), r["email"], r["student_id"]))

        instructors = []
        for r in self._q_instructors("", False):
            instructors.append(Instructor(r["name"], int(r["age"]), r["email"], r["instructor_id"]))

        courses_map: Dict[str, Course] = {}
        for r in self._q_courses("", False):
            co = Course(r["course_id"], r["course_name"])
            courses_map[r["course_id"]] = co

        for r in self._q_courses("", False):
            cid = r["course_id"]
            iid = r.get("instructor")
            if iid and iid != "—":
                iobj = next((i for i in instructors if i.instructor_id == iid), None)
                if iobj:
                    courses_map[cid].set_instructor(iobj)

        regs = self.repo.search("REGISTRATION")
        stu_map = {s.student_id: s for s in students}
        for rg in regs:
            s = stu_map.get(rg["s_id"])
            c = courses_map.get(rg["c_id"])
            if s and c:
                c.add_student(s)

        save_to_json(path, students, instructors, list(courses_map.values()))
        self._info("Exported successfully.")

    def _on_load_json(self) -> None:
        """
        loads a json snapshot (from our own exporter) and upserts everything into the db:
        students, instructors, courses, and their relationships. duplicates are fine, i either
        skip or update so it doesn’t crash on existing data.

        :return: nothing; writes into the db and refreshes the ui
        :rtype: None
        :raises: none here; i catch insert errors and move on (very lab-friendly)
        :notes: instructor can be missing on a course; registrations are re-linked by calling repo.register_student.
        """
        # import a json snapshot and upsert into db (safe if duplicates)
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All Files", "*.*")])
        if not path:
            return

        s, i, c = load_from_json(path)

        for st in s.values():
            try:
                self.repo.add_student(st.student_id, st.name, st.age, st.email)
            except:
                pass
        for ins in i.values():
            try:
                self.repo.add_instructor(ins.instructor_id, ins.name, ins.age, ins.email)
            except:
                pass

        for co in c.values():
            iid = co.instructor.instructor_id if getattr(co, "instructor", None) else None
            try:
                self.repo.add_course(co.course_id, co.course_name, iid)
            except:
                self.repo.update_course(co.course_id, co.course_name, iid)
            for s_obj in co.enrolled_students:
                try:
                    self.repo.register_student(s_obj.student_id, co.course_id)
                except:
                    pass

        self._refresh_all_views()
        self._info("Imported successfully.")

    def _on_clear_ui(self) -> None:
        """
        clears the ui state (tables/forms) after a quick confirm. the database stays as-is,
        this is just a visual reset so i can start clean.

        :return: nothing; just refreshes all views
        :rtype: None
        """
        # just refresh views/forms; the db remains intact
        if not self._confirm("Clear table views and forms? (Does not delete from DB)"):
            return
        self._refresh_all_views()

    # ---------- queries ----------
    def _q_students(self, q: str, limit_scope: bool) -> List[Dict]:
        """
        runs the students query and returns rows as dicts. if i pass a text `q`,
        i do a simple like filter over id/name/email or registered course id. keeping sql readable.

        :param q: search text to filter by; empty string means no filtering
        :type q: str
        :param limit_scope: kept for future tweaks (not used now, i just keep the signature stable)
        :type limit_scope: bool

        :return: list of student dicts with keys: student_id, name, age, email, courses (comma-separated)
        :rtype: list[dict]
        :notes: i coalesce nulls and also pretty-print the courses with ", " instead of raw commas.
        """
        # raw sql kept readable; limit_scope kept for possible future use
        where = ""
        params: List[str] = []
        if q:
            like = f"%{q.lower()}%"
            where = """
            WHERE
              lower(s.student_id) LIKE ? OR
              lower(s.name)      LIKE ? OR
              lower(s.email)     LIKE ? OR
              lower(r.c_id)      LIKE ?
            """
            params = [like, like, like, like]
        sql = f"""
        SELECT
          s.student_id,
          s.name,
          s.age,
          s.email,
          COALESCE(GROUP_CONCAT(DISTINCT r.c_id), '') AS courses
        FROM STUDENTS s
        LEFT JOIN REGISTRATION r ON r.s_id = s.student_id
        {where}
        GROUP BY s.student_id, s.name, s.age, s.email
        ORDER BY s.student_id
        """
        cur = self.repo.conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        out = [dict(zip(cols, row)) for row in cur.fetchall()]
        for r in out:
            r["courses"] = r["courses"].replace(",", ", ")
        return out

    def _q_instructors(self, q: str, limit_scope: bool) -> List[Dict]:
        """
        fetches instructors with a simple join to list the courses they own. if `q` is given,
        i filter by id/name/email or course id using like (lowercased).

        :param q: search text to narrow results; empty means show all
        :type q: str
        :param limit_scope: placeholder for future behavior; not used now
        :type limit_scope: bool

        :return: list of dicts with instructor_id, name, age, email, courses (comma-separated)
        :rtype: list[dict]
        :notes: i coalesce nulls and pretty-print the courses with a space after commas.
        """
        # list instructors and the courses they own
        where = ""
        params: List[str] = []
        if q:
            like = f"%{q.lower()}%"
            where = """
            WHERE
              lower(i.instructor_id) LIKE ? OR
              lower(i.name)          LIKE ? OR
              lower(i.email)         LIKE ? OR
              lower(c.course_id)     LIKE ?
            """
            params = [like, like, like, like]
        sql = f"""
        SELECT
          i.instructor_id,
          i.name,
          i.age,
          i.email,
          COALESCE(GROUP_CONCAT(DISTINCT c.course_id), '') AS courses
        FROM INSTRUCTORS i
        LEFT JOIN COURSES c ON c.i_id = i.instructor_id
        {where}
        GROUP BY i.instructor_id, i.name, i.age, i.email
        ORDER BY i.instructor_id
        """
        cur = self.repo.conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        out = [dict(zip(cols, row)) for row in cur.fetchall()]
        for r in out:
            r["courses"] = r["courses"].replace(",", ", ")
        return out

    def _q_courses(self, q: str, limit_scope: bool) -> List[Dict]:
        """
        gets courses with their optional instructor and enrolled students. if i pass `q`,
        i filter by course id/name, instructor id, or student id using lower+like.

        :param q: search text to narrow results; empty means no filter
        :type q: str
        :param limit_scope: kept for future tweaks (not used now)
        :type limit_scope: bool

        :return: list of dicts: course_id, course_name, instructor (or '—'), students (comma-separated)
        :rtype: list[dict]
        :notes: i coalesce nulls and space out the comma list for readability.
        """
        # list courses with optional instructor and enrolled students
        where = ""
        params: List[str] = []
        if q:
            like = f"%{q.lower()}%"
            where = """
            WHERE
              lower(c.course_id)     LIKE ? OR
              lower(c.course_name)   LIKE ? OR
              lower(i.instructor_id) LIKE ? OR
              lower(r.s_id)          LIKE ?
            """
            params = [like, like, like, like]
        sql = f"""
        SELECT
          c.course_id,
          c.course_name,
          COALESCE(i.instructor_id, '—') AS instructor,
          COALESCE(GROUP_CONCAT(DISTINCT r.s_id), '') AS students
        FROM COURSES c
        LEFT JOIN INSTRUCTORS i ON i.instructor_id = c.i_id
        LEFT JOIN REGISTRATION r ON r.c_id = c.course_id
        {where}
        GROUP BY c.course_id, c.course_name, i.instructor_id
        ORDER BY c.course_id
        """
        cur = self.repo.conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        out = [dict(zip(cols, row)) for row in cur.fetchall()]
        for r in out:
            r["students"] = r["students"].replace(",", ", ")
        return out

    def _fill_tree(self, tree: ttk.Treeview, rows: Iterable[dict], order: Iterable[str]) -> None:
        """
        clears a treeview and refills it from a list of row dicts, using the given key order.
        i also tag rows as odd/even for a light zebra effect.

        :param tree: the treeview to write into
        :type tree: ttk.Treeview
        :param rows: iterable of dicts holding the data
        :type rows: Iterable[dict]
        :param order: keys to pull from each row (and in this column order)
        :type order: Iterable[str]

        :return: nothing; it just repopulates the widget
        :rtype: None
        :notes: values get cast to str before insert, so the table stays consistent.
        """
        # reusable helper to clear and refill a tree with zebra tags
        for i in tree.get_children():
            tree.delete(i)
        tree.tag_configure('odd', background=STRIPE)
        tree.tag_configure('even', background=SURFACE)
        for idx, r in enumerate(rows):
            vals = tuple(str(r.get(k, "")) for k in order)
            tag = 'odd' if idx % 2 else 'even'
            tree.insert("", tk.END, values=vals, tags=(tag,))


if __name__ == "__main__":
    # run the app; no cli args expected
    App().mainloop()
