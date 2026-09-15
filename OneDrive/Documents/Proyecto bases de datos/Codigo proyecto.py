import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

import customtkinter as ctk
import psycopg2

try:
    from tkcalendar import DateEntry
except ImportError:
    DateEntry = None


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class AppAgenda(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Agenda 3 Patitos")
        self.geometry("1280x760")
        self.minsize(1050, 650)

        self.conn_params = {
            "dbname": "agenda",
            "user": "postgres",
            "password": "postgres",
            "host": "localhost",
            "port": "5432",
        }

        self.usuarios_combo = {}
        self.categorias_combo = {}
        self.categorias_padre_combo = {}
        self.eventos_combo = {}
        self.ubicaciones_combo = {}

        self.dias_semana = {
            "Lunes": 1, "Martes": 2, "Miércoles": 3, "Jueves": 4,
            "Viernes": 5, "Sábado": 6, "Domingo": 7,
        }
        self.dias_semana_inv = {v: k for k, v in self.dias_semana.items()}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.crear_sidebar()
        self.crear_area_principal()
        self.configurar_estilos()

        self.actualizar_todas_las_tablas()

        if DateEntry is None:
            self.after(500, lambda: messagebox.showwarning(
                "Calendario no instalado",
                "Para usar los selectores de fecha instala:\n\npip install tkcalendar"
            ))

    # -------------------- INFRAESTRUCTURA --------------------

    def obtener_conexion(self):
        conn = psycopg2.connect(**self.conn_params)
        with conn.cursor() as cur:
            cur.execute("SET search_path TO prototipo, public;")
        return conn

    def ejecutar_consulta(self, sql, params=None, fetch=False):
        conn = None
        try:
            conn = self.obtener_conexion()
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall() if fetch else None
            conn.commit()
            return rows
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def configurar_estilos(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def crear_treeview(self, parent, columnas, widths):
        contenedor = ctk.CTkFrame(parent, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        tree = ttk.Treeview(contenedor, columns=columnas, show="headings")
        for col, width in zip(columnas, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")
        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)
        return tree

    def seleccionar_modulo(self, nombre):
        self.tabview.set(nombre)
        for modulo, boton in self.botones_nav.items():
            boton.configure(fg_color=("gray75", "gray25") if modulo == nombre else "transparent")

    def crear_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=235, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(
            self.sidebar_frame,
            text="📅 AGENDA 🦆🦆🦆",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(28, 5), sticky="w")

        ctk.CTkLabel(
            self.sidebar_frame,
            text="Gestión de usuarios, categorías y eventos",
            font=ctk.CTkFont(size=11),
            wraplength=190,
            justify="left"
        ).grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

        self.botones_nav = {}
        for i, (nombre, icono) in enumerate([
            ("Usuarios", "👥"),
            ("Categorías", "📁"),
            ("Eventos", "🗓️"),
            ("Ubicaciones", "📍"),
            ("Disponibilidad", "⏰"),
            ("Tareas", "✅"),
        ], start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame, text=f"{icono}  {nombre}",
                anchor="w", fg_color="transparent",
                command=lambda n=nombre: self.seleccionar_modulo(n)
            )
            btn.grid(row=i, column=0, padx=15, pady=5, sticky="ew")
            self.botones_nav[nombre] = btn

        ctk.CTkButton(
            self.sidebar_frame,
            text="🔄  Recargar datos",
            command=self.actualizar_todas_las_tablas
        ).grid(row=9, column=0, padx=15, pady=(20, 5), sticky="ew")

        ctk.CTkLabel(self.sidebar_frame, text="APARIENCIA", font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=11, column=0, padx=20, pady=(10, 5), sticky="w"
        )
        self.option_mode = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["System", "Dark", "Light"],
            command=ctk.set_appearance_mode
        )
        self.option_mode.set("System")
        self.option_mode.grid(row=12, column=0, padx=15, pady=(0, 25), sticky="ew")

    def crear_area_principal(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.main_container, command=self.al_cambiar_pestana)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.tab_usuarios = self.tabview.add("Usuarios")
        self.tab_categorias = self.tabview.add("Categorías")
        self.tab_eventos = self.tabview.add("Eventos")

        self.tab_ubicaciones = self.tabview.add("Ubicaciones")
        self.tab_disponibilidad = self.tabview.add("Disponibilidad")
        self.tab_tareas = self.tabview.add("Tareas")

        self.configurar_pestana_usuarios()
        self.configurar_pestana_categorias()
        self.configurar_pestana_eventos()
        self.configurar_pestana_ubicaciones()
        self.configurar_pestana_disponibilidad()
        self.configurar_pestana_tareas()
        self.seleccionar_modulo("Usuarios")

    def al_cambiar_pestana(self):
        nombre = self.tabview.get()
        if nombre in self.botones_nav:
            for modulo, boton in self.botones_nav.items():
                boton.configure(fg_color=("gray75", "gray25") if modulo == nombre else "transparent")

    def crear_encabezado(self, parent, titulo, descripcion):
        ctk.CTkLabel(parent, text=titulo, font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 0)
        )
        ctk.CTkLabel(parent, text=descripcion, font=ctk.CTkFont(size=12)).pack(
            anchor="w", padx=15, pady=(0, 12)
        )

    # -------------------- USUARIOS --------------------

    def configurar_pestana_usuarios(self):
        self.crear_encabezado(self.tab_usuarios, "Usuarios", "Registra, consulta y administra los usuarios de la agenda.")

        cuerpo = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        tabla_frame = ctk.CTkFrame(cuerpo)
        tabla_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=300)
        form.grid(row=0, column=1, sticky="nsew")

        self.tree_usuarios = self.crear_treeview(
            tabla_frame, ("ID", "Nombre", "Apellido", "Registro", "Activo"),
            (70, 160, 160, 160, 80)
        )
        self.tree_usuarios.bind("<<TreeviewSelect>>", self.cargar_usuario_seleccionado)

        ctk.CTkLabel(form, text="Formulario de usuario", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        self.entry_nombre = ctk.CTkEntry(form, placeholder_text="Nombre")
        self.entry_nombre.pack(fill="x", padx=10, pady=6)
        self.entry_apellido = ctk.CTkEntry(form, placeholder_text="Apellido")
        self.entry_apellido.pack(fill="x", padx=10, pady=6)

        self.switch_usuario_activo = ctk.CTkSwitch(form, text="Usuario activo")
        self.switch_usuario_activo.select()
        self.switch_usuario_activo.pack(anchor="w", padx=12, pady=10)

        ctk.CTkButton(form, text="➕ Registrar usuario", command=self.agregar_usuario).pack(fill="x", padx=10, pady=(12, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionado", command=self.actualizar_usuario).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nuevo / Limpiar", command=self.limpiar_form_usuario, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionado", command=self.eliminar_usuario, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

    def usuario_seleccionado_id(self):
        sel = self.tree_usuarios.selection()
        return self.tree_usuarios.item(sel[0])["values"][0] if sel else None

    def cargar_usuario_seleccionado(self, _=None):
        sel = self.tree_usuarios.selection()
        if not sel:
            return
        vals = self.tree_usuarios.item(sel[0])["values"]
        self.entry_nombre.delete(0, tk.END); self.entry_nombre.insert(0, vals[1])
        self.entry_apellido.delete(0, tk.END); self.entry_apellido.insert(0, vals[2])
        if vals[4]:
            self.switch_usuario_activo.select()
        else:
            self.switch_usuario_activo.deselect()

    def limpiar_form_usuario(self):
        self.tree_usuarios.selection_remove(self.tree_usuarios.selection())
        self.entry_nombre.delete(0, tk.END)
        self.entry_apellido.delete(0, tk.END)
        self.switch_usuario_activo.select()

    def agregar_usuario(self):
        nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
        if not nombre or not apellido:
            return messagebox.showwarning("Campos incompletos", "Indica nombre y apellido.")
        try:
            self.ejecutar_consulta("INSERT INTO usuarios (nombre, apellido, activo) VALUES (%s, %s, %s)",
                                   (nombre, apellido, self.switch_usuario_activo.get() == 1))
            self.limpiar_form_usuario(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
        except Exception as e:
            messagebox.showerror("Error de base de datos", str(e))

    def actualizar_usuario(self):
        uid = self.usuario_seleccionado_id()
        if uid is None:
            return messagebox.showwarning("Selección requerida", "Selecciona un usuario para actualizar.")
        nombre, apellido = self.entry_nombre.get().strip(), self.entry_apellido.get().strip()
        if not nombre or not apellido:
            return messagebox.showwarning("Campos incompletos", "Indica nombre y apellido.")
        try:
            self.ejecutar_consulta("UPDATE usuarios SET nombre=%s, apellido=%s, activo=%s WHERE id_usuario=%s",
                                   (nombre, apellido, self.switch_usuario_activo.get() == 1, uid))
            self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Usuario actualizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_usuario(self):
        uid = self.usuario_seleccionado_id()
        if uid is None:
            return messagebox.showwarning("Selección requerida", "Selecciona un usuario.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar el usuario seleccionado?"):
            return
        try:
            self.ejecutar_consulta("DELETE FROM usuarios WHERE id_usuario=%s", (uid,))
            self.limpiar_form_usuario(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Eliminado", "Usuario eliminado.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_usuarios(self):
        try:
            rows = self.ejecutar_consulta(
                "SELECT id_usuario, nombre, apellido, fecha_registro, activo FROM usuarios ORDER BY nombre, apellido",
                fetch=True
            )
            for item in self.tree_usuarios.get_children(): self.tree_usuarios.delete(item)
            self.usuarios_combo = {}
            for row in rows:
                registro = row[3].strftime("%Y-%m-%d %H:%M") if hasattr(row[3], "strftime") else row[3]
                self.tree_usuarios.insert("", "end", values=(row[0], row[1], row[2], registro, "Sí" if row[4] else "No"))
                etiqueta = f"{row[1]} {row[2]} — #{row[0]}"
                self.usuarios_combo[etiqueta] = row[0]
        except Exception as e:
            print(f"Error cargando usuarios: {e}")

    # -------------------- CATEGORÍAS --------------------

    def configurar_pestana_categorias(self):
        self.crear_encabezado(self.tab_categorias, "Categorías", "Organiza los eventos mediante categorías y subcategorías.")

        cuerpo = ctk.CTkFrame(self.tab_categorias, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=320); form.grid(row=0, column=1, sticky="nsew")

        self.tree_categorias = self.crear_treeview(tabla, ("ID", "Categoría", "Categoría padre"), (80, 230, 230))
        self.tree_categorias.bind("<<TreeviewSelect>>", self.cargar_categoria_seleccionada)

        ctk.CTkLabel(form, text="Formulario de categoría", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        self.entry_cat_nombre = ctk.CTkEntry(form, placeholder_text="Nombre de la categoría")
        self.entry_cat_nombre.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(form, text="Categoría padre").pack(anchor="w", padx=10, pady=(10, 2))
        self.combo_cat_padre = ctk.CTkComboBox(form, values=["Sin categoría padre"], state="readonly")
        self.combo_cat_padre.set("Sin categoría padre")
        self.combo_cat_padre.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(form, text="➕ Crear categoría", command=self.agregar_categoria).pack(fill="x", padx=10, pady=(15, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionada", command=self.actualizar_categoria).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nueva / Limpiar", command=self.limpiar_form_categoria, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionada", command=self.eliminar_categoria, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

    def categoria_seleccionada_id(self):
        sel = self.tree_categorias.selection()
        return self.tree_categorias.item(sel[0])["values"][0] if sel else None

    def cargar_categoria_seleccionada(self, _=None):
        sel = self.tree_categorias.selection()
        if not sel: return
        vals = self.tree_categorias.item(sel[0])["values"]
        self.entry_cat_nombre.delete(0, tk.END); self.entry_cat_nombre.insert(0, vals[1])
        padre = vals[2]
        self.combo_cat_padre.set(padre if padre in self.categorias_padre_combo else "Sin categoría padre")

    def limpiar_form_categoria(self):
        self.tree_categorias.selection_remove(self.tree_categorias.selection())
        self.entry_cat_nombre.delete(0, tk.END); self.combo_cat_padre.set("Sin categoría padre")

    def _padre_id_actual(self):
        valor = self.combo_cat_padre.get()
        return None if valor == "Sin categoría padre" else self.categorias_padre_combo.get(valor)

    def agregar_categoria(self):
        nombre = self.entry_cat_nombre.get().strip()
        if not nombre: return messagebox.showwarning("Campo requerido", "Indica el nombre de la categoría.")
        try:
            self.ejecutar_consulta("INSERT INTO categorias (nombre, id_categoria_padre) VALUES (%s, %s)",
                                   (nombre, self._padre_id_actual()))
            self.limpiar_form_categoria(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Categoría creada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_categoria(self):
        cid = self.categoria_seleccionada_id()
        if cid is None: return messagebox.showwarning("Selección requerida", "Selecciona una categoría.")
        nombre = self.entry_cat_nombre.get().strip(); padre = self._padre_id_actual()
        if not nombre: return messagebox.showwarning("Campo requerido", "Indica el nombre.")
        if padre == cid: return messagebox.showwarning("Relación inválida", "Una categoría no puede ser su propia categoría padre.")
        try:
            self.ejecutar_consulta("UPDATE categorias SET nombre=%s, id_categoria_padre=%s WHERE id_categoria=%s",
                                   (nombre, padre, cid))
            self.actualizar_todas_las_tablas(); messagebox.showinfo("Éxito", "Categoría actualizada.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar_categoria(self):
        cid = self.categoria_seleccionada_id()
        if cid is None: return messagebox.showwarning("Selección requerida", "Selecciona una categoría.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar la categoría seleccionada?"): return
        try:
            self.ejecutar_consulta("DELETE FROM categorias WHERE id_categoria=%s", (cid,))
            self.limpiar_form_categoria(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Eliminado", "Categoría eliminada.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_categorias(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT c.id_categoria, c.nombre, p.nombre
                FROM categorias c
                LEFT JOIN categorias p ON p.id_categoria = c.id_categoria_padre
                ORDER BY c.nombre
            """, fetch=True)
            ids = self.ejecutar_consulta("SELECT id_categoria, nombre FROM categorias ORDER BY nombre", fetch=True)

            for item in self.tree_categorias.get_children(): self.tree_categorias.delete(item)
            self.categorias_combo = {}
            self.categorias_padre_combo = {}
            for cid, nombre in ids:
                etiqueta = f"{nombre} — #{cid}"
                self.categorias_combo[etiqueta] = cid
                self.categorias_padre_combo[etiqueta] = cid
            for row in rows:
                padre = "Sin categoría padre"
                if row[2] is not None:
                    # Buscar etiqueta completa del padre
                    for etiqueta, cid in self.categorias_padre_combo.items():
                        if etiqueta.startswith(f"{row[2]} —"):
                            padre = etiqueta; break
                self.tree_categorias.insert("", "end", values=(row[0], row[1], padre))

            valores_padre = ["Sin categoría padre"] + list(self.categorias_padre_combo.keys())
            self.combo_cat_padre.configure(values=valores_padre)
            if self.combo_cat_padre.get() not in valores_padre:
                self.combo_cat_padre.set("Sin categoría padre")
        except Exception as e:
            print(f"Error cargando categorías: {e}")

    # -------------------- EVENTOS --------------------

    def configurar_pestana_eventos(self):
        self.crear_encabezado(self.tab_eventos, "Eventos", "Programa eventos seleccionando usuarios, categorías, fechas y horas.")

        cuerpo = ctk.CTkFrame(self.tab_eventos, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=350); form.grid(row=0, column=1, sticky="nsew")

        self.tree_eventos = self.crear_treeview(
            tabla, ("ID", "Propietario", "Categoría", "Título", "Inicio", "Fin", "Ubicación"),
            (70, 170, 150, 220, 150, 150, 160)
        )

        self.tree_eventos.bind("<<TreeviewSelect>>", self.cargar_evento_seleccionado)

        ctk.CTkLabel(form, text="Formulario de evento", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 12))

        self.entry_ev_titulo = ctk.CTkEntry(form, placeholder_text="Título del evento")
        self.entry_ev_titulo.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(form, text="Propietario").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_ev_usuario = ctk.CTkComboBox(form, values=["Seleccione un usuario"], state="readonly")
        self.combo_ev_usuario.set("Seleccione un usuario")
        self.combo_ev_usuario.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Categoría").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_ev_categoria = ctk.CTkComboBox(form, values=["Seleccione una categoría"], state="readonly")
        self.combo_ev_categoria.set("Seleccione una categoría")
        self.combo_ev_categoria.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(form, text="Ubicación (opcional)").pack(anchor="w", padx=10, pady=(8, 2))
        self.combo_ev_ubicacion = ctk.CTkComboBox(form, values=["Sin ubicación asignada"], state="readonly")
        self.combo_ev_ubicacion.set("Sin ubicación asignada")
        self.combo_ev_ubicacion.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Inicio").pack(anchor="w", padx=10, pady=(10, 2))
        fila_inicio = ctk.CTkFrame(form, fg_color="transparent"); fila_inicio.pack(fill="x", padx=10)
        self.fecha_inicio = self.crear_selector_fecha(fila_inicio)
        self.fecha_inicio.pack(side="left", fill="x", expand=True)
        self.hora_inicio = ctk.CTkEntry(fila_inicio, placeholder_text="HH:MM", width=75)
        self.hora_inicio.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(form, text="Fin").pack(anchor="w", padx=10, pady=(10, 2))
        fila_fin = ctk.CTkFrame(form, fg_color="transparent"); fila_fin.pack(fill="x", padx=10)
        self.fecha_fin = self.crear_selector_fecha(fila_fin)
        self.fecha_fin.pack(side="left", fill="x", expand=True)
        self.hora_fin = ctk.CTkEntry(fila_fin, placeholder_text="HH:MM", width=75)
        self.hora_fin.pack(side="left", padx=(6, 0))

        ctk.CTkButton(form, text="➕ Crear evento", command=self.agregar_evento).pack(fill="x", padx=10, pady=(16, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionado", command=self.actualizar_evento).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nuevo / Limpiar", command=self.limpiar_form_evento, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionado", command=self.eliminar_evento, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

        self.limpiar_form_evento()

    def crear_selector_fecha(self, parent):
        if DateEntry is not None:
            return DateEntry(parent, date_pattern="yyyy-mm-dd", font=("Arial", 10))
        return ttk.Entry(parent)

    def obtener_fecha(self, widget):
        if DateEntry is not None:
            return widget.get_date().strftime("%Y-%m-%d")
        return widget.get().strip()

    def establecer_fecha(self, widget, valor):
        fecha = valor.date() if hasattr(valor, "date") else datetime.strptime(str(valor)[:10], "%Y-%m-%d").date()
        if DateEntry is not None:
            widget.set_date(fecha)
        else:
            widget.delete(0, tk.END); widget.insert(0, fecha.strftime("%Y-%m-%d"))

    def evento_seleccionado_id(self):
        sel = self.tree_eventos.selection()
        return self.tree_eventos.item(sel[0])["values"][0] if sel else None

    def cargar_evento_seleccionado(self, _=None):
        sel = self.tree_eventos.selection()
        if not sel: return
        vals = self.tree_eventos.item(sel[0])["values"]
        self.entry_ev_titulo.delete(0, tk.END); self.entry_ev_titulo.insert(0, vals[3])
        self.combo_ev_usuario.set(vals[1])
        ubicacion = vals[6] if len(vals) > 6 and vals[6] else "Sin ubicación asignada"
        self.combo_ev_ubicacion.set(ubicacion if ubicacion in self.ubicaciones_combo else "Sin ubicación asignada")
        self.combo_ev_categoria.set(vals[2])
        try:
            ini = datetime.strptime(str(vals[4]), "%Y-%m-%d %H:%M")
            fin = datetime.strptime(str(vals[5]), "%Y-%m-%d %H:%M")
            self.establecer_fecha(self.fecha_inicio, ini)
            self.establecer_fecha(self.fecha_fin, fin)
            self.hora_inicio.delete(0, tk.END); self.hora_inicio.insert(0, ini.strftime("%H:%M"))
            self.hora_fin.delete(0, tk.END); self.hora_fin.insert(0, fin.strftime("%H:%M"))
        except ValueError:
            pass

    def limpiar_form_evento(self):
        self.tree_eventos.selection_remove(self.tree_eventos.selection())
        self.entry_ev_titulo.delete(0, tk.END)
        self.combo_ev_usuario.set("Seleccione un usuario")
        self.combo_ev_categoria.set("Seleccione una categoría")
        self.combo_ev_ubicacion.set("Sin ubicación asignada")
        hoy = datetime.now()
        self.establecer_fecha(self.fecha_inicio, hoy); self.establecer_fecha(self.fecha_fin, hoy)
        self.hora_inicio.delete(0, tk.END); self.hora_inicio.insert(0, "09:00")
        self.hora_fin.delete(0, tk.END); self.hora_fin.insert(0, "10:00")

    def datos_evento_formulario(self):
        titulo = self.entry_ev_titulo.get().strip()
        usuario = self.usuarios_combo.get(self.combo_ev_usuario.get())
        categoria = self.categorias_combo.get(self.combo_ev_categoria.get())
        valor_ubicacion = self.combo_ev_ubicacion.get()
        ubicacion = None if valor_ubicacion == "Sin ubicación asignada" else self.ubicaciones_combo.get(valor_ubicacion)
        try:
            inicio = datetime.strptime(f"{self.obtener_fecha(self.fecha_inicio)} {self.hora_inicio.get().strip()}", "%Y-%m-%d %H:%M")
            fin = datetime.strptime(f"{self.obtener_fecha(self.fecha_fin)} {self.hora_fin.get().strip()}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError("La hora debe tener formato HH:MM, por ejemplo 09:30.")
        if not titulo or usuario is None or categoria is None:
            raise ValueError("Completa título, propietario y categoría.")
        if fin <= inicio:
            raise ValueError("La fecha y hora de finalización deben ser posteriores al inicio.")
        return usuario, categoria, titulo, inicio, fin, ubicacion

    def agregar_evento(self):
        try:
            datos = self.datos_evento_formulario()
            self.ejecutar_consulta("""
                INSERT INTO eventos
                (id_usuario_propietario, id_categoria, titulo, fecha_inicio, fecha_fin, id_ubicacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, datos)
            self.limpiar_form_evento(); self.cargar_datos_eventos()
            messagebox.showinfo("Éxito", "Evento creado correctamente.")
        except Exception as e:
            messagebox.showerror("No se pudo crear el evento", str(e))

    def actualizar_evento(self):
        eid = self.evento_seleccionado_id()
        if eid is None: return messagebox.showwarning("Selección requerida", "Selecciona un evento.")
        try:
            usuario, categoria, titulo, inicio, fin, ubicacion = self.datos_evento_formulario()
            self.ejecutar_consulta("""
                UPDATE eventos SET id_usuario_propietario=%s, id_categoria=%s,
                titulo=%s, fecha_inicio=%s, fecha_fin=%s, id_ubicacion=%s WHERE id_evento=%s
            """, (usuario, categoria, titulo, inicio, fin, ubicacion, eid))
            self.cargar_datos_eventos(); messagebox.showinfo("Éxito", "Evento actualizado.")
        except Exception as e:
            messagebox.showerror("No se pudo actualizar", str(e))

    def eliminar_evento(self):
        eid = self.evento_seleccionado_id()
        if eid is None: return messagebox.showwarning("Selección requerida", "Selecciona un evento.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar el evento seleccionado?"): return
        try:
            self.ejecutar_consulta("DELETE FROM eventos WHERE id_evento=%s", (eid,))
            self.limpiar_form_evento(); self.cargar_datos_eventos()
            messagebox.showinfo("Eliminado", "Evento eliminado.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_eventos(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT e.id_evento, u.id_usuario, u.nombre, u.apellido,
                       c.id_categoria, c.nombre, e.titulo, e.fecha_inicio, e.fecha_fin,
                       ub.id_ubicacion, ub.tipo_ubicacion
                FROM eventos e
                JOIN usuarios u ON u.id_usuario = e.id_usuario_propietario
                JOIN categorias c ON c.id_categoria = e.id_categoria
                LEFT JOIN ubicaciones ub ON ub.id_ubicacion = e.id_ubicacion
                ORDER BY e.fecha_inicio DESC
            """, fetch=True)
            for item in self.tree_eventos.get_children(): self.tree_eventos.delete(item)
            self.eventos_combo = {}
            for row in rows:
                usuario = f"{row[2]} {row[3]} — #{row[1]}"
                categoria = f"{row[5]} — #{row[4]}"
                inicio = row[7].strftime("%Y-%m-%d %H:%M") if hasattr(row[7], "strftime") else row[7]
                fin = row[8].strftime("%Y-%m-%d %H:%M") if hasattr(row[8], "strftime") else row[8]
                ubicacion = f"{row[10]} — #{row[9]}" if row[9] is not None else ""
                self.tree_eventos.insert("", "end", values=(row[0], usuario, categoria, row[6], inicio, fin, ubicacion))
                self.eventos_combo[f"{row[6]} — #{row[0]}"] = row[0]

            valores_u = ["Seleccione un usuario"] + list(self.usuarios_combo.keys())
            valores_c = ["Seleccione una categoría"] + list(self.categorias_combo.keys())
            valores_ub = ["Sin ubicación asignada"] + list(self.ubicaciones_combo.keys())
            self.combo_ev_usuario.configure(values=valores_u)
            self.combo_ev_categoria.configure(values=valores_c)
            self.combo_ev_ubicacion.configure(values=valores_ub)
            if self.combo_ev_ubicacion.get() not in valores_ub:
                self.combo_ev_ubicacion.set("Sin ubicación asignada")
            if hasattr(self, "combo_tarea_evento"):
                valores_ev = ["Selecciñne un evento"] + list(self.eventos_combo.keys())
                self.combo_tarea_evento.configure(values=valores_ev)
        except Exception as e:
            print(f"Error cargando eventos: {e}")

    # -------------------- REFRESCO GENERAL --------------------
    # ----------------Implementaciones Gnereles --------------------

    def configurar_pestana_ubicaciones(self):
        self.crear_encabezado(
            self.tab_ubicaciones, "Ubicaciones",
            "Administra salas, auditorios y recintos físicos asignables a los eventos."
        )

        cuerpo = ctk.CTkFrame(self.tab_ubicaciones, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=300); form.grid(row=0, column=1, sticky="nsew")

        self.tree_ubicaciones = self.crear_treeview(
            tabla, ("ID", "Tipo", "Capacidad", "Dirección"), (60, 150, 100, 260)
        )
        self.tree_ubicaciones.bind("<<TreeviewSelect>>", self.cargar_ubicacion_seleccionada)

        ctk.CTkLabel(form, text="Formulario de ubicación", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))
        self.entry_ub_tipo = ctk.CTkEntry(form, placeholder_text="Tipo (Sala, Auditorio, Oficina...)")
        self.entry_ub_tipo.pack(fill="x", padx=10, pady=6)
        self.entry_ub_capacidad = ctk.CTkEntry(form, placeholder_text="Capacidad (número de personas)")
        self.entry_ub_capacidad.pack(fill="x", padx=10, pady=6)
        self.entry_ub_direccion = ctk.CTkEntry(form, placeholder_text="Dirección / ubicación física")
        self.entry_ub_direccion.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(form, text="➕ Crear ubicación", command=self.agregar_ubicacion).pack(fill="x", padx=10, pady=(15, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionada", command=self.actualizar_ubicacion).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nueva / Limpiar", command=self.limpiar_form_ubicacion, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionada", command=self.eliminar_ubicacion, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(form, text="Eventos programados en la ubicación seleccionada", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(20, 4))
        self.lista_ocupacion_ubicacion = tk.Listbox(form, height=8)
        self.lista_ocupacion_ubicacion.pack(fill="x", padx=10, pady=(0, 10))

    def ubicacion_seleccionada_id(self):
        sel = self.tree_ubicaciones.selection()
        return self.tree_ubicaciones.item(sel[0])["values"][0] if sel else None

    def cargar_ubicacion_seleccionada(self, _=None):
        sel = self.tree_ubicaciones.selection()
        if not sel: return
        vals = self.tree_ubicaciones.item(sel[0])["values"]
        self.entry_ub_tipo.delete(0, tk.END); self.entry_ub_tipo.insert(0, vals[1])
        self.entry_ub_capacidad.delete(0, tk.END); self.entry_ub_capacidad.insert(0, vals[2])
        self.entry_ub_direccion.delete(0, tk.END); self.entry_ub_direccion.insert(0, vals[3])
        self.cargar_ocupacion_ubicacion(vals[0])

    def limpiar_form_ubicacion(self):
        self.tree_ubicaciones.selection_remove(self.tree_ubicaciones.selection())
        self.entry_ub_tipo.delete(0, tk.END)
        self.entry_ub_capacidad.delete(0, tk.END)
        self.entry_ub_direccion.delete(0, tk.END)
        self.lista_ocupacion_ubicacion.delete(0, tk.END)

    def datos_ubicacion_formulario(self):
        tipo = self.entry_ub_tipo.get().strip()
        direccion = self.entry_ub_direccion.get().strip()
        capacidad_txt = self.entry_ub_capacidad.get().strip()
        if not tipo or not direccion or not capacidad_txt:
            raise ValueError("Completa tipo, capacidad y dirección.")
        try:
            capacidad = int(capacidad_txt)
        except ValueError:
            raise ValueError("La capacidad debe ser un número entero.")
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser mayor a cero.")
        return tipo, capacidad, direccion

    def agregar_ubicacion(self):
        try:
            tipo, capacidad, direccion = self.datos_ubicacion_formulario()
            self.ejecutar_consulta(
                "INSERT INTO ubicaciones (tipo_ubicacion, capacidad, direccion) VALUES (%s, %s, %s)",
                (tipo, capacidad, direccion)
            )
            self.limpiar_form_ubicacion(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Éxito", "Ubicación creada correctamente.")
        except Exception as e:
            messagebox.showerror("No se pudo crear la ubicación", str(e))

    def actualizar_ubicacion(self):
        uid = self.ubicacion_seleccionada_id()
        if uid is None: return messagebox.showwarning("Selección requerida", "Selecciona una ubicación.")
        try:
            tipo, capacidad, direccion = self.datos_ubicacion_formulario()
            self.ejecutar_consulta(
                "UPDATE ubicaciones SET tipo_ubicacion=%s, capacidad=%s, direccion=%s WHERE id_ubicacion=%s",
                (tipo, capacidad, direccion, uid)
            )
            self.actualizar_todas_las_tablas(); messagebox.showinfo("Éxito", "Ubicación actualizada.")
        except Exception as e:
            messagebox.showerror("No se pudo actualizar", str(e))

    def eliminar_ubicacion(self):
        uid = self.ubicacion_seleccionada_id()
        if uid is None: return messagebox.showwarning("Selección requerida", "Selecciona una ubicación.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar la ubicación seleccionada?"): return
        try:
            self.ejecutar_consulta("DELETE FROM ubicaciones WHERE id_ubicacion=%s", (uid,))
            self.limpiar_form_ubicacion(); self.actualizar_todas_las_tablas()
            messagebox.showinfo("Eliminado", "Ubicación eliminada.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", "La ubicación está asignada a eventos existentes o ocurrió un error.\n" + str(e))

    def cargar_ocupacion_ubicacion(self, id_ubicacion):
        self.lista_ocupacion_ubicacion.delete(0, tk.END)
        try:
            rows = self.ejecutar_consulta("""
                SELECT titulo, fecha_inicio, fecha_fin FROM eventos
                WHERE id_ubicacion = %s ORDER BY fecha_inicio
            """, (id_ubicacion,), fetch=True)
            for titulo, inicio, fin in rows:
                ini_s = inicio.strftime("%Y-%m-%d %H:%M") if hasattr(inicio, "strftime") else inicio
                fin_s = fin.strftime("%H:%M") if hasattr(fin, "strftime") else fin
                self.lista_ocupacion_ubicacion.insert(tk.END, f"{titulo}  ({ini_s} - {fin_s})")
        except Exception as e:
            print(f"Error cargando ocupación de ubicación: {e}")

    def cargar_datos_ubicaciones(self):
        try:
            rows = self.ejecutar_consulta(
                "SELECT id_ubicacion, tipo_ubicacion, capacidad, direccion FROM ubicaciones ORDER BY tipo_ubicacion",
                fetch=True
            )
            for item in self.tree_ubicaciones.get_children(): self.tree_ubicaciones.delete(item)
            self.ubicaciones_combo = {}
            for row in rows:
                self.tree_ubicaciones.insert("", "end", values=row)
                etiqueta = f"{row[1]} — #{row[0]}"
                self.ubicaciones_combo[etiqueta] = row[0]
        except Exception as e:
            print(f"Error cargando ubicaciones: {e}")

    # -------------------- DISPONIBILIDAD DE USUARIOS (RF-11 y RF-12) --------------------

    def configurar_pestana_disponibilidad(self):
        self.crear_encabezado(
            self.tab_disponibilidad, "Disponibilidad de Usuarios",
            "Registra bloques horarios de disponibilidad y consulta la concurrencia entre usuarios."
        )

        cuerpo = ctk.CTkFrame(self.tab_disponibilidad, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=300); form.grid(row=0, column=1, sticky="nsew")

        self.tree_disponibilidad = self.crear_treeview(
            tabla, ("Usuario", "Día", "Hora inicio", "Hora fin"), (180, 110, 100, 100)
        )
        self.tree_disponibilidad.bind("<<TreeviewSelect>>", self.cargar_disponibilidad_seleccionada)

        ctk.CTkLabel(form, text="Formulario de disponibilidad", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))

        ctk.CTkLabel(form, text="Usuario").pack(anchor="w", padx=10, pady=(4, 2))
        self.combo_disp_usuario = ctk.CTkComboBox(form, values=["Seleccione un usuario"], state="readonly")
        self.combo_disp_usuario.set("Seleccione un usuario")
        self.combo_disp_usuario.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Día de la semana").pack(anchor="w", padx=10, pady=(10, 2))
        self.combo_disp_dia = ctk.CTkComboBox(form, values=list(self.dias_semana.keys()), state="readonly")
        self.combo_disp_dia.set("Lunes")
        self.combo_disp_dia.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Hora inicio (HH:MM)").pack(anchor="w", padx=10, pady=(10, 2))
        self.entry_disp_hora_inicio = ctk.CTkEntry(form, placeholder_text="08:00")
        self.entry_disp_hora_inicio.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Hora fin (HH:MM)").pack(anchor="w", padx=10, pady=(10, 2))
        self.entry_disp_hora_fin = ctk.CTkEntry(form, placeholder_text="10:00")
        self.entry_disp_hora_fin.pack(fill="x", padx=10, pady=4)

        ctk.CTkButton(form, text="➕ Registrar disponibilidad", command=self.agregar_disponibilidad).pack(fill="x", padx=10, pady=(16, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionada", command=self.actualizar_disponibilidad).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nueva / Limpiar", command=self.limpiar_form_disponibilidad, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionada", command=self.eliminar_disponibilidad, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(form, text="🔎 Ver concurrencia entre usuarios", command=self.mostrar_concurrencia).pack(fill="x", padx=10, pady=(20, 5))

        self.limpiar_form_disponibilidad()

    def _disponibilidad_seleccionada_clave(self):
        """PK compuesta: (id_usuario, dia_semana, hora_inicio). Se guarda al seleccionar la fila."""
        return getattr(self, "_disp_clave_actual", None)

    def cargar_disponibilidad_seleccionada(self, _=None):
        sel = self.tree_disponibilidad.selection()
        if not sel: return
        vals = self.tree_disponibilidad.item(sel[0])["values"]
        etiqueta_usuario, dia_txt, hora_ini, hora_fin = vals
        if etiqueta_usuario in self.usuarios_combo:
            self.combo_disp_usuario.set(etiqueta_usuario)
        self.combo_disp_dia.set(dia_txt)
        self.entry_disp_hora_inicio.delete(0, tk.END); self.entry_disp_hora_inicio.insert(0, str(hora_ini)[:5])
        self.entry_disp_hora_fin.delete(0, tk.END); self.entry_disp_hora_fin.insert(0, str(hora_fin)[:5])
        self._disp_clave_actual = (
            self.usuarios_combo.get(etiqueta_usuario), self.dias_semana.get(dia_txt), str(hora_ini)
        )

    def limpiar_form_disponibilidad(self):
        self.tree_disponibilidad.selection_remove(self.tree_disponibilidad.selection())
        self.combo_disp_usuario.set("Seleccione un usuario")
        self.combo_disp_dia.set("Lunes")
        self.entry_disp_hora_inicio.delete(0, tk.END); self.entry_disp_hora_inicio.insert(0, "08:00")
        self.entry_disp_hora_fin.delete(0, tk.END); self.entry_disp_hora_fin.insert(0, "10:00")
        self._disp_clave_actual = None

    def datos_disponibilidad_formulario(self):
        usuario = self.usuarios_combo.get(self.combo_disp_usuario.get())
        dia = self.dias_semana.get(self.combo_disp_dia.get())
        try:
            hora_inicio = datetime.strptime(self.entry_disp_hora_inicio.get().strip(), "%H:%M").time()
            hora_fin = datetime.strptime(self.entry_disp_hora_fin.get().strip(), "%H:%M").time()
        except ValueError:
            raise ValueError("Las horas deben tener formato HH:MM, por ejemplo 08:30.")
        if usuario is None:
            raise ValueError("Selecciona un usuario.")
        if hora_fin <= hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")
        return usuario, dia, hora_inicio, hora_fin

    def agregar_disponibilidad(self):
        try:
            usuario, dia, hora_inicio, hora_fin = self.datos_disponibilidad_formulario()
            self.ejecutar_consulta(
                "INSERT INTO disponibilidad_y_gestion (id_usuario, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)",
                (usuario, dia, hora_inicio, hora_fin)
            )
            self.limpiar_form_disponibilidad(); self.cargar_datos_disponibilidad()
            messagebox.showinfo("Éxito", "Disponibilidad registrada.")
        except Exception as e:
            messagebox.showerror("No se pudo registrar", str(e))

    def actualizar_disponibilidad(self):
        clave = self._disponibilidad_seleccionada_clave()
        if clave is None: return messagebox.showwarning("Selección requerida", "Selecciona un bloque de disponibilidad.")
        try:
            usuario, dia, hora_inicio, hora_fin = self.datos_disponibilidad_formulario()
            conn = self.obtener_conexion()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM disponibilidad_y_gestion WHERE id_usuario=%s AND dia_semana=%s AND hora_inicio=%s",
                        clave
                    )
                    cur.execute(
                        "INSERT INTO disponibilidad_y_gestion (id_usuario, dia_semana, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s)",
                        (usuario, dia, hora_inicio, hora_fin)
                    )
                conn.commit()
            except Exception:
                conn.rollback(); raise
            finally:
                conn.close()
            self.limpiar_form_disponibilidad(); self.cargar_datos_disponibilidad()
            messagebox.showinfo("Éxito", "Disponibilidad actualizada.")
        except Exception as e:
            messagebox.showerror("No se pudo actualizar", str(e))

    def eliminar_disponibilidad(self):
        clave = self._disponibilidad_seleccionada_clave()
        if clave is None: return messagebox.showwarning("Selección requerida", "Selecciona un bloque de disponibilidad.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar el bloque de disponibilidad seleccionado?"): return
        try:
            self.ejecutar_consulta(
                "DELETE FROM disponibilidad_y_gestion WHERE id_usuario=%s AND dia_semana=%s AND hora_inicio=%s",
                clave
            )
            self.limpiar_form_disponibilidad(); self.cargar_datos_disponibilidad()
            messagebox.showinfo("Eliminado", "Disponibilidad eliminada.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_disponibilidad(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT u.id_usuario, u.nombre, u.apellido, d.dia_semana, d.hora_inicio, d.hora_fin
                FROM disponibilidad_y_gestion d
                JOIN usuarios u ON u.id_usuario = d.id_usuario
                ORDER BY u.nombre, d.dia_semana, d.hora_inicio
            """, fetch=True)
            for item in self.tree_disponibilidad.get_children(): self.tree_disponibilidad.delete(item)
            for uid, nombre, apellido, dia, hora_i, hora_f in rows:
                etiqueta_usuario = f"{nombre} {apellido} — #{uid}"
                dia_txt = self.dias_semana_inv.get(dia, str(dia))
                self.tree_disponibilidad.insert("", "end", values=(etiqueta_usuario, dia_txt, str(hora_i)[:5], str(hora_f)[:5]))

            valores_u = ["Seleccione un usuario"] + list(self.usuarios_combo.keys())
            self.combo_disp_usuario.configure(values=valores_u)
        except Exception as e:
            print(f"Error cargando disponibilidad: {e}")

    def mostrar_concurrencia(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT u1.nombre, u1.apellido, u2.nombre, u2.apellido, v.dia_semana, v.inicio_comun, v.fin_comun
                FROM vista_concurrencia_usuarios v
                JOIN usuarios u1 ON u1.id_usuario = v.usuario_1
                JOIN usuarios u2 ON u2.id_usuario = v.usuario_2
                ORDER BY v.dia_semana, v.inicio_comun
            """, fetch=True)
            if not rows:
                return messagebox.showinfo("Concurrencia", "No hay bloques de disponibilidad que coincidan entre usuarios.")
            texto = "\n".join(
                f"{n1} {a1}  y  {n2} {a2}  —  {self.dias_semana_inv.get(dia, dia)}  "
                f"{str(ini)[:5]} a {str(fin)[:5]}"
                for n1, a1, n2, a2, dia, ini, fin in rows
            )
            messagebox.showinfo("Concurrencia entre usuarios", texto)
        except Exception as e:
            messagebox.showerror("No se pudo consultar", str(e))

    # -------------------- TAREAS ASOCIADAS A EVENTOS (RF-15 a RF-17) --------------------

    def configurar_pestana_tareas(self):
        self.crear_encabezado(
            self.tab_tareas, "Tareas",
            "Gestiona subtareas de los eventos: responsables, prioridad, estado y plazos."
        )

        cuerpo = ctk.CTkFrame(self.tab_tareas, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=10, pady=5)
        cuerpo.grid_columnconfigure(0, weight=3); cuerpo.grid_columnconfigure(1, weight=1); cuerpo.grid_rowconfigure(0, weight=1)

        tabla = ctk.CTkFrame(cuerpo); tabla.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        form = ctk.CTkScrollableFrame(cuerpo, width=320); form.grid(row=0, column=1, sticky="nsew")

        self.tree_tareas = self.crear_treeview(
            tabla, ("ID", "Evento", "Descripción", "Fecha límite", "Prioridad", "Estado", "Responsable"),
            (60, 160, 220, 150, 90, 100, 160)
        )
        self.tree_tareas.bind("<<TreeviewSelect>>", self.cargar_tarea_seleccionada)

        ctk.CTkLabel(form, text="Formulario de tarea", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))

        ctk.CTkLabel(form, text="Evento").pack(anchor="w", padx=10, pady=(4, 2))
        self.combo_tarea_evento = ctk.CTkComboBox(form, values=["Seleccione un evento"], state="readonly")
        self.combo_tarea_evento.set("Seleccione un evento")
        self.combo_tarea_evento.pack(fill="x", padx=10, pady=4)

        self.entry_tarea_descripcion = ctk.CTkEntry(form, placeholder_text="Descripción de la subtarea")
        self.entry_tarea_descripcion.pack(fill="x", padx=10, pady=6)

        ctk.CTkLabel(form, text="Fecha y hora límite").pack(anchor="w", padx=10, pady=(8, 2))
        fila_limite = ctk.CTkFrame(form, fg_color="transparent"); fila_limite.pack(fill="x", padx=10)
        self.fecha_tarea_limite = self.crear_selector_fecha(fila_limite)
        self.fecha_tarea_limite.pack(side="left", fill="x", expand=True)
        self.hora_tarea_limite = ctk.CTkEntry(fila_limite, placeholder_text="HH:MM", width=75)
        self.hora_tarea_limite.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(form, text="Prioridad").pack(anchor="w", padx=10, pady=(10, 2))
        self.combo_tarea_prioridad = ctk.CTkComboBox(form, values=["baja", "media", "alta", "critica"], state="readonly")
        self.combo_tarea_prioridad.set("media")
        self.combo_tarea_prioridad.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Estado").pack(anchor="w", padx=10, pady=(10, 2))
        self.combo_tarea_estado = ctk.CTkComboBox(
            form, values=["pendiente", "en_progreso", "completada", "cancelada"], state="readonly"
        )
        self.combo_tarea_estado.set("pendiente")
        self.combo_tarea_estado.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(form, text="Responsable").pack(anchor="w", padx=10, pady=(10, 2))
        self.combo_tarea_responsable = ctk.CTkComboBox(form, values=["Sin responsable asignado"], state="readonly")
        self.combo_tarea_responsable.set("Sin responsable asignado")
        self.combo_tarea_responsable.pack(fill="x", padx=10, pady=4)

        ctk.CTkButton(form, text="➕ Crear tarea", command=self.agregar_tarea).pack(fill="x", padx=10, pady=(16, 5))
        ctk.CTkButton(form, text="💾 Actualizar seleccionada", command=self.actualizar_tarea).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🧹 Nueva / Limpiar", command=self.limpiar_form_tarea, fg_color="gray").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="🗑️ Eliminar seleccionada", command=self.eliminar_tarea, fg_color="#b33939", hover_color="#8f2d2d").pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(form, text="⏳ Ver tareas vencidas", command=self.mostrar_tareas_vencidas).pack(fill="x", padx=10, pady=(20, 5))

        self.limpiar_form_tarea()

    def tarea_seleccionada_id(self):
        sel = self.tree_tareas.selection()
        return self.tree_tareas.item(sel[0])["values"][0] if sel else None

    def cargar_tarea_seleccionada(self, _=None):
        sel = self.tree_tareas.selection()
        if not sel: return
        vals = self.tree_tareas.item(sel[0])["values"]
        _id, evento_txt, descripcion, limite, prioridad, estado, responsable_txt = vals
        if evento_txt in self.eventos_combo:
            self.combo_tarea_evento.set(evento_txt)
        self.entry_tarea_descripcion.delete(0, tk.END); self.entry_tarea_descripcion.insert(0, descripcion)
        try:
            limite_dt = datetime.strptime(str(limite), "%Y-%m-%d %H:%M")
            self.establecer_fecha(self.fecha_tarea_limite, limite_dt)
            self.hora_tarea_limite.delete(0, tk.END); self.hora_tarea_limite.insert(0, limite_dt.strftime("%H:%M"))
        except ValueError:
            pass
        self.combo_tarea_prioridad.set(prioridad)
        self.combo_tarea_estado.set(estado)
        self.combo_tarea_responsable.set(responsable_txt if responsable_txt in self.usuarios_combo else "Sin responsable asignado")

    def limpiar_form_tarea(self):
        self.tree_tareas.selection_remove(self.tree_tareas.selection())
        self.combo_tarea_evento.set("Seleccione un evento")
        self.entry_tarea_descripcion.delete(0, tk.END)
        hoy = datetime.now()
        self.establecer_fecha(self.fecha_tarea_limite, hoy)
        self.hora_tarea_limite.delete(0, tk.END); self.hora_tarea_limite.insert(0, "18:00")
        self.combo_tarea_prioridad.set("media")
        self.combo_tarea_estado.set("pendiente")
        self.combo_tarea_responsable.set("Sin responsable asignado")

    def datos_tarea_formulario(self):
        evento = self.eventos_combo.get(self.combo_tarea_evento.get())
        descripcion = self.entry_tarea_descripcion.get().strip()
        prioridad = self.combo_tarea_prioridad.get()
        estado = self.combo_tarea_estado.get()
        valor_resp = self.combo_tarea_responsable.get()
        responsable = None if valor_resp == "Sin responsable asignado" else self.usuarios_combo.get(valor_resp)
        try:
            limite = datetime.strptime(
                f"{self.obtener_fecha(self.fecha_tarea_limite)} {self.hora_tarea_limite.get().strip()}", "%Y-%m-%d %H:%M"
            )
        except ValueError:
            raise ValueError("La hora límite debe tener formato HH:MM, por ejemplo 18:00.")
        if evento is None or not descripcion:
            raise ValueError("Selecciona un evento e indica la descripción de la tarea.")
        return evento, descripcion, limite, prioridad, estado, responsable

    def agregar_tarea(self):
        try:
            evento, descripcion, limite, prioridad, estado, responsable = self.datos_tarea_formulario()
            filas = self.ejecutar_consulta("""
                INSERT INTO tareas_evento (id_evento, descripcion, fecha_limite, prioridad, estado)
                VALUES (%s, %s, %s, %s, %s) RETURNING id_tarea
            """, (evento, descripcion, limite, prioridad, estado), fetch=True)
            id_tarea = filas[0][0]
            if responsable is not None:
                self.ejecutar_consulta(
                    "INSERT INTO tarea_usuario_asignado (id_tarea, id_usuario) VALUES (%s, %s)",
                    (id_tarea, responsable)
                )
            self.limpiar_form_tarea(); self.cargar_datos_tareas()
            messagebox.showinfo("Éxito", "Tarea creada correctamente.")
        except Exception as e:
            messagebox.showerror("No se pudo crear la tarea", str(e))

    def actualizar_tarea(self):
        tid = self.tarea_seleccionada_id()
        if tid is None: return messagebox.showwarning("Selección requerida", "Selecciona una tarea.")
        try:
            evento, descripcion, limite, prioridad, estado, responsable = self.datos_tarea_formulario()
            self.ejecutar_consulta("""
                UPDATE tareas_evento SET id_evento=%s, descripcion=%s, fecha_limite=%s,
                prioridad=%s, estado=%s WHERE id_tarea=%s
            """, (evento, descripcion, limite, prioridad, estado, tid))
            self.ejecutar_consulta("DELETE FROM tarea_usuario_asignado WHERE id_tarea=%s", (tid,))
            if responsable is not None:
                self.ejecutar_consulta(
                    "INSERT INTO tarea_usuario_asignado (id_tarea, id_usuario) VALUES (%s, %s)",
                    (tid, responsable)
                )
            self.cargar_datos_tareas(); messagebox.showinfo("Éxito", "Tarea actualizada.")
        except Exception as e:
            messagebox.showerror("No se pudo actualizar", str(e))

    def eliminar_tarea(self):
        tid = self.tarea_seleccionada_id()
        if tid is None: return messagebox.showwarning("Selección requerida", "Selecciona una tarea.")
        if not messagebox.askyesno("Confirmar", "¿Eliminar la tarea seleccionada?"): return
        try:
            self.ejecutar_consulta("DELETE FROM tareas_evento WHERE id_tarea=%s", (tid,))
            self.limpiar_form_tarea(); self.cargar_datos_tareas()
            messagebox.showinfo("Eliminado", "Tarea eliminada.")
        except Exception as e:
            messagebox.showerror("No se pudo eliminar", str(e))

    def cargar_datos_tareas(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT t.id_tarea, e.id_evento, e.titulo, t.descripcion, t.fecha_limite,
                       t.prioridad, t.estado, u.id_usuario, u.nombre, u.apellido
                FROM tareas_evento t
                JOIN eventos e ON e.id_evento = t.id_evento
                LEFT JOIN tarea_usuario_asignado a ON a.id_tarea = t.id_tarea
                LEFT JOIN usuarios u ON u.id_usuario = a.id_usuario
                ORDER BY t.fecha_limite
            """, fetch=True)
            for item in self.tree_tareas.get_children(): self.tree_tareas.delete(item)
            for tid, eid, etitulo, descripcion, limite, prioridad, estado, uid, nombre, apellido in rows:
                evento_txt = f"{etitulo} — #{eid}"
                limite_txt = limite.strftime("%Y-%m-%d %H:%M") if hasattr(limite, "strftime") else limite
                responsable_txt = f"{nombre} {apellido} — #{uid}" if uid is not None else "Sin responsable asignado"
                self.tree_tareas.insert("", "end", values=(tid, evento_txt, descripcion, limite_txt, prioridad, estado, responsable_txt))

            valores_ev = ["Seleccione un evento"] + list(self.eventos_combo.keys())
            valores_resp = ["Sin responsable asignado"] + list(self.usuarios_combo.keys())
            self.combo_tarea_evento.configure(values=valores_ev)
            self.combo_tarea_responsable.configure(values=valores_resp)
        except Exception as e:
            print(f"Error cargando tareas: {e}")

    def mostrar_tareas_vencidas(self):
        try:
            rows = self.ejecutar_consulta("""
                SELECT descripcion, fecha_limite, prioridad, estado, evento
                FROM vista_tareas_vencidas ORDER BY fecha_limite
            """, fetch=True)
            if not rows:
                return messagebox.showinfo("Tareas vencidas", "No hay tareas vencidas. ¡Buen trabajo!")
            texto = "\n".join(
                f"[{prioridad.upper()}] {desc}  (evento: {evento})  — venció {str(limite)[:16]}  — estado: {estado}"
                for desc, limite, prioridad, estado, evento in rows
            )
            messagebox.showwarning("Tareas vencidas", texto)
        except Exception as e:
            messagebox.showerror("No se pudo consultar", str(e))
    
    def actualizar_todas_las_tablas(self):
        self.cargar_datos_usuarios()
        self.cargar_datos_categorias()
        self.cargar_datos_ubicaciones()
        self.cargar_datos_eventos()
        self.cargar_datos_disponibilidad()
        self.cargar_datos_tareas()


if __name__ == "__main__":
    app = AppAgenda()
    app.mainloop()
