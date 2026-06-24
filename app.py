from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, TypeVar

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from api_service import ApiError, download_todos
from book_service import BookError, analyse_book
from config import APP_TITLE, DB_PATH, OUTPUT_DIR, REPORT_AUTHOR
from database import Database
from models import BookAnalysis
from report_service import ReportError, create_word_report

T = TypeVar("T")


class MainApplication(tk.Tk):
    THEMES = {
        "Clair": {"background": "#f5f7fb", "foreground": "#1f2937", "accent": "#2563eb"},
        "Sombre": {"background": "#1f2937", "foreground": "#f9fafb", "accent": "#60a5fa"},
    }

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1200x800")
        self.minsize(980, 680)

        self.database = Database(DB_PATH)
        self.analysis: BookAnalysis | None = None
        self.result_queue: queue.Queue[tuple[Callable[[object], None], object, Exception | None]] = queue.Queue()
        self.theme_name = tk.StringVar(value="Clair")
        self.font_size = tk.IntVar(value=10)
        self.status = tk.StringVar(value="Application prête.")

        self._build_style()
        self._build_menu()
        self._build_layout()
        self._apply_theme()
        self._refresh_table()
        self.after(100, self._poll_results)

    def _build_style(self) -> None:
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

    def _build_menu(self) -> None:
        menu = tk.Menu(self)

        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Télécharger les données JSON", command=self.download_json_data)
        file_menu.add_command(label="Vider la base de données", command=self.clear_database)
        file_menu.add_separator()
        file_menu.add_command(label="Analyser le livre", command=self.analyse_book_async)
        file_menu.add_command(label="Exporter le rapport Word", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.destroy)
        menu.add_cascade(label="Fichier", menu=file_menu)

        options_menu = tk.Menu(menu, tearoff=False)
        theme_menu = tk.Menu(options_menu, tearoff=False)
        for theme in self.THEMES:
            theme_menu.add_radiobutton(
                label=theme,
                variable=self.theme_name,
                value=theme,
                command=self._apply_theme,
            )
        options_menu.add_cascade(label="Couleurs", menu=theme_menu)

        font_menu = tk.Menu(options_menu, tearoff=False)
        for size in (9, 10, 11, 12, 14):
            font_menu.add_radiobutton(
                label=f"{size} pt",
                variable=self.font_size,
                value=size,
                command=self._apply_theme,
            )
        options_menu.add_cascade(label="Taille de police", menu=font_menu)
        menu.add_cascade(label="Options", menu=options_menu)

        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(
            label="À propos",
            command=lambda: messagebox.showinfo(
                "À propos",
                "Projet Python Avancé\nTkinter, SQLite, JSON, Matplotlib, Pillow et python-docx.",
            ),
        )
        menu.add_cascade(label="Aide", menu=help_menu)
        self.config(menu=menu)

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        title = ttk.Label(root, text=APP_TITLE, style="Title.TLabel")
        title.pack(anchor="w", pady=(0, 10))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.data_tab = ttk.Frame(self.notebook, padding=10)
        self.chart_tab = ttk.Frame(self.notebook, padding=10)
        self.book_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.data_tab, text="Données JSON / SQLite")
        self.notebook.add(self.chart_tab, text="Graphique JSON")
        self.notebook.add(self.book_tab, text="Livre et rapport Word")

        self._build_data_tab()
        self._build_chart_tab()
        self._build_book_tab()

        status_bar = ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w", padding=6)
        status_bar.pack(fill="x", pady=(10, 0))

    def _build_data_tab(self) -> None:
        controls = ttk.Frame(self.data_tab)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Button(controls, text="Télécharger JSON", command=self.download_json_data).pack(side="left", padx=(0, 6))
        ttk.Button(controls, text="Agrégation SQL", command=self.show_aggregate).pack(side="left", padx=6)
        ttk.Button(controls, text="Actualiser", command=self._refresh_table).pack(side="left", padx=6)
        ttk.Button(controls, text="Vider la base", command=self.clear_database).pack(side="left", padx=6)

        source_note = ttk.Label(
            self.data_tab,
            text=(
                "Source : JSONPlaceholder. Les identifiants, utilisateurs et états viennent de l’API ; "
                "les intitulés sont adaptés en français par l’application."
            ),
        )
        source_note.pack(fill="x", pady=(0, 6))

        self.aggregate_label = ttk.Label(self.data_tab, text="Aucune agrégation calculée.", style="Info.TLabel")
        self.aggregate_label.pack(fill="x", pady=(0, 8))

        columns = ("remote_id", "user_id", "name", "state", "length", "downloaded_at")
        self.tree = ttk.Treeview(self.data_tab, columns=columns, show="headings")
        headings = {
            "remote_id": "ID",
            "user_id": "Utilisateur n°",
            "name": "Nom",
            "state": "État",
            "length": "Longueur",
            "downloaded_at": "Téléchargé le",
        }
        widths = {"remote_id": 60, "user_id": 85, "name": 520, "state": 100, "length": 90, "downloaded_at": 150}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center" if column != "name" else "w")

        scrollbar = ttk.Scrollbar(self.data_tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _build_chart_tab(self) -> None:
        controls = ttk.Frame(self.chart_tab)
        controls.pack(fill="x", pady=(0, 8))
        ttk.Button(controls, text="Afficher le graphique", command=self.draw_json_chart).pack(side="left")

        self.json_figure = Figure(figsize=(8, 5), dpi=100)
        self.json_axis = self.json_figure.add_subplot(111)
        self.json_canvas = FigureCanvasTkAgg(self.json_figure, master=self.chart_tab)
        self.json_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _build_book_tab(self) -> None:
        controls = ttk.Frame(self.book_tab)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Button(controls, text="Télécharger et analyser le livre", command=self.analyse_book_async).pack(side="left", padx=(0, 6))
        ttk.Button(controls, text="Exporter le rapport Word", command=self.export_report).pack(side="left", padx=6)

        self.book_summary = tk.Text(self.book_tab, height=7, wrap="word")
        self.book_summary.pack(fill="x", pady=(0, 10))
        self.book_summary.insert("1.0", "Aucune analyse réalisée.")
        self.book_summary.configure(state="disabled")

        self.book_figure = Figure(figsize=(8, 4.5), dpi=100)
        self.book_axis = self.book_figure.add_subplot(111)
        self.book_canvas = FigureCanvasTkAgg(self.book_figure, master=self.book_tab)
        self.book_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _apply_theme(self) -> None:
        palette = self.THEMES[self.theme_name.get()]
        size = self.font_size.get()
        self.configure(background=palette["background"])
        self.style.configure(".", font=("Segoe UI", size))
        self.style.configure("TFrame", background=palette["background"])
        self.style.configure("TLabel", background=palette["background"], foreground=palette["foreground"])
        self.style.configure("Title.TLabel", font=("Segoe UI", size + 8, "bold"))
        self.style.configure("Info.TLabel", font=("Segoe UI", size, "italic"))
        self.style.configure("TButton", padding=7)
        self.style.configure("Treeview", rowheight=max(24, size + 15))
        self.style.map("TButton", background=[("active", palette["accent"])])

    def _run_async(self, task: Callable[[], T], callback: Callable[[T], None]) -> None:
        self.status.set("Opération en cours...")

        def worker() -> None:
            try:
                result = task()
                self.result_queue.put((callback, result, None))
            except Exception as exc:
                self.result_queue.put((callback, None, exc))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_results(self) -> None:
        try:
            while True:
                callback, result, error = self.result_queue.get_nowait()
                if error:
                    self.status.set("Échec de la dernière opération.")
                    messagebox.showerror("Erreur", str(error))
                else:
                    callback(result)
        except queue.Empty:
            pass
        self.after(100, self._poll_results)

    def download_json_data(self) -> None:
        if not self.database.is_empty():
            choice = messagebox.askyesnocancel(
                "Base non vide",
                "La base contient déjà des données.\n\nOui : remplacer les données\nNon : ajouter uniquement les nouveaux éléments\nAnnuler : ne rien faire",
            )
            if choice is None:
                return
            mode = "replace" if choice else "append"
        else:
            mode = "replace"

        def task() -> tuple[str, int]:
            records = download_todos()
            count = self.database.replace_all(records) if mode == "replace" else self.database.append_new(records)
            return mode, count

        self._run_async(task, self._after_json_download)

    def _after_json_download(self, result: tuple[str, int]) -> None:
        mode, count = result
        self._refresh_table()
        self.show_aggregate()
        self.draw_json_chart()
        action = "remplacées" if mode == "replace" else "ajoutées"
        self.status.set(f"{count} données en français {action} dans SQLite.")
        messagebox.showinfo("Succès", f"{count} lignes en français ont été {action}.")

    def _refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.database.fetch_all():
            self.tree.insert("", "end", values=tuple(row))
        self.status.set("Tableau actualisé.")

    def clear_database(self) -> None:
        if not messagebox.askyesno("Confirmation", "Supprimer toutes les données SQLite ?"):
            return
        self.database.clear()
        self._refresh_table()
        self.aggregate_label.configure(text="Base de données vide.")
        self.draw_json_chart()
        self.status.set("Base de données vidée.")

    def show_aggregate(self) -> None:
        stats = self.database.aggregate()
        self.aggregate_label.configure(
            text=(
                f"Total : {stats['total']} | Terminés : {stats['completed']} | En attente : {stats['pending']} | "
                f"Longueur moyenne : {stats['average_length']:.2f} | Min : {stats['min_length']} | Max : {stats['max_length']}"
            )
        )
        self.status.set("Agrégation SQL calculée.")

    def draw_json_chart(self) -> None:
        stats = self.database.aggregate()
        self.json_axis.clear()
        if stats["total"] == 0:
            self.json_axis.text(0.5, 0.5, "Aucune donnée", ha="center", va="center", transform=self.json_axis.transAxes)
            self.json_axis.set_axis_off()
        else:
            self.json_axis.set_axis_on()
            self.json_axis.bar(["Terminés", "En attente"], [stats["completed"], stats["pending"]])
            self.json_axis.set_title(f"Répartition des tâches - longueur moyenne : {stats['average_length']:.2f}")
            self.json_axis.set_ylabel("Nombre de tâches")
            self.json_axis.grid(axis="y", alpha=0.25)
        self.json_figure.tight_layout()
        self.json_canvas.draw_idle()
        self.status.set("Graphique JSON affiché dans la fenêtre principale.")

    def analyse_book_async(self) -> None:
        self._run_async(analyse_book, self._after_book_analysis)

    def _after_book_analysis(self, analysis: BookAnalysis) -> None:
        self.analysis = analysis
        summary = (
            f"Titre : {analysis.title}\n"
            f"Auteur : {analysis.author}\n"
            f"Paragraphes : {len(analysis.paragraph_word_counts)}\n"
            f"Mots : {analysis.total_words}\n"
            f"Minimum : {analysis.min_words} | Maximum : {analysis.max_words} | Moyenne : {analysis.average_words:.2f}\n"
            f"Source du texte : {analysis.text_source}\n"
            f"Source de l’image : {analysis.image_source}\n"
            f"Fichiers créés : {analysis.processed_image_path.name} et {analysis.chart_path.name}"
        )
        self.book_summary.configure(state="normal")
        self.book_summary.delete("1.0", "end")
        self.book_summary.insert("1.0", summary)
        self.book_summary.configure(state="disabled")

        self.book_axis.clear()
        self.book_axis.bar([str(k) for k in analysis.rounded_distribution], list(analysis.rounded_distribution.values()))
        self.book_axis.set_title("Distribution des longueurs des paragraphes")
        self.book_axis.set_xlabel("Mots arrondis à la dizaine inférieure")
        self.book_axis.set_ylabel("Paragraphes")
        self.book_axis.grid(axis="y", alpha=0.25)
        self.book_figure.tight_layout()
        self.book_canvas.draw_idle()
        self.notebook.select(self.book_tab)
        if analysis.text_source.startswith("Internet"):
            self.status.set("Livre téléchargé sur Internet et analysé avec succès.")
        else:
            self.status.set("Gutenberg indisponible : analyse réalisée avec la copie locale de secours.")
            messagebox.showwarning(
                "Mode secours",
                "Project Gutenberg n’a pas répondu dans le délai prévu.\n"
                "L’analyse a quand même été réalisée avec la copie locale officielle incluse dans le projet.\n\n"
                "Tu peux continuer et exporter le rapport Word.",
            )

    def export_report(self) -> None:
        if self.analysis is None:
            messagebox.showwarning("Analyse requise", "Analysez d'abord le livre.")
            return

        suggested = OUTPUT_DIR / "rapport_alice.docx"
        destination = filedialog.asksaveasfilename(
            title="Enregistrer le rapport Word",
            initialdir=str(OUTPUT_DIR),
            initialfile=suggested.name,
            defaultextension=".docx",
            filetypes=[("Document Word", "*.docx")],
        )
        if not destination:
            return

        def task() -> Path:
            return create_word_report(self.analysis, Path(destination), REPORT_AUTHOR)

        self._run_async(task, self._after_report_export)

    def _after_report_export(self, path: Path) -> None:
        self.status.set(f"Rapport Word créé : {path.name}")
        messagebox.showinfo("Rapport créé", f"Le document Word a été enregistré ici :\n{path}")


if __name__ == "__main__":
    try:
        MainApplication().mainloop()
    except (ApiError, BookError, ReportError) as exc:
        messagebox.showerror("Erreur", str(exc))
