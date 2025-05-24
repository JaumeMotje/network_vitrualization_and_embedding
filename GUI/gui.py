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
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel superior - Configuración
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        self.setup_control_panel(control_frame)
        
        # Panel central - Contenido principal
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda - Matrices
        left_column = tk.Frame(content_frame, width=400)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_column.pack_propagate(False)
        self.setup_matrices_panel(left_column)
        
        # Columna central - Visualización
        center_column = tk.Frame(content_frame)
        center_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.setup_visualization_panel(center_column)
        
        # Columna derecha - Demandas y Resultados
        right_column = tk.Frame(content_frame, width=350)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_column.pack_propagate(False)
        self.setup_demands_results_panel(right_column)
    
    def setup_control_panel(self, parent):
        # Panel de configuración
        config_frame = tk.LabelFrame(parent, text="Network Configuration", 
                                   font=("Arial", 10), padx=5, pady=5)
        config_frame.pack(fill=tk.X)
        
        # Configuración básica
        config_row = tk.Frame(config_frame)
        config_row.pack(fill=tk.X, pady=2)
        
        tk.Label(config_row, text="Nodes:").pack(side=tk.LEFT, padx=(0, 5))
        nodes_spin = ttk.Spinbox(config_row, from_=2, to=20, textvariable=self.num_nodes, 
                                command=self.update_matrices, width=5)
        nodes_spin.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(config_row, text="Demands:").pack(side=tk.LEFT, padx=(0, 5))
        demands_spin = ttk.Spinbox(config_row, from_=1, to=50, textvariable=self.num_demands,
                                  command=self.update_demands, width=5)
        demands_spin.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botones principales
        btn_frame = tk.Frame(config_row)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Update", command=self.update_matrices).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Example", command=self.load_example).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Analyze", command=self.analyze_network).pack(side=tk.LEFT, padx=2)
        
        # Opciones de visualización
        viz_frame = tk.Frame(config_frame)
        viz_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(viz_frame, text="Show:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(viz_frame, text="Capacities", variable=self.show_capacities,
                       command=self.update_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(viz_frame, text="Demands", variable=self.show_demands,
                       command=self.update_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(viz_frame, text="Labels", variable=self.show_node_labels,
                       command=self.update_visualization).pack(side=tk.LEFT, padx=2)
        
        # Botones de archivo
        file_frame = tk.Frame(config_frame)
        file_frame.pack(fill=tk.X, pady=(2, 0))
        
        ttk.Button(file_frame, text="Save", command=self.save_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Load", command=self.load_config).pack(side=tk.LEFT, padx=2)
        
        # Estado
        self.status_label = tk.Label(file_frame, text="Ready", fg='green')
        self.status_label.pack(side=tk.RIGHT, padx=5)
    
    def setup_matrices_panel(self, parent):
        matrices_frame = tk.Frame(parent)
        matrices_frame.pack(fill=tk.BOTH, expand=True)
        
        # Matriz de adyacencia
        adj_frame = tk.LabelFrame(matrices_frame, text="Adjacency Matrix", font=("Arial", 10))
        adj_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        adj_canvas = tk.Canvas(adj_frame, height=150)
        adj_scrollbar_v = ttk.Scrollbar(adj_frame, orient="vertical", command=adj_canvas.yview)
        adj_scrollbar_h = ttk.Scrollbar(adj_frame, orient="horizontal", command=adj_canvas.xview)
        self.adj_scrollable_frame = tk.Frame(adj_canvas)
        
        self.adj_scrollable_frame.bind("<Configure>",
            lambda e: adj_canvas.configure(scrollregion=adj_canvas.bbox("all")))
        
        adj_canvas.create_window((0, 0), window=self.adj_scrollable_frame, anchor="nw")
        adj_canvas.configure(yscrollcommand=adj_scrollbar_v.set, xscrollcommand=adj_scrollbar_h.set)
        
        adj_canvas.pack(side="left", fill="both", expand=True)
        adj_scrollbar_v.pack(side="right", fill="y")
        adj_scrollbar_h.pack(side="bottom", fill="x")
        
        # Matriz de capacidades
        cap_frame = tk.LabelFrame(matrices_frame, text="Capacity Matrix (Mbps)", font=("Arial", 10))
        cap_frame.pack(fill=tk.BOTH, expand=True)
        
        cap_canvas = tk.Canvas(cap_frame, height=150)
        cap_scrollbar_v = ttk.Scrollbar(cap_frame, orient="vertical", command=cap_canvas.yview)
        cap_scrollbar_h = ttk.Scrollbar(cap_frame, orient="horizontal", command=cap_canvas.xview)
        self.cap_scrollable_frame = tk.Frame(cap_canvas)
        
        self.cap_scrollable_frame.bind("<Configure>",
            lambda e: cap_canvas.configure(scrollregion=cap_canvas.bbox("all")))
        
        cap_canvas.create_window((0, 0), window=self.cap_scrollable_frame, anchor="nw")
        cap_canvas.configure(yscrollcommand=cap_scrollbar_v.set, xscrollcommand=cap_scrollbar_h.set)
        
        cap_canvas.pack(side="left", fill="both", expand=True)
        cap_scrollbar_v.pack(side="right", fill="y")
        cap_scrollbar_h.pack(side="bottom", fill="x")
    
    def setup_visualization_panel(self, parent):
        viz_frame = tk.LabelFrame(parent, text="Network Visualization", font=("Arial", 10))
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas de visualización
        canvas_frame = tk.Frame(viz_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.viz_canvas = Canvas(canvas_frame, bg='white', width=480, height=400)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.viz_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.viz_canvas.xview)
        
        self.viz_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.viz_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Botones de visualización
        btn_frame = tk.Frame(viz_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="Update View", command=self.update_visualization).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save Image", command=self.save_visualization).pack(side=tk.LEFT, padx=2)
    
    def setup_demands_results_panel(self, parent):
        # Panel de demandas
        demands_frame = tk.LabelFrame(parent, text="Traffic Demands", font=("Arial", 10))
        demands_frame.pack(fill=tk.X, pady=(0, 5))
        
        demands_canvas = tk.Canvas(demands_frame, height=180)
        demands_scrollbar = ttk.Scrollbar(demands_frame, orient="vertical", command=demands_canvas.yview)
        self.demand_scrollable_frame = tk.Frame(demands_canvas)
        
        self.demand_scrollable_frame.bind("<Configure>",
            lambda e: demands_canvas.configure(scrollregion=demands_canvas.bbox("all")))
        
        demands_canvas.create_window((0, 0), window=self.demand_scrollable_frame, anchor="nw")
        demands_canvas.configure(yscrollcommand=demands_scrollbar.set)
        
        demands_canvas.pack(side="left", fill="both", expand=True)
        demands_scrollbar.pack(side="right", fill="y")
        
        # Panel de resultados
        results_frame = tk.LabelFrame(parent, text="Analysis Results", font=("Arial", 10))
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = tk.Text(results_frame, height=15, width=45, font=("Consolas", 9),
                                 wrap=tk.WORD)
        result_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")
        
        # Mensaje inicial
        self.result_text.insert(tk.END, "Virtual Network Dashboard\n")
        self.result_text.insert(tk.END, "="*30 + "\n\n")
        self.result_text.insert(tk.END, "1. Set nodes and demands\n")
        self.result_text.insert(tk.END, "2. Configure matrices\n")
        self.result_text.insert(tk.END, "3. Define traffic demands\n")
        self.result_text.insert(tk.END, "4. Click 'Analyze' for results\n")
    
    # Resto de los métodos permanecen iguales (update_matrices, sync_adjacency, update_demands, etc.)
    # Solo se han modificado los métodos de configuración de la interfaz
    
    def update_matrices(self):
        n = self.num_nodes.get()
        self.status_label.config(text="Updating matrices...", fg='orange')
        self.root.update()
        
        for widget in self.adj_scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.cap_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.adjacency_matrix = [[tk.IntVar() for _ in range(n)] for _ in range(n)]
        self.capacity_matrix = [[tk.DoubleVar() for _ in range(n)] for _ in range(n)]
        
        # Matriz de adyacencia
        tk.Label(self.adj_scrollable_frame, text="Node", font=("Arial", 9, "bold")).grid(row=0, column=0)
        
        for j in range(n):
            tk.Label(self.adj_scrollable_frame, text=f"{j+1}", font=("Arial", 9, "bold")).grid(row=0, column=j+1)
        
        for i in range(n):
            tk.Label(self.adj_scrollable_frame, text=f"{i+1}", font=("Arial", 9, "bold")).grid(row=i+1, column=0)
            for j in range(n):
                if i != j:
                    cb = ttk.Checkbutton(self.adj_scrollable_frame, 
                                       variable=self.adjacency_matrix[i][j],
                                       command=lambda r=i, c=j: self.sync_adjacency(r, c))
                    cb.grid(row=i+1, column=j+1)
                else:
                    tk.Label(self.adj_scrollable_frame, text="—").grid(row=i+1, column=j+1)
        
        # Matriz de capacidades
        tk.Label(self.cap_scrollable_frame, text="Node", font=("Arial", 9, "bold")).grid(row=0, column=0)
        
        for j in range(n):
            tk.Label(self.cap_scrollable_frame, text=f"{j+1}", font=("Arial", 9, "bold")).grid(row=0, column=j+1)
        
        for i in range(n):
            tk.Label(self.cap_scrollable_frame, text=f"{i+1}", font=("Arial", 9, "bold")).grid(row=i+1, column=0)
            for j in range(n):
                if i != j:
                    entry = ttk.Entry(self.cap_scrollable_frame, 
                                    textvariable=self.capacity_matrix[i][j], 
                                    width=6)
                    entry.grid(row=i+1, column=j+1)
                else:
                    tk.Label(self.cap_scrollable_frame, text="—").grid(row=i+1, column=j+1)
        
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
            tk.Label(self.demand_scrollable_frame, text=header, font=("Arial", 9, "bold")).grid(row=0, column=col)
        
        for i in range(n_demands):
            demand_info = {
                'source': tk.IntVar(value=1),
                'dest': tk.IntVar(value=n_nodes),
                'demand': tk.DoubleVar(value=0.0)
            }
            
            tk.Label(self.demand_scrollable_frame, text=f"{i+1}").grid(row=i+1, column=0)
            
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
            self.node_positions = self.calculate_layered_layout(n, canvas_width, canvas_height, margin)
        except:
            self.node_positions = self.calculate_simple_horizontal_layout(n, canvas_width, canvas_height, margin)
        
        self.draw_grid()
        
        if hasattr(self, 'adjacency_matrix') and hasattr(self, 'capacity_matrix'):
            self.draw_edges()
        
        self.draw_nodes()
        
        if self.show_demands.get() and hasattr(self, 'demands'):
            self.draw_demands_text()
        
        self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
        self.status_label.config(text="Ready", fg='green')
    
    def draw_grid(self):
        canvas_width = 480
        canvas_height = 400
        
        for x in range(0, canvas_width, 40):
            self.viz_canvas.create_line(x, 0, x, canvas_height, fill='#f0f0f0', width=1)
        
        for y in range(0, canvas_height, 40):
            self.viz_canvas.create_line(0, y, canvas_width, y, fill='#f0f0f0', width=1)
    
    def calculate_simple_horizontal_layout(self, n, canvas_width, canvas_height, margin):
        positions = {}
        if n > 1:
            spacing = (canvas_width - 2 * margin) / (n - 1)
            y_center = canvas_height // 2
            
            for i in range(n):
                x = margin + i * spacing
                y = y_center
                positions[i] = (x, y)
        else:
            positions[0] = (canvas_width // 2, canvas_height // 2)
        return positions
    
    def calculate_layered_layout(self, n, canvas_width, canvas_height, margin):
        if not hasattr(self, 'adjacency_matrix') or n < 2:
            return self.calculate_simple_horizontal_layout(n, canvas_width, canvas_height, margin)
        
        graph = {}
        for i in range(n):
            graph[i] = []
            for j in range(n):
                if (i < len(self.adjacency_matrix) and 
                    j < len(self.adjacency_matrix[i]) and
                    self.adjacency_matrix[i][j].get() == 1):
                    graph[i].append(j)
        
        node_degrees = {i: len(graph[i]) for i in range(n)}
        unique_degrees = set(node_degrees.values())
        
        if len(unique_degrees) <= 2:
            return self.calculate_simple_horizontal_layout(n, canvas_width, canvas_height, margin)
        
        layers = self.organize_nodes_into_layers(graph, node_degrees, n)
        
        positions = {}
        layer_width = (canvas_width - 2 * margin) / max(1, len(layers) - 1) if len(layers) > 1 else 0
        
        for layer_idx, layer_nodes in enumerate(layers):
            if len(layers) == 1:
                x = canvas_width // 2
            else:
                x = margin + layer_idx * layer_width
            
            if len(layer_nodes) == 1:
                y = canvas_height // 2
                positions[layer_nodes[0]] = (x, y)
            else:
                layer_height = canvas_height - 2 * margin
                node_spacing = layer_height / (len(layer_nodes) - 1) if len(layer_nodes) > 1 else 0
                
                for node_idx, node in enumerate(layer_nodes):
                    y = margin + node_idx * node_spacing
                    positions[node] = (x, y)
        
        return positions
    
    def organize_nodes_into_layers(self, graph, node_degrees, n):
        visited = set()
        layers = []
        sorted_nodes = sorted(range(n), key=lambda x: node_degrees[x])
        
        for start_node in sorted_nodes:
            if start_node in visited:
                continue
            
            current_layer = []
            queue = [(start_node, 0)]
            layer_nodes = {0: []}
            max_distance = 0
            
            while queue:
                node, distance = queue.pop(0)
                if node in visited:
                    continue
                
                visited.add(node)
                if distance not in layer_nodes:
                    layer_nodes[distance] = []
                layer_nodes[distance].append(node)
                max_distance = max(max_distance, distance)
                
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        queue.append((neighbor, distance + 1))
            
            for dist in sorted(layer_nodes.keys()):
                if layer_nodes[dist]:
                    layers.append(layer_nodes[dist])
        
        remaining = [i for i in range(n) if i not in visited]
        if remaining:
            layers.append(remaining)
        
        return layers
    
    def draw_edges(self):
        n = self.num_nodes.get()
        
        for i in range(n):
            for j in range(i + 1, n):
                if (i < len(self.adjacency_matrix) and 
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
                    
                    self.viz_canvas.create_line(x1, y1, x2, y2, 
                                               fill=color, width=width)
                    
                    if self.show_capacities.get() and capacity > 0:
                        mid_x = (x1 + x2) / 2
                        mid_y = (y1 + y2) / 2
                        
                        text_id = self.viz_canvas.create_text(mid_x, mid_y, 
                                                             text=f"{capacity:.0f}",
                                                             font=("Arial", 9, "bold"))
                        
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
        
        colors = ["red", "blue", "green", "purple", "orange", "brown", "pink", "cyan"]
        
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
    
    def save_visualization(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".ps",
                filetypes=[("PostScript files", "*.ps"), ("All files", "*.*")]
            )
            if filename:
                self.viz_canvas.postscript(file=filename)
                messagebox.showinfo("Success", f"Visualization saved as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {str(e)}")
    
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
        
        connections = [(0,1), (1,2), (1,3), (2,4), (3,4)]
        for i, j in connections:
            self.adjacency_matrix[i][j].set(1)
            self.adjacency_matrix[j][i].set(1)
        
        capacities = {(0,1): 12, (1,2): 10, (1,3): 7, (2,4): 8, (3,4): 6}
        for (i,j), cap in capacities.items():
            self.capacity_matrix[i][j].set(cap)
            self.capacity_matrix[j][i].set(cap)
        
        self.demands[0]['source'].set(1)
        self.demands[0]['dest'].set(5)
        self.demands[0]['demand'].set(8)
        
        self.demands[1]['source'].set(1)
        self.demands[1]['dest'].set(5)
        self.demands[1]['demand'].set(4)
        
        self.update_visualization()
    
    def save_config(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                config = {
                    'num_nodes': self.num_nodes.get(),
                    'num_demands': self.num_demands.get(),
                    'adjacency': [[self.adjacency_matrix[i][j].get() for j in range(len(self.adjacency_matrix[i]))] 
                                for i in range(len(self.adjacency_matrix))],
                    'capacities': [[self.capacity_matrix[i][j].get() for j in range(len(self.capacity_matrix[i]))] 
                                 for i in range(len(self.capacity_matrix))],
                    'demands': [{'source': d['source'].get(), 'dest': d['dest'].get(), 'demand': d['demand'].get()} 
                               for d in self.demands]
                }
                
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                
                messagebox.showinfo("Success", "Configuration saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {str(e)}")
    
    def load_config(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                self.num_nodes.set(config['num_nodes'])
                self.num_demands.set(config['num_demands'])
                self.update_matrices()
                
                for i in range(len(config['adjacency'])):
                    for j in range(len(config['adjacency'][i])):
                        self.adjacency_matrix[i][j].set(config['adjacency'][i][j])
                
                for i in range(len(config['capacities'])):
                    for j in range(len(config['capacities'][i])):
                        self.capacity_matrix[i][j].set(config['capacities'][i][j])
                
                for i, demand_data in enumerate(config['demands']):
                    self.demands[i]['source'].set(demand_data['source'])
                    self.demands[i]['dest'].set(demand_data['dest'])
                    self.demands[i]['demand'].set(demand_data['demand'])
                
                self.update_visualization()
                
                messagebox.showinfo("Success", "Configuration loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading: {str(e)}")
    
    def analyze_network(self):
        try:
            self.result_text.delete(1.0, tk.END)
            
            n = self.num_nodes.get()
            
            adj_matrix = np.array([[self.adjacency_matrix[i][j].get() for j in range(n)] for i in range(n)])
            cap_matrix = np.array([[self.capacity_matrix[i][j].get() for j in range(n)] for i in range(n)])
            
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
                self.result_text.insert(tk.END, "⚠️ No active demands to process\n")
                messagebox.showinfo("Info", "No active demands to process")
                return None
            
            self.result_text.insert(tk.END, "🔄 STARTING NETWORK ANALYSIS\n")
            self.result_text.insert(tk.END, "="*50 + "\n\n")
            
            network_data = {
                'capacity_matrix': capacity_adjacency_matrix,
                'demands': demands_list
            }
            
            self.result_text.insert(tk.END, "📊 Initializing allocation algorithm...\n")
            self.root.update()
            
            allocator = VirtualNetworkAllocation(network_data)
            
            initial_status = allocator.get_network_status()
            self.result_text.insert(tk.END, "\n📋 NETWORK INITIAL STATUS\n")
            self.result_text.insert(tk.END, "-"*30 + "\n")
            self.result_text.insert(tk.END, f"• Nodes: {allocator.num_nodes}\n")
            self.result_text.insert(tk.END, f"• Links: {allocator.total_links}\n")
            self.result_text.insert(tk.END, f"• Total capacity: {allocator.total_capacity:.2f} Mbps\n")
            self.result_text.insert(tk.END, f"• Total demand: {allocator.total_demand:.2f} Mbps\n")
            self.result_text.insert(tk.END, f"• Network connected: {'✅ Yes' if allocator.network_connected else '❌ No'}\n")
            self.result_text.insert(tk.END, f"• Total demands: {initial_status['total_demands']}\n")
            
            if not allocator.network_connected:
                self.result_text.insert(tk.END, "\n⚠️ WARNING: Network is not fully connected\n")
                messagebox.showwarning("Warning", "Network is not fully connected")
            
            self.result_text.insert(tk.END, "\n🔄 RUNNING OPTIMAL ALLOCATION...\n")
            self.result_text.insert(tk.END, "Please wait, this may take a moment...\n\n")
            self.root.update()
            
            result = allocator.offline_brute_force_allocation()
            
            if result['success']:
                self.result_text.insert(tk.END, "✅ ALLOCATION RESULTS\n")
                self.result_text.insert(tk.END, "="*40 + "\n")
                self.result_text.insert(tk.END, f"📈 Acceptance ratio: {result['acceptance_ratio']:.2%}\n")
                self.result_text.insert(tk.END, f"💰 Revenue/cost ratio: {result['revenue_cost_ratio']:.2f}\n")
                self.result_text.insert(tk.END, f"💵 Total revenue: ${result['total_revenue']:.2f}\n")
                self.result_text.insert(tk.END, f"💸 Total costs: ${result['total_cost']:.2f}\n")
                self.result_text.insert(tk.END, f"✅ Allocated demands: {len(result['allocated_demands'])}\n")
                self.result_text.insert(tk.END, f"❌ Rejected demands: {len(result['rejected_demands'])}\n")
                self.result_text.insert(tk.END, f"🔢 Combinaciones evaluadas: {result['total_combinations_evaluated']}\n")
                self.result_text.insert(tk.END, f"✅ Combinaciones válidas: {result['valid_combinations']}\n")
                
                # Mostrar detalles de asignación
                if result.get('allocation_details'):
                    self.result_text.insert(tk.END, "\n📊 DETALLES DE ASIGNACIÓN\n")
                    self.result_text.insert(tk.END, "-" * 40 + "\n")
                    
                    for i, detail in enumerate(result['allocation_details']):
                        path_str = " → ".join([str(node+1) for node in detail['path']])  # Convertir a base 1 para mostrar
                        
                        self.result_text.insert(tk.END, f"\n🔹 Demanda {detail['demand_index']+1}:\n")
                        self.result_text.insert(tk.END, f"   • Origen: Nodo {detail['source']+1}\n")
                        self.result_text.insert(tk.END, f"   • Destino: Nodo {detail['destination']+1}\n")
                        self.result_text.insert(tk.END, f"   • Ancho de banda: {detail['bandwidth']:.2f} Mbps\n")
                        self.result_text.insert(tk.END, f"   • Ruta: {path_str}\n")
                        self.result_text.insert(tk.END, f"   • Costo: ${detail['cost']:.2f}\n")
                        self.result_text.insert(tk.END, f"   • Ingreso: ${detail['revenue']:.2f}\n")
                
                # Mostrar demandas rechazadas si las hay
                if result['rejected_demands']:
                    self.result_text.insert(tk.END, "\n❌ DEMANDAS RECHAZADAS\n")
                    self.result_text.insert(tk.END, "-" * 25 + "\n")
                    for i, rejected in enumerate(result['rejected_demands']):
                        self.result_text.insert(tk.END, f"• Demanda {rejected+1}: No se pudo asignar por falta de capacidad\n")
                
                # Mostrar estado final de la red
                final_status = allocator.get_network_status()
                self.result_text.insert(tk.END, "\n📊 ESTADO FINAL DE LA RED\n")
                self.result_text.insert(tk.END, "-" * 30 + "\n")
                self.result_text.insert(tk.END, f"📊 Utilización de red: {final_status['network_utilization']:.2%}\n")
                self.result_text.insert(tk.END, f"💾 Capacidad restante: {final_status['remaining_capacity']:.2f} Mbps\n")
                
                # Mostrar eficiencia y métricas adicionales
                if final_status['network_utilization'] > 0.8:
                    self.result_text.insert(tk.END, f"🔥 ¡Excelente utilización de la red!\n")
                elif final_status['network_utilization'] > 0.6:
                    self.result_text.insert(tk.END, f"✅ Buena utilización de la red\n")
                else:
                    self.result_text.insert(tk.END, f"⚠️ Utilización de red baja - considere optimizar\n")
                
                # Resumen final
                self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
                self.result_text.insert(tk.END, "✅ ANÁLISIS COMPLETADO EXITOSAMENTE\n")
                self.result_text.insert(tk.END, "=" * 50 + "\n")
                
                # Scroll al final
                self.result_text.see(tk.END)
                
                # Mostrar ventana emergente con resumen
                summary = (f"🎯 ASIGNACIÓN COMPLETADA EXITOSAMENTE\n\n"
                          f"📈 Ratio de aceptación: {result['acceptance_ratio']:.2%}\n"
                          f"✅ Demandas asignadas: {len(result['allocated_demands'])}\n"
                          f"❌ Demandas rechazadas: {len(result['rejected_demands'])}\n"
                          f"📊 Utilización de red: {final_status['network_utilization']:.2%}\n"
                          f"💰 Ratio ingresos/costos: {result['revenue_cost_ratio']:.2f}")
                
                messagebox.showinfo("🎉 Asignación Exitosa", summary)
                
                # Retornar datos actualizados con resultados
                return {
                    'capacity_matrix': capacity_adjacency_matrix,
                    'demands': demands_list,
                    'allocation_result': result,
                    'network_status': final_status,
                    'allocator': allocator  # Para uso posterior si es necesario
                }
            else:
                # Mostrar error en la GUI
                error_msg = result.get('message', 'Error desconocido en la asignación')
                self.result_text.insert(tk.END, f"❌ ERROR EN ASIGNACIÓN\n")
                self.result_text.insert(tk.END, "=" * 30 + "\n")
                self.result_text.insert(tk.END, f"💥 {error_msg}\n\n")
                self.result_text.insert(tk.END, "🔍 Posibles causas:\n")
                self.result_text.insert(tk.END, "• Red no conectada completamente\n")
                self.result_text.insert(tk.END, "• Capacidades insuficientes\n")
                self.result_text.insert(tk.END, "• Demandas muy altas\n")
                self.result_text.insert(tk.END, "• Configuración de red inválida\n")
                
                self.result_text.see(tk.END)
                messagebox.showerror("❌ Error de Asignación", 
                                  f"No se pudo realizar la asignación:\n\n{error_msg}")
                return None
                
        except Exception as e:
            error_msg = f"Error en el análisis: {str(e)}"
            
            # Mostrar error en la GUI
            self.result_text.insert(tk.END, f"💥 ERROR CRÍTICO\n")
            self.result_text.insert(tk.END, "=" * 20 + "\n")
            self.result_text.insert(tk.END, f"{error_msg}\n\n")
            self.result_text.insert(tk.END, "🔧 Por favor:\n")
            self.result_text.insert(tk.END, "• Verifique la configuración de la red\n")
            self.result_text.insert(tk.END, "• Asegúrese de que las matrices estén completas\n")
            self.result_text.insert(tk.END, "• Revise que las demandas sean válidas\n")
            
            self.result_text.see(tk.END)
            messagebox.showerror("💥 Error Crítico", error_msg)
            return None
      
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