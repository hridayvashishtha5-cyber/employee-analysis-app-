"""
Employee Task & Performance Analytics Application
A beginner-friendly desktop app built with Tkinter, Turtle, Pandas, NumPy, and Matplotlib.

Run:
    pip install -r requirements.txt
    python main.py

Records are saved locally to employee_data.csv in the same folder.
"""
from __future__ import annotations

import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import turtle

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "employee_data.csv")
COLUMNS = ["Name", "Department", "Tasks Completed", "Performance Score", "Date Added"]

BG = "#101827"
PANEL = "#182337"
PANEL_2 = "#202f47"
ACCENT = "#65d6ad"
ACCENT_2 = "#7aa8ff"
TEXT = "#f3f6fc"
MUTED = "#a8b5c9"
DANGER = "#ff7f86"


def create_csv_if_needed():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(DATA_FILE, index=False)


def load_data() -> pd.DataFrame:
    create_csv_if_needed()
    try:
        df = pd.read_csv(DATA_FILE)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[COLUMNS]
    if not df.empty:
        df["Tasks Completed"] = pd.to_numeric(df["Tasks Completed"], errors="coerce").fillna(0).astype(int)
        df["Performance Score"] = pd.to_numeric(df["Performance Score"], errors="coerce").fillna(0).astype(float)
        df["Name"] = df["Name"].fillna("").astype(str)
        df["Department"] = df["Department"].fillna("").astype(str)
    return df


def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)


class EmployeeAnalyticsApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Employee Performance Analytics")
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)
        self.root.configure(bg=BG)
        self.df = load_data()
        self.selected_index = None
        self._style()
        self._build_header()
        self._build_layout()
        self.refresh_all()

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=TEXT, fieldbackground=PANEL,
                        rowheight=29, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=PANEL_2, foreground=TEXT,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#31527a")], foreground=[("selected", "white")])
        style.configure("TCombobox", fieldbackground=PANEL_2, background=PANEL_2, foreground=TEXT)
        style.configure("TScrollbar", background=PANEL_2, troughcolor=PANEL)

    def _label(self, parent, text, size=10, color=TEXT, bold=False):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"))

    def _build_header(self):
        header = tk.Frame(self.root, bg=BG, padx=24, pady=18)
        header.pack(fill="x")
        left = tk.Frame(header, bg=BG)
        left.pack(side="left", fill="x", expand=True)
        tk.Label(left, text="EMPLOYEE ANALYTICS", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left, text="Task & Performance Dashboard", bg=BG, fg=TEXT,
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", pady=(2, 0))
        tk.Label(left, text="Track team output, review performance, and turn records into insights.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(3, 0))
        tk.Button(header, text="＋  Add employee", command=self.clear_form, bg=ACCENT, fg="#0d1c23",
                  activebackground="#8ce8c6", relief="flat", font=("Segoe UI", 10, "bold"),
                  padx=16, pady=10, cursor="hand2").pack(side="right", anchor="center")

    def _build_layout(self):
        body = tk.Frame(self.root, bg=BG, padx=20, pady=20)
        body.pack(fill="both", expand=True)
        self.left_col = tk.Frame(body, bg=BG, width=330)
        self.left_col.pack(side="left", fill="y", padx=(0, 16))
        self.left_col.pack_propagate(False)
        self.right_col = tk.Frame(body, bg=BG)
        self.right_col.pack(side="left", fill="both", expand=True)

        self._build_form()
        self._build_stats()
        self._build_records()
        self._build_chart_panel()

    def _build_form(self):
        panel = tk.Frame(self.left_col, bg=PANEL, padx=18, pady=18)
        panel.pack(fill="x")
        self._label(panel, "EMPLOYEE RECORD", 10, ACCENT, True).pack(anchor="w")
        self._label(panel, "Add or update details", 15, TEXT, True).pack(anchor="w", pady=(3, 14))

        self.name_var = tk.StringVar()
        self.dept_var = tk.StringVar(value="Engineering")
        self.tasks_var = tk.StringVar()
        self.score_var = tk.StringVar()
        fields = [
            ("Employee name", self.name_var, "e.g. Aanya Sharma"),
            ("Tasks completed", self.tasks_var, "e.g. 12"),
            ("Performance score (1–10)", self.score_var, "e.g. 8.5"),
        ]
        for label, var, placeholder in fields:
            self._label(panel, label, 9, MUTED, True).pack(anchor="w", pady=(7, 5))
            entry = tk.Entry(panel, textvariable=var, bg=PANEL_2, fg=TEXT, insertbackground=TEXT,
                             relief="flat", font=("Segoe UI", 10), highlightthickness=1,
                             highlightbackground=PANEL_2, highlightcolor=ACCENT)
            entry.pack(fill="x", ipady=9)
            entry.insert(0, "")
            entry.bind("<FocusIn>", lambda e, ent=entry: ent.configure(highlightbackground=ACCENT))
            entry.bind("<FocusOut>", lambda e, ent=entry: ent.configure(highlightbackground=PANEL_2))
            if label == "Employee name":
                self.name_entry = entry

        self._label(panel, "Department", 9, MUTED, True).pack(anchor="w", pady=(12, 5))
        self.dept_combo = ttk.Combobox(panel, textvariable=self.dept_var, state="normal",
                                       values=["Engineering", "Data Science", "Marketing", "Sales",
                                               "Human Resources", "Finance", "Operations", "Design"])
        self.dept_combo.pack(fill="x", ipady=5)

        buttons = tk.Frame(panel, bg=PANEL)
        buttons.pack(fill="x", pady=(16, 0))
        tk.Button(buttons, text="Save record", command=self.save_record, bg=ACCENT, fg="#0d1c23",
                  activebackground="#8ce8c6", relief="flat", font=("Segoe UI", 10, "bold"),
                  padx=10, pady=9, cursor="hand2").pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Button(buttons, text="Clear", command=self.clear_form, bg=PANEL_2, fg=TEXT,
                  activebackground="#30415d", relief="flat", font=("Segoe UI", 10),
                  padx=10, pady=9, cursor="hand2").pack(side="left", fill="x", expand=True, padx=(5, 0))

        tk.Frame(self.left_col, bg=BG, height=14).pack()
        tools = tk.Frame(self.left_col, bg=PANEL, padx=18, pady=16)
        tools.pack(fill="x")
        self._label(tools, "DATA TOOLS", 10, ACCENT, True).pack(anchor="w", pady=(0, 10))
        tk.Button(tools, text="Export CSV as…", command=self.export_csv, bg=PANEL_2, fg=TEXT,
                  activebackground="#30415d", relief="flat", font=("Segoe UI", 10),
                  padx=10, pady=9, cursor="hand2").pack(fill="x")
        tk.Button(tools, text="Delete selected record", command=self.delete_record, bg="#422b3a", fg="#ffbdc2",
                  activebackground="#593347", relief="flat", font=("Segoe UI", 10),
                  padx=10, pady=9, cursor="hand2").pack(fill="x", pady=(8, 0))
        self._label(tools, "Data is stored locally in employee_data.csv.", 8, MUTED).pack(anchor="w", pady=(12, 0))

    def _build_stats(self):
        row = tk.Frame(self.right_col, bg=BG)
        row.pack(fill="x", pady=(0, 14))
        self.stat_values = {}
        cards = [("EMPLOYEES", "employees"), ("TASKS COMPLETED", "tasks"),
                 ("AVERAGE SCORE", "average"), ("TOP SCORE", "top")]
        for title, key in cards:
            card = tk.Frame(row, bg=PANEL, padx=14, pady=13)
            card.pack(side="left", fill="both", expand=True, padx=(0, 9))
            self._label(card, title, 8, MUTED, True).pack(anchor="w")
            value = tk.Label(card, text="0", bg=PANEL, fg=TEXT, font=("Segoe UI", 20, "bold"))
            value.pack(anchor="w", pady=(5, 0))
            self.stat_values[key] = value

    def _build_records(self):
        panel = tk.Frame(self.right_col, bg=PANEL, padx=14, pady=14)
        panel.pack(fill="both", expand=True, pady=(0, 14))
        top = tk.Frame(panel, bg=PANEL)
        top.pack(fill="x", pady=(0, 10))
        self._label(top, "Employee records", 13, TEXT, True).pack(side="left")
        self.search_var = tk.StringVar()
        search = tk.Entry(top, textvariable=self.search_var, bg=PANEL_2, fg=TEXT, insertbackground=TEXT,
                          relief="flat", font=("Segoe UI", 9), width=24)
        search.pack(side="right", ipady=7)
        search.insert(0, "")
        search.bind("<KeyRelease>", lambda e: self.refresh_table())
        tk.Label(top, text="Search", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(side="right", padx=(0, 8))

        table_frame = tk.Frame(panel, bg=PANEL)
        table_frame.pack(fill="both", expand=True)
        cols = ("Name", "Department", "Tasks Completed", "Performance Score")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        widths = [160, 145, 125, 135]
        for col, width in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="w" if col in ("Name", "Department") else "center")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _build_chart_panel(self):
        panel = tk.Frame(self.right_col, bg=PANEL, padx=14, pady=12)
        panel.pack(fill="both", expand=True)
        top = tk.Frame(panel, bg=PANEL)
        top.pack(fill="x", pady=(0, 5))
        self._label(top, "Performance insights", 13, TEXT, True).pack(side="left")
        self.chart_var = tk.StringVar(value="Department averages")
        combo = ttk.Combobox(top, textvariable=self.chart_var, state="readonly",
                             values=["Department averages", "Tasks by employee", "Scores by employee"], width=23)
        combo.pack(side="right")
        combo.bind("<<ComboboxSelected>>", lambda e: self.draw_chart())
        self.chart_holder = tk.Frame(panel, bg=PANEL)
        self.chart_holder.pack(fill="both", expand=True)
        self.figure = Figure(figsize=(7, 2.4), dpi=90, facecolor=PANEL)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_holder)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_form(self):
        self.selected_index = None
        self.name_var.set("")
        self.dept_var.set("Engineering")
        self.tasks_var.set("")
        self.score_var.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def save_record(self):
        name = self.name_var.get().strip()
        dept = self.dept_var.get().strip()
        try:
            tasks = int(self.tasks_var.get())
            score = float(self.score_var.get())
        except ValueError:
            messagebox.showerror("Check your inputs", "Tasks must be a whole number and score must be numeric.")
            return
        if not name or not dept:
            messagebox.showerror("Missing information", "Please enter an employee name and department.")
            return
        if tasks < 0:
            messagebox.showerror("Invalid tasks", "Tasks completed cannot be negative.")
            return
        if not 1 <= score <= 10:
            messagebox.showerror("Invalid score", "Performance score must be between 1 and 10.")
            return
        record = {"Name": name, "Department": dept, "Tasks Completed": tasks,
                  "Performance Score": score, "Date Added": datetime.now().strftime("%Y-%m-%d %H:%M")}
        if self.selected_index is not None and self.selected_index < len(self.df):
            self.df.loc[self.selected_index, COLUMNS] = [record[c] for c in COLUMNS]
        else:
            self.df = pd.concat([self.df, pd.DataFrame([record])], ignore_index=True)
        save_data(self.df)
        self.clear_form()
        self.refresh_all()
        messagebox.showinfo("Saved", f"Record for {name} saved successfully.")

    def on_select(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            return
        idx = int(selection[0])
        if idx >= len(self.df):
            return
        self.selected_index = idx
        record = self.df.iloc[idx]
        self.name_var.set(str(record["Name"]))
        self.dept_var.set(str(record["Department"]))
        self.tasks_var.set(str(int(record["Tasks Completed"])))
        self.score_var.set(str(float(record["Performance Score"])))

    def delete_record(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select a record", "Choose an employee record in the table first.")
            return
        idx = int(selection[0])
        name = self.df.iloc[idx]["Name"]
        if messagebox.askyesno("Confirm deletion", f"Delete the record for {name}?"):
            self.df = self.df.drop(self.df.index[idx]).reset_index(drop=True)
            save_data(self.df)
            self.clear_form()
            self.refresh_all()

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")], initialfile="employee_performance_export.csv")
        if path:
            self.df.to_csv(path, index=False)
            messagebox.showinfo("Export complete", f"Exported {len(self.df)} records.")

    def refresh_table(self):
        query = self.search_var.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, row in self.df.iterrows():
            if query and query not in str(row["Name"]).lower() and query not in str(row["Department"]).lower():
                continue
            score = float(row["Performance Score"])
            self.tree.insert("", "end", iid=str(idx), values=(
                row["Name"], row["Department"], int(row["Tasks Completed"]), f"{score:.1f}/10"))

    def refresh_stats(self):
        df = self.df
        self.stat_values["employees"].configure(text=str(len(df)))
        self.stat_values["tasks"].configure(text=f"{int(df['Tasks Completed'].sum()) if len(df) else 0:,}")
        self.stat_values["average"].configure(text=f"{df['Performance Score'].mean():.1f}/10" if len(df) else "—")
        self.stat_values["top"].configure(text=f"{df['Performance Score'].max():.1f}/10" if len(df) else "—")

    def draw_chart(self):
        self.ax.clear()
        self.figure.patch.set_facecolor(PANEL)
        self.ax.set_facecolor(PANEL)
        self.ax.tick_params(colors=MUTED, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color("#34445d")
        mode = self.chart_var.get()
        df = self.df
        if df.empty:
            self.ax.text(0.5, 0.5, "Add employee records to see analytics",
                         color=MUTED, ha="center", va="center", transform=self.ax.transAxes, fontsize=11)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        elif mode == "Department averages":
            grouped = df.groupby("Department")["Performance Score"].mean().sort_values(ascending=False)
            self.ax.bar(grouped.index, grouped.values, color="#65d6ad", width=0.62)
            self.ax.set_ylabel("Average score / 10", color=MUTED, fontsize=8)
            self.ax.set_ylim(0, 10)
            self.ax.tick_params(axis="x", rotation=18)
        elif mode == "Tasks by employee":
            view = df.sort_values("Tasks Completed", ascending=False).head(10)
            self.ax.bar(view["Name"], view["Tasks Completed"], color="#7aa8ff", width=0.62)
            self.ax.set_ylabel("Tasks completed", color=MUTED, fontsize=8)
            self.ax.tick_params(axis="x", rotation=25)
        else:
            view = df.sort_values("Performance Score", ascending=False).head(10)
            self.ax.bar(view["Name"], view["Performance Score"], color="#f6c66a", width=0.62)
            self.ax.set_ylabel("Performance score / 10", color=MUTED, fontsize=8)
            self.ax.set_ylim(0, 10)
            self.ax.tick_params(axis="x", rotation=25)
        self.ax.grid(axis="y", alpha=0.15, color="#9aa9c0")
        self.ax.set_axisbelow(True)
        self.figure.tight_layout(pad=1.6)
        self.canvas.draw_idle()

    def refresh_all(self):
        self.refresh_table()
        self.refresh_stats()
        self.draw_chart()


def show_splash():
    """A short Turtle logo animation, with safe fallback if the graphics window is unavailable."""
    try:
        screen = turtle.Screen()
        screen.title("Employee Analytics — Welcome")
        screen.bgcolor("#101827")
        screen.setup(width=520, height=340)
        screen.tracer(0)
        pen = turtle.Turtle(visible=False)
        pen.speed(0)
        pen.pensize(5)
        pen.color("#65d6ad")
        pen.penup()
        pen.goto(0, -55)
        pen.pendown()
        for _ in range(36):
            pen.circle(55, 10)
            pen.left(10)
        pen.penup()
        pen.goto(0, 18)
        pen.color("#f3f6fc")
        pen.write("EMPLOYEE ANALYTICS", align="center", font=("Arial", 17, "bold"))
        pen.goto(0, -5)
        pen.color("#a8b5c9")
        pen.write("Task & Performance Dashboard", align="center", font=("Arial", 10, "normal"))
        screen.update()
        screen.ontimer(screen.bye, 1200)
        screen.mainloop()
    except Exception:
        # Turtle may be unavailable in headless or restricted environments.
        pass


def main():
    create_csv_if_needed()
    # The Turtle intro is intentionally optional: close it or wait briefly to continue.
    show_splash()
    root = tk.Tk()
    EmployeeAnalyticsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
