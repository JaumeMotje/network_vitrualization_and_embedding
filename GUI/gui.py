
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import numpy as np
import math
from tkinter import Canvas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Allocation.allocation import VirtualNetworkAllocation

class VirtualNetworkUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Network Dashboard")
        self.root.geometry("1200x800")

        # Variables principales
        self.num_nodes = tk.IntVar(value=5)
        self.num_demands = tk.IntVar(value=2)
        self.adjacency_matrix = []
        self.capacity_matrix = []
        self.demands = []

        # Variables para visualización
        self.show_capacities = tk.BooleanVar(value=True)
        self.show_demands = tk.BooleanVar(value=True)
        self.show_node_labels = tk.BooleanVar(value=True)
        self.node_positions = {}

        self.setup_dashboard()
        self.update_matrices()

    def setup_dashboard(self):
        # Frame principal con padding elegante
        main_frame = tk.Frame(self.root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Panel superior - Configuración con estilo minimalista
        control_frame = tk.Frame(main_frame, bg='#ffffff', relief='flat', bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 8))
        self.setup_control_panel(control_frame)

        # Panel central - Contenido principal
        content_frame = tk.Frame(main_frame, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Columna izquierda - Matrices con estilo limpio
        left_column = tk.Frame(content_frame, width=420,
                               bg='#ffffff', relief='flat', bd=1)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 8))
        left_column.pack_propagate(False)
        self.setup_matrices_panel(left_column)

        # Columna central - Visualización
        center_column = tk.Frame(
            content_frame, bg='#ffffff', relief='flat', bd=1)
        center_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
        self.setup_visualization_panel(center_column)

        # Columna derecha - Demandas y Resultados
        right_column = tk.Frame(content_frame, width=360,
                                bg='#ffffff', relief='flat', bd=1)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
        right_column.pack_propagate(False)
        self.setup_demands_results_panel(right_column)

    def setup_control_panel(self, parent):
        parent.configure(bg='#ffffff')

        # Panel de configuración con diseño limpio
        config_frame = tk.LabelFrame(parent, text="Network Configuration",
                                     font=("Segoe UI", 11, "normal"),
                                     bg='#ffffff', fg='#2c3e50',
                                     bd=0, relief='flat', padx=12, pady=8)
        config_frame.pack(fill=tk.X, padx=12, pady=8)

        # Configuración básica con espaciado elegante
        config_row = tk.Frame(config_frame, bg='#ffffff')
        config_row.pack(fill=tk.X, pady=4)

        # Estilo minimalista para controles
        tk.Label(config_row, text="Nodes:", font=("Segoe UI", 10),
                 bg='#ffffff', fg='#34495e').pack(side=tk.LEFT, padx=(0, 8))
        nodes_spin = ttk.Spinbox(config_row, from_=2, to=20, textvariable=self.num_nodes,
                                 command=self.update_matrices, width=6)
        nodes_spin.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(config_row, text="Demands:", font=("Segoe UI", 10),
                 bg='#ffffff', fg='#34495e').pack(side=tk.LEFT, padx=(0, 8))
        demands_spin = ttk.Spinbox(config_row, from_=1, to=50, textvariable=self.num_demands,
                                   command=self.update_demands, width=6)
        demands_spin.pack(side=tk.LEFT, padx=(0, 20))

        # Botones principales con estilo moderno
        btn_frame = tk.Frame(config_row, bg='#ffffff')
        btn_frame.pack(side=tk.RIGHT)

        # Configurar estilo de botones
        style = ttk.Style()
        style.configure('Modern.TButton', padding=(12, 6))

        ttk.Button(btn_frame, text="Update", command=self.update_matrices,
                   style='Modern.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Clear", command=self.clear_all,
                   style='Modern.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Example", command=self.load_example,
                   style='Modern.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Analyze", command=self.analyze_network,
                   style='Modern.TButton').pack(side=tk.LEFT, padx=3)

        # Separador sutil
        separator = tk.Frame(config_frame, height=1, bg='#ecf0f1')
        separator.pack(fill=tk.X, pady=8)

        # Opciones de visualización con diseño limpio
        viz_frame = tk.Frame(config_frame, bg='#ffffff')
        viz_frame.pack(fill=tk.X, pady=4)

        tk.Label(viz_frame, text="Display Options:", font=("Segoe UI", 10),
                 bg='#ffffff', fg='#34495e').pack(side=tk.LEFT, padx=(0, 12))

        ttk.Checkbutton(viz_frame, text="Capacities", variable=self.show_capacities,
                        command=self.update_visualization).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(viz_frame, text="Demands", variable=self.show_demands,
                        command=self.update_visualization).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(viz_frame, text="Node Labels", variable=self.show_node_labels,
                        command=self.update_visualization).pack(side=tk.LEFT, padx=8)

        # Otro separador
        separator2 = tk.Frame(config_frame, height=1, bg='#ecf0f1')
        separator2.pack(fill=tk.X, pady=8)

        # Botones de archivo con estado
        file_frame = tk.Frame(config_frame, bg='#ffffff')
        file_frame.pack(fill=tk.X, pady=4)

        # Estado con diseño moderno
        self.status_label = tk.Label(file_frame, text="Ready", font=("Segoe UI", 10),
                                     fg='#27ae60', bg='#ffffff')
        self.status_label.pack(side=tk.RIGHT, padx=12)

    def setup_matrices_panel(self, parent):
        parent.configure(bg='#ffffff')

        matrices_frame = tk.Frame(parent, bg='#ffffff')
        matrices_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Matriz de adyacencia con diseño limpio
        adj_frame = tk.LabelFrame(matrices_frame, text="Adjacency Matrix",
                                  font=("Segoe UI", 11, "normal"),
                                  bg='#ffffff', fg='#2c3e50', bd=0, relief='flat')
        adj_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Container con borde sutil
        adj_container = tk.Frame(adj_frame, bg='#f8f9fa', relief='solid', bd=1)
        adj_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        adj_canvas = tk.Canvas(adj_container, height=160,
                               bg='#ffffff', highlightthickness=0)
        adj_scrollbar_v = ttk.Scrollbar(
            adj_container, orient="vertical", command=adj_canvas.yview)
        adj_scrollbar_h = ttk.Scrollbar(
            adj_container, orient="horizontal", command=adj_canvas.xview)
        self.adj_scrollable_frame = tk.Frame(adj_canvas, bg='#ffffff')

        self.adj_scrollable_frame.bind("<Configure>",
                                       lambda e: adj_canvas.configure(scrollregion=adj_canvas.bbox("all")))

        adj_canvas.create_window(
            (0, 0), window=self.adj_scrollable_frame, anchor="nw")
        adj_canvas.configure(yscrollcommand=adj_scrollbar_v.set,
                             xscrollcommand=adj_scrollbar_h.set)

        adj_canvas.pack(side="left", fill="both", expand=True)
        adj_scrollbar_v.pack(side="right", fill="y")
        adj_scrollbar_h.pack(side="bottom", fill="x")

        # Matriz de capacidades con el mismo estilo
        cap_frame = tk.LabelFrame(matrices_frame, text="Capacity Matrix (Mbps)",
                                  font=("Segoe UI", 11, "normal"),
                                  bg='#ffffff', fg='#2c3e50', bd=0, relief='flat')
        cap_frame.pack(fill=tk.BOTH, expand=True)

        cap_container = tk.Frame(cap_frame, bg='#f8f9fa', relief='solid', bd=1)
        cap_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        cap_canvas = tk.Canvas(cap_container, height=160,
                               bg='#ffffff', highlightthickness=0)
        cap_scrollbar_v = ttk.Scrollbar(
            cap_container, orient="vertical", command=cap_canvas.yview)
        cap_scrollbar_h = ttk.Scrollbar(
            cap_container, orient="horizontal", command=cap_canvas.xview)
        self.cap_scrollable_frame = tk.Frame(cap_canvas, bg='#ffffff')

        self.cap_scrollable_frame.bind("<Configure>",
                                       lambda e: cap_canvas.configure(scrollregion=cap_canvas.bbox("all")))

        cap_canvas.create_window(
            (0, 0), window=self.cap_scrollable_frame, anchor="nw")
        cap_canvas.configure(yscrollcommand=cap_scrollbar_v.set,
                             xscrollcommand=cap_scrollbar_h.set)

        cap_canvas.pack(side="left", fill="both", expand=True)
        cap_scrollbar_v.pack(side="right", fill="y")
        cap_scrollbar_h.pack(side="bottom", fill="x")

    def setup_visualization_panel(self, parent):
        parent.configure(bg='#ffffff')

        viz_frame = tk.LabelFrame(parent, text="Network Visualization",
                                  font=("Segoe UI", 11, "normal"),
                                  bg='#ffffff', fg='#2c3e50', bd=0, relief='flat')
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Canvas de visualización con borde elegante
        canvas_container = tk.Frame(
            viz_frame, bg='#f8f9fa', relief='solid', bd=1)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        canvas_frame = tk.Frame(canvas_container, bg='#f8f9fa')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.viz_canvas = Canvas(canvas_frame, bg='#ffffff', width=500, height=420,
                                 highlightthickness=0, relief='flat')

        # Scrollbars con estilo
        v_scrollbar = ttk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=self.viz_canvas.yview)
        h_scrollbar = ttk.Scrollbar(
            canvas_frame, orient=tk.HORIZONTAL, command=self.viz_canvas.xview)

        self.viz_canvas.configure(
            yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.viz_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Botones de visualización con espaciado elegante
        btn_frame = tk.Frame(viz_frame, bg='#ffffff')
        btn_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        ttk.Button(btn_frame, text="Refresh View", command=self.update_visualization,
                   style='Modern.TButton').pack(side=tk.LEFT, padx=4)

    def setup_demands_results_panel(self, parent):
        parent.configure(bg='#ffffff')

        # Panel principal con espaciado
        main_panel = tk.Frame(parent, bg='#ffffff')
        main_panel.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Panel de demandas con diseño limpio
        demands_frame = tk.LabelFrame(main_panel, text="Traffic Demands",
                                      font=("Segoe UI", 11, "normal"),
                                      bg='#ffffff', fg='#2c3e50', bd=0, relief='flat')
        demands_frame.pack(fill=tk.X, pady=(0, 8))

        demands_container = tk.Frame(
            demands_frame, bg='#f8f9fa', relief='solid', bd=1)
        demands_container.pack(fill=tk.X, padx=8, pady=4)

        demands_canvas = tk.Canvas(
            demands_container, height=180, bg='#ffffff', highlightthickness=0)
        demands_scrollbar = ttk.Scrollbar(
            demands_container, orient="vertical", command=demands_canvas.yview)
        self.demand_scrollable_frame = tk.Frame(demands_canvas, bg='#ffffff')

        self.demand_scrollable_frame.bind("<Configure>",
                                          lambda e: demands_canvas.configure(scrollregion=demands_canvas.bbox("all")))

        demands_canvas.create_window(
            (0, 0), window=self.demand_scrollable_frame, anchor="nw")
        demands_canvas.configure(yscrollcommand=demands_scrollbar.set)

        demands_canvas.pack(side="left", fill="both",
                            expand=True, padx=2, pady=2)
        demands_scrollbar.pack(side="right", fill="y")

        # Panel de resultados con diseño moderno
        results_frame = tk.LabelFrame(main_panel, text="Analysis Results",
                                      font=("Segoe UI", 11, "normal"),
                                      bg='#ffffff', fg='#2c3e50', bd=0, relief='flat')
        results_frame.pack(fill=tk.BOTH, expand=True)

        results_container = tk.Frame(
            results_frame, bg='#f8f9fa', relief='solid', bd=1)
        results_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Text widget con fuente moderna
        self.result_text = tk.Text(results_container, height=16, width=48,
                                   font=("Consolas", 9), wrap=tk.WORD,
                                   bg='#ffffff', fg='#2c3e50', relief='flat',
                                   selectbackground='#3498db', selectforeground='#ffffff',
                                   insertbackground='#2c3e50', highlightthickness=0,
                                   padx=8, pady=6)

        result_scrollbar = ttk.Scrollbar(
            results_container, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.pack(side="left", fill="both",
                              expand=True, padx=2, pady=2)
        result_scrollbar.pack(side="right", fill="y")

        # Mensaje inicial con diseño limpio
        self.result_text.insert(tk.END, "Virtual Network Analysis Dashboard\n")
        self.result_text.insert(tk.END, "=" * 38 + "\n\n")
        self.result_text.insert(tk.END, "Getting Started:\n")
        self.result_text.insert(
            tk.END, "1. Configure network nodes and demands\n")
        self.result_text.insert(
            tk.END, "2. Set up adjacency and capacity matrices\n")
        self.result_text.insert(
            tk.END, "3. Define traffic demand parameters\n")
        self.result_text.insert(
            tk.END, "4. Click 'Analyze' to run optimization\n\n")
        self.result_text.insert(tk.END, "Ready for network configuration...")

    def update_matrices(self):
        n = self.num_nodes.get()
        self.status_label.config(text="Updating matrices...", fg='orange')
        self.root.update()

        for widget in self.adj_scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.cap_scrollable_frame.winfo_children():
            widget.destroy()

        self.adjacency_matrix = [[tk.IntVar() for _ in range(n)]
                                 for _ in range(n)]
        self.capacity_matrix = [[tk.DoubleVar() for _ in range(n)]
                                for _ in range(n)]

        # Matriz de adyacencia
        tk.Label(self.adj_scrollable_frame, text="Node",
                 font=("Arial", 9, "bold")).grid(row=0, column=0)

        for j in range(n):
            tk.Label(self.adj_scrollable_frame,
                     text=f"{j+1}", font=("Arial", 9, "bold")).grid(row=0, column=j+1)

        for i in range(n):
            tk.Label(self.adj_scrollable_frame,
                     text=f"{i+1}", font=("Arial", 9, "bold")).grid(row=i+1, column=0)
            for j in range(n):
                if i != j:
                    cb = ttk.Checkbutton(self.adj_scrollable_frame,
                                         variable=self.adjacency_matrix[i][j],
                                         command=lambda r=i, c=j: self.sync_adjacency(r, c))
                    cb.grid(row=i+1, column=j+1)
                else:
                    tk.Label(self.adj_scrollable_frame, text="—").grid(
                        row=i+1, column=j+1)

        # Matriz de capacidades
        tk.Label(self.cap_scrollable_frame, text="Node",
                 font=("Arial", 9, "bold")).grid(row=0, column=0)

        for j in range(n):
            tk.Label(self.cap_scrollable_frame,
                     text=f"{j+1}", font=("Arial", 9, "bold")).grid(row=0, column=j+1)

        for i in range(n):
            tk.Label(self.cap_scrollable_frame,
                     text=f"{i+1}", font=("Arial", 9, "bold")).grid(row=i+1, column=0)
            for j in range(n):
                if i != j:
                    entry = ttk.Entry(self.cap_scrollable_frame,
                                      textvariable=self.capacity_matrix[i][j],
                                      width=6)
                    entry.grid(row=i+1, column=j+1)
                else:
                    tk.Label(self.cap_scrollable_frame, text="—").grid(
                        row=i+1, column=j+1)

        self.update_demands()
        self.status_label.config(text="Ready", fg='green')

    def sync_adjacency(self, i, j):
        self.adjacency_matrix[j][i].set(self.adjacency_matrix[i][j].get())
        self.update_visualization()

    def update_demands(self):
        for widget in self.demand_scrollable_frame.winfo_children():
            widget.destroy()

        n_demands = self.num_demands.get()
        n_nodes = self.num_nodes.get()
        self.demands = []

        headers = ["#", "Source", "Dest", "Demand (Mbps)"]
        for col, header in enumerate(headers):
            tk.Label(self.demand_scrollable_frame, text=header,
                     font=("Arial", 9, "bold")).grid(row=0, column=col)

        for i in range(n_demands):
            demand_info = {
                'source': tk.IntVar(value=1),
                'dest': tk.IntVar(value=n_nodes),
                'demand': tk.DoubleVar(value=0.0)
            }

            tk.Label(self.demand_scrollable_frame,
                     text=f"{i+1}").grid(row=i+1, column=0)

            source_cb = ttk.Combobox(self.demand_scrollable_frame,
                                     textvariable=demand_info['source'],
                                     values=list(range(1, n_nodes+1)),
                                     width=6, state="readonly")
            source_cb.grid(row=i+1, column=1)

            dest_cb = ttk.Combobox(self.demand_scrollable_frame,
                                   textvariable=demand_info['dest'],
                                   values=list(range(1, n_nodes+1)),
                                   width=6, state="readonly")
            dest_cb.grid(row=i+1, column=2)

            demand_entry = ttk.Entry(self.demand_scrollable_frame,
                                     textvariable=demand_info['demand'],
                                     width=8)
            demand_entry.grid(row=i+1, column=3)

            self.demands.append(demand_info)

    def update_visualization(self):
        self.status_label.config(text="Updating visualization...", fg='orange')
        self.root.update()

        self.viz_canvas.delete("all")

        n = self.num_nodes.get()
        if n < 2:
            self.status_label.config(text="Need at least 2 nodes", fg='red')
            return

        canvas_width = 480
        canvas_height = 400
        margin = 60

        try:
            self.node_positions = self.calculate_layered_layout(
                n, canvas_width, canvas_height, margin)
        except:
            self.node_positions = self.calculate_simple_layout(
                n, canvas_width, canvas_height, margin)

        

        if hasattr(self, 'adjacency_matrix') and hasattr(self, 'capacity_matrix'):
            self.draw_edges()

        self.draw_nodes()

        if self.show_demands.get() and hasattr(self, 'demands'):
            self.draw_demands_text()

        self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        self.status_label.config(text="Ready", fg='green')



    

    def calculate_simple_layout(self, n, canvas_width, canvas_height, margin=50):
        """Layout simple que minimiza cruces de conexiones"""
        positions = {}
        
        # Área disponible
        traffic_space = 120
        available_height = canvas_height - traffic_space
        center_x = canvas_width // 2
        center_y = traffic_space + available_height // 2
        
        # Caso 1: Un solo nodo
        if n == 1:
            positions[0] = (center_x, center_y)
            return positions
        
        # Si no hay matriz de adyacencia, usar layout simple
        if not hasattr(self, 'adjacency_matrix'):
            return self._simple_grid_layout(n, canvas_width, canvas_height, margin)
        
        # Contar conexiones de cada nodo
        connections = {}
        for i in range(n):
            connections[i] = []
            for j in range(n):
                if (i < len(self.adjacency_matrix) and 
                    j < len(self.adjacency_matrix[i]) and
                    self.adjacency_matrix[i][j].get() == 1):
                    connections[i].append(j)
        
        # Detectar patrones específicos para evitar cruces
        
        # Patrón estrella: un nodo conectado a muchos otros
        degrees = [len(connections[i]) for i in range(n)]
        max_degree = max(degrees) if degrees else 0
        
        if max_degree >= n - 1:  # Nodo central conectado a casi todos
            center_node = degrees.index(max_degree)
            positions[center_node] = (center_x, center_y)
            
            # Otros nodos en círculo alrededor del centro
            other_nodes = [i for i in range(n) if i != center_node]
            radius = min(canvas_width, available_height) // 3
            
            for i, node in enumerate(other_nodes):
                angle = 2 * 3.14159 * i / len(other_nodes)
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[node] = (x, y)
            
            return positions
        
        # Patrón lineal: intentar detectar si es una cadena
        if self._is_chain_pattern(connections, n):
            return self._chain_layout(connections, n, canvas_width, canvas_height, margin)
        
        # Patrón circular: todos tienen exactamente 2 conexiones
        if all(len(connections[i]) == 2 for i in range(n)) and n > 2:
            radius = min(canvas_width, available_height) // 3
            for i in range(n):
                angle = 2 * 3.14159 * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[i] = (x, y)
            return positions
        
        # Para otros casos, usar layout circular (minimiza cruces en grafos densos)
        if n <= 10:
            radius = min(canvas_width, available_height) // 3
            for i in range(n):
                angle = 2 * 3.14159 * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                positions[i] = (x, y)
            return positions
        
        # Para muchos nodos, usar cuadrícula ordenada por conexiones
        return self._ordered_grid_layout(connections, n, canvas_width, canvas_height, margin)

    def _is_chain_pattern(self, connections, n):
        """Detecta si el grafo es una cadena (línea)"""
        # Una cadena tiene exactamente 2 nodos con 1 conexión (extremos)
        # y el resto con exactamente 2 conexiones
        degrees = [len(connections[i]) for i in range(n)]
        return degrees.count(1) == 2 and degrees.count(2) == n - 2

    def _chain_layout(self, connections, n, canvas_width, canvas_height, margin):
        """Layout en línea para cadenas"""
        positions = {}
        
        # Encontrar un extremo de la cadena
        start_node = None
        for i in range(n):
            if len(connections[i]) == 1:
                start_node = i
                break
        
        if start_node is None:
            return self._simple_grid_layout(n, canvas_width, canvas_height, margin)
        
        # Seguir la cadena desde el extremo
        chain_order = [start_node]
        current = start_node
        visited = {start_node}
        
        while len(chain_order) < n:
            next_node = None
            for neighbor in connections[current]:
                if neighbor not in visited:
                    next_node = neighbor
                    break
            
            if next_node is None:
                break
                
            chain_order.append(next_node)
            visited.add(next_node)
            current = next_node
        
        # Posicionar nodos en línea horizontal
        if len(chain_order) > 1:
            step = (canvas_width - 2 * margin) / (len(chain_order) - 1)
            y = canvas_height // 2 + 60  # Un poco abajo del centro
            
            for i, node in enumerate(chain_order):
                x = margin + i * step
                positions[node] = (x, y)
        else:
            positions[chain_order[0]] = (canvas_width // 2, canvas_height // 2 + 60)
        
        return positions

    def _ordered_grid_layout(self, connections, n, canvas_width, canvas_height, margin):
        """Layout de cuadrícula ordenado por número de conexiones"""
        # Ordenar nodos por número de conexiones (más conectados primero)
        nodes_by_degree = sorted(range(n), key=lambda x: len(connections[x]), reverse=True)
        
        cols = int(math.sqrt(n)) + 1
        rows = (n + cols - 1) // cols
        
        spacing_x = (canvas_width - 2 * margin) // max(1, cols - 1) if cols > 1 else 0
        spacing_y = (canvas_height - 180 - 2 * margin) // max(1, rows - 1) if rows > 1 else 0
        
        start_x = margin if cols > 1 else canvas_width // 2
        start_y = 120 + margin if rows > 1 else canvas_height // 2 + 60
        
        positions = {}
        for i, node in enumerate(nodes_by_degree):
            row = i // cols
            col = i % cols
            
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            positions[node] = (x, y)
        
        return positions

    def _simple_grid_layout(self, n, canvas_width, canvas_height, margin):
        """Layout de cuadrícula simple sin análisis de conexiones"""
        positions = {}
        cols = int(math.sqrt(n)) + 1
        rows = (n + cols - 1) // cols
        
        spacing_x = (canvas_width - 2 * margin) // max(1, cols - 1) if cols > 1 else 0
        spacing_y = (canvas_height - 180 - 2 * margin) // max(1, rows - 1) if rows > 1 else 0
        
        start_x = margin if cols > 1 else canvas_width // 2
        start_y = 120 + margin if rows > 1 else canvas_height // 2 + 60
        
        for i in range(n):
            row = i // cols
            col = i % cols
            
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            positions[i] = (x, y)
        
        return positions


    def draw_edges(self):
        n = self.num_nodes.get()

        for i in range(n):
            for j in range(n):
                if i != j and (i < len(self.adjacency_matrix) and
                            j < len(self.adjacency_matrix[i]) and
                            self.adjacency_matrix[i][j].get() == 1):

                    x1, y1 = self.node_positions[i]
                    x2, y2 = self.node_positions[j]

                    capacity = 0
                    if (i < len(self.capacity_matrix) and
                            j < len(self.capacity_matrix[i])):
                        capacity = self.capacity_matrix[i][j].get()

                    if capacity > 0:
                        width = max(2, min(8, int(capacity / 2)))
                        color = self.get_capacity_color(capacity)
                    else:
                        width = 1
                        color = "gray"

                    # Verificar si existe conexión bidireccional
                    bidirectional = (j < len(self.adjacency_matrix) and
                                i < len(self.adjacency_matrix[j]) and
                                self.adjacency_matrix[j][i].get() == 1)

                    # Calcular offset para separar las líneas bidireccionales
                    offset = 8 if bidirectional else 0  # Aumentar offset para mejor visualización

                    # Calcular vector perpendicular para el offset
                    dx = x2 - x1
                    dy = y2 - y1
                    length = max(1, (dx*dx + dy*dy)**0.5)

                    # Vector perpendicular normalizado
                    perp_x = -dy / length * offset
                    perp_y = dx / length * offset

                    # Para conexiones bidireccionales, aplicar offset en direcciones opuestas
                    if bidirectional:
                        # Para la arista i->j, desplazar hacia un lado
                        offset_x1 = x1 + perp_x
                        offset_y1 = y1 + perp_y
                        offset_x2 = x2 + perp_x
                        offset_y2 = y2 + perp_y
                    else:
                        # Para conexiones unidireccionales, sin offset
                        offset_x1 = x1
                        offset_y1 = y1
                        offset_x2 = x2
                        offset_y2 = y2

                    # Acortar la línea para que la flecha no se superponga con el nodo
                    # Calcular el radio del nodo (asumiendo radio de 15 píxeles)
                    node_radius = 15
                    
                    # Acortar el final de la línea
                    line_dx = offset_x2 - offset_x1
                    line_dy = offset_y2 - offset_y1
                    line_length = max(1, (line_dx*line_dx + line_dy*line_dy)**0.5)
                    
                    # Normalizar y acortar
                    unit_x = line_dx / line_length
                    unit_y = line_dy / line_length
                    
                    final_x2 = offset_x2 - unit_x * node_radius
                    final_y2 = offset_y2 - unit_y * node_radius
                    final_x1 = offset_x1 + unit_x * node_radius

                    # Dibujar la línea con flecha
                    self.viz_canvas.create_line(final_x1, offset_y1 + unit_y * node_radius, 
                                            final_x2, final_y2,
                                            fill=color, width=width,
                                            arrow="last", 
                                            arrowshape=(12, 15, 4))  # Flecha más visible

                    # Mostrar capacidad si está habilitado
                    if self.show_capacities.get() and capacity > 0:
                        mid_x = (offset_x1 + offset_x2) / 2
                        mid_y = (offset_y1 + offset_y2) / 2

                        text_id = self.viz_canvas.create_text(mid_x, mid_y,
                                                            text=f"{capacity:.0f}",
                                                            font=("Arial", 8, "bold"),
                                                            fill="black")

                        bbox = self.viz_canvas.bbox(text_id)
                        if bbox:
                            self.viz_canvas.create_rectangle(bbox[0]-2, bbox[1]-1,
                                                            bbox[2]+2, bbox[3]+1,
                                                            fill="white", outline="gray")

                        self.viz_canvas.tag_raise(text_id)

    def draw_demands_text(self):
        if not hasattr(self, 'demands'):
            return

        start_x = 50
        start_y = 50
        line_height = 20

        self.viz_canvas.create_text(start_x, start_y,
                                    text="TRAFFIC DEMANDS:",
                                    font=("Arial", 12, "bold"),
                                    anchor="w")

        current_y = start_y + 30
        demand_count = 0

        colors = ["red", "blue", "green", "purple",
                  "orange", "brown", "pink", "cyan"]

        for idx, demand in enumerate(self.demands):
            if demand['demand'].get() > 0:
                src = demand['source'].get()
                dst = demand['dest'].get()
                dem_value = demand['demand'].get()

                color = colors[demand_count % len(colors)]

                demand_text = f"D{demand_count + 1}: Node {src} → Node {dst} = {dem_value:.0f} Mbps"

                self.viz_canvas.create_text(start_x, current_y,
                                            text=demand_text,
                                            font=("Arial", 10, "bold"),
                                            fill=color, anchor="w")

                current_y += line_height
                demand_count += 1

        if demand_count == 0:
            self.viz_canvas.create_text(start_x, current_y,
                                        text="No demands configured",
                                        font=("Arial", 10, "italic"),
                                        fill="gray", anchor="w")

    def draw_nodes(self):
        n = self.num_nodes.get()
        node_radius = 25

        for i in range(n):
            x, y = self.node_positions[i]

            self.viz_canvas.create_oval(x - node_radius, y - node_radius,
                                        x + node_radius, y + node_radius,
                                        fill="lightblue", outline="navy", width=2)

            if self.show_node_labels.get():
                self.viz_canvas.create_text(x, y, text=str(i + 1),
                                            font=("Arial", 12, "bold"),
                                            fill="navy")

    def get_capacity_color(self, capacity):
        if capacity >= 10:
            return "darkgreen"
        elif capacity >= 7:
            return "green"
        elif capacity >= 5:
            return "orange"
        else:
            return "red"

    def clear_all(self):
        for i in range(len(self.adjacency_matrix)):
            for j in range(len(self.adjacency_matrix[i])):
                self.adjacency_matrix[i][j].set(0)
                self.capacity_matrix[i][j].set(0.0)

        for demand in self.demands:
            demand['demand'].set(0.0)

        self.result_text.delete(1.0, tk.END)

    def load_example(self):
        self.num_nodes.set(5)
        self.num_demands.set(2)
        self.update_matrices()

        connections = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)]
        for i, j in connections:
            self.adjacency_matrix[i][j].set(1)
            self.adjacency_matrix[j][i].set(1)

        capacities = {(0, 1): 12, (1, 2): 10, (1, 3): 7, (2, 4): 8, (3, 4): 6}
        for (i, j), cap in capacities.items():
            self.capacity_matrix[i][j].set(cap)
            self.capacity_matrix[j][i].set(cap)

        self.demands[0]['source'].set(1)
        self.demands[0]['dest'].set(5)
        self.demands[0]['demand'].set(8)

        self.demands[1]['source'].set(1)
        self.demands[1]['dest'].set(5)
        self.demands[1]['demand'].set(4)

        self.update_visualization()

    def analyze_network(self):
        try:
            self.result_text.delete(1.0, tk.END)

            n = self.num_nodes.get()

            adj_matrix = np.array(
                [[self.adjacency_matrix[i][j].get() for j in range(n)] for i in range(n)])
            cap_matrix = np.array(
                [[self.capacity_matrix[i][j].get() for j in range(n)] for i in range(n)])

            capacity_adjacency_matrix = []
            for i in range(n):
                row = []
                for j in range(n):
                    if adj_matrix[i][j] == 1:
                        row.append(cap_matrix[i][j])
                    else:
                        row.append(0)
                capacity_adjacency_matrix.append(row)

            demands_list = []
            for i, demand in enumerate(self.demands):
                src = demand['source'].get() - 1
                dst = demand['dest'].get() - 1
                dem = demand['demand'].get()

                if dem > 0:
                    demands_list.append([src, dst, dem])

            if not demands_list:
                self.result_text.insert(
                    tk.END, "WARNING: No active demands to process\n")
                messagebox.showinfo(
                    "Information", "No active demands to process")
                return None

            # Header
            self.result_text.insert(
                tk.END, "VIRTUAL NETWORK ANALYSIS REPORT\n")
            self.result_text.insert(tk.END, "="*60 + "\n\n")

            network_data = {
                'capacity_matrix': capacity_adjacency_matrix,
                'demands': demands_list
            }

            self.result_text.insert(
                tk.END, "Initializing allocation algorithm...\n")
            self.root.update()

            allocator = VirtualNetworkAllocation(network_data)

            # Network Initial Status
            initial_status = allocator.get_network_status()
            self.result_text.insert(tk.END, "\nNETWORK CONFIGURATION\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")
            self.result_text.insert(
                tk.END, f"Number of nodes:          {allocator.num_nodes}\n")
            self.result_text.insert(
                tk.END, f"Number of links:          {allocator.total_links}\n")
            self.result_text.insert(
                tk.END, f"Total capacity:           {allocator.total_capacity:.2f} Mbps\n")
            self.result_text.insert(
                tk.END, f"Total demand:             {allocator.total_demand:.2f} Mbps\n")
            self.result_text.insert(
                tk.END, f"Network connectivity:     {'Connected' if allocator.network_connected else 'Disconnected'}\n")
            self.result_text.insert(
                tk.END, f"Number of demands:        {initial_status['total_demands']}\n")

            if not allocator.network_connected:
                self.result_text.insert(
                    tk.END, "\nWARNING: Network topology is not fully connected\n")
                self.result_text.insert(
                    tk.END, "Some demands may not be satisfiable due to connectivity issues.\n")
                messagebox.showwarning(
                    "Network Warning", "Network topology is not fully connected")

            # Capacity vs Demand Analysis
            capacity_utilization = min(
                allocator.total_demand / allocator.total_capacity * 100, 100) if allocator.total_capacity > 0 else 0
            self.result_text.insert(
                tk.END, f"Initial capacity usage:   {capacity_utilization:.1f}%\n")

            if capacity_utilization > 100:
                self.result_text.insert(
                    tk.END, "WARNING: Total demand exceeds total network capacity\n")

            self.result_text.insert(
                tk.END, "\nEXECUTING OPTIMAL ALLOCATION ALGORITHM\n")
            self.result_text.insert(tk.END, "-" * 40 + "\n")
            self.result_text.insert(
                tk.END, "Status: Processing... Please wait\n\n")
            self.root.update()

            result = allocator.offline_brute_force_allocation()

            if result['success']:
                # Main Results Section
                self.result_text.insert(tk.END, "ALLOCATION RESULTS\n")
                self.result_text.insert(tk.END, "=" * 40 + "\n")
                self.result_text.insert(
                    tk.END, f"Acceptance ratio:         {result['acceptance_ratio']:.2%}\n")
                self.result_text.insert(
                    tk.END, f"Revenue/cost ratio:       {result['revenue_cost_ratio']:.2f}\n")
                self.result_text.insert(
                    tk.END, f"Total revenue:            {result['total_revenue']:.2f}\n")
                self.result_text.insert(
                    tk.END, f"Total operating costs:    {result['total_cost']:.2f}\n")
                self.result_text.insert(
                    tk.END, f"Net profit:               {result['total_revenue'] - result['total_cost']:.2f}\n")
                self.result_text.insert(
                    tk.END, f"Allocated demands:        {len(result['allocated_demands'])}\n")
                self.result_text.insert(
                    tk.END, f"Rejected demands:         {len(result['rejected_demands'])}\n")

                # Algorithm Performance Metrics
                self.result_text.insert(tk.END, f"\nALGORITHM PERFORMANCE\n")
                self.result_text.insert(tk.END, "-" * 25 + "\n")
                self.result_text.insert(
                    tk.END, f"Total combinations evaluated: {result['total_combinations_evaluated']}\n")
                self.result_text.insert(
                    tk.END, f"Valid combinations found:     {result['valid_combinations']}\n")

                # Detailed Allocation Information
                if result.get('allocation_details'):
                    self.result_text.insert(tk.END, "\nALLOCATION DETAILS\n")
                    self.result_text.insert(tk.END, "-" * 30 + "\n")

                    for i, detail in enumerate(result['allocation_details']):
                        path_str = " -> ".join([str(node+1)
                                               for node in detail['path']])

                        self.result_text.insert(
                            tk.END, f"\nDemand {detail['demand_index']+1}:\n")
                        self.result_text.insert(
                            tk.END, f"  Source node:        {detail['source']+1}\n")
                        self.result_text.insert(
                            tk.END, f"  Destination node:   {detail['destination']+1}\n")
                        self.result_text.insert(
                            tk.END, f"  Bandwidth required: {detail['bandwidth']:.2f} Mbps\n")
                        self.result_text.insert(
                            tk.END, f"  Allocated path:     {path_str}\n")
                        self.result_text.insert(
                            tk.END, f"  Path length:        {len(detail['path'])-1} hops\n")
                        self.result_text.insert(
                            tk.END, f"  Operating cost:     {detail['cost']:.2f}\n")
                        self.result_text.insert(
                            tk.END, f"  Generated revenue:  {detail['revenue']:.2f}\n")
                        

                # Rejected Demands Analysis
                if result['rejected_demands']:
                    self.result_text.insert(
                        tk.END, "\nREJECTED DEMANDS ANALYSIS\n")
                    self.result_text.insert(tk.END, "-" * 35 + "\n")
                    total_rejected_bandwidth = 0
                    total_lost_revenue = 0

                    for i, rejected in enumerate(result['rejected_demands']):
                        demand_info = demands_list[rejected]
                        rejected_bandwidth = demand_info[2]
                        estimated_revenue = rejected_bandwidth * 1.5  # Assuming revenue factor
                        total_rejected_bandwidth += rejected_bandwidth
                        total_lost_revenue += estimated_revenue

                        self.result_text.insert(
                            tk.END, f"Demand {rejected+1}: ")
                        self.result_text.insert(
                            tk.END, f"Node {demand_info[0]+1} -> Node {demand_info[1]+1}, ")
                        self.result_text.insert(
                            tk.END, f"{rejected_bandwidth:.2f} Mbps")
                        self.result_text.insert(
                            tk.END, f" (Est. lost revenue: ${estimated_revenue:.2f})\n")

                    self.result_text.insert(tk.END, f"\nRejection Summary:\n")
                    self.result_text.insert(
                        tk.END, f"  Total rejected bandwidth: {total_rejected_bandwidth:.2f} Mbps\n")
                    self.result_text.insert(
                        tk.END, f"  Estimated lost revenue:   ${total_lost_revenue:.2f}\n")
                    self.result_text.insert(
                        tk.END, f"  Primary cause: Insufficient network capacity\n")

                
                self.result_text.see(tk.END)

                # Professional summary dialog
                summary = (f"Network Analysis Summary\n\n"
                           f"Acceptance Ratio: {result['acceptance_ratio']:.2%}\n"
                           f"Allocated Demands: {len(result['allocated_demands'])}\n"
                           f"Rejected Demands: {len(result['rejected_demands'])}\n"
                           f"Revenue/Cost Ratio: {result['revenue_cost_ratio']:.2f}\n")

                messagebox.showinfo("Analysis Complete", summary)

                return {
                    'capacity_matrix': capacity_adjacency_matrix,
                    'demands': demands_list,
                    'allocation_result': result,
                    'allocator': allocator
                }

            else:
                # Error handling with professional formatting
                error_msg = result.get('message', 'Unknown allocation error')
                self.result_text.insert(tk.END, "ALLOCATION ERROR REPORT\n")
                self.result_text.insert(tk.END, "=" * 35 + "\n")
                self.result_text.insert(
                    tk.END, f"Error Description: {error_msg}\n\n")

                self.result_text.insert(tk.END, "DIAGNOSTIC INFORMATION\n")
                self.result_text.insert(tk.END, "-" * 30 + "\n")
                self.result_text.insert(tk.END, "Possible causes:\n")
                self.result_text.insert(
                    tk.END, "• Network topology is not fully connected\n")
                self.result_text.insert(
                    tk.END, "• Insufficient link capacities for demand requirements\n")
                self.result_text.insert(
                    tk.END, "• Invalid network configuration parameters\n")
                self.result_text.insert(
                    tk.END, "• Demand specifications exceed network capabilities\n\n")

                self.result_text.insert(tk.END, "RECOMMENDED ACTIONS\n")
                self.result_text.insert(tk.END, "-" * 25 + "\n")
                self.result_text.insert(
                    tk.END, "1. Verify all nodes are properly connected\n")
                self.result_text.insert(
                    tk.END, "2. Check that link capacities are sufficient\n")
                self.result_text.insert(
                    tk.END, "3. Validate demand parameters\n")
                self.result_text.insert(
                    tk.END, "4. Review network topology for bottlenecks\n")

                self.result_text.see(tk.END)
                messagebox.showerror(
                    "Allocation Error", f"Network allocation failed:\n\n{error_msg}")
                return None

        except Exception as e:
            error_msg = f"Critical system error: {str(e)}"

            self.result_text.insert(tk.END, "CRITICAL ERROR REPORT\n")
            self.result_text.insert(tk.END, "=" * 30 + "\n")
            self.result_text.insert(tk.END, f"Error Details: {error_msg}\n\n")

            self.result_text.insert(tk.END, "SYSTEM DIAGNOSTIC\n")
            self.result_text.insert(tk.END, "-" * 20 + "\n")
            self.result_text.insert(tk.END, "Please verify the following:\n")
            self.result_text.insert(
                tk.END, "• Network configuration is complete and valid\n")
            self.result_text.insert(
                tk.END, "• All matrix entries contain valid numerical values\n")
            self.result_text.insert(
                tk.END, "• Demand specifications are properly formatted\n")
            self.result_text.insert(
                tk.END, "• System has sufficient resources for computation\n")

            self.result_text.see(tk.END)
            messagebox.showerror("Critical Error", error_msg)
            return None

    def get_current_timestamp(self):
        """Helper method to get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def has_path(self, adj_matrix, src, dst):
        """Verificar si existe un camino entre dos nodos usando BFS"""
        n = len(adj_matrix)
        visited = [False] * n
        queue = [src]
        visited[src] = True

        while queue:
            node = queue.pop(0)
            if node == dst:
                return True

            for neighbor in range(n):
                if adj_matrix[node][neighbor] and not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)

        return False


def main():
    root = tk.Tk()
    app = VirtualNetworkUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
