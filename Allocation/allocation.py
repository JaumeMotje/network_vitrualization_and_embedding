import itertools
import copy
from typing import List, Dict, Tuple, Optional
import numpy as np

class VirtualNetworkAllocation:
    def __init__(self, network_data: Dict):
        """
        Initialize the Virtual Network Allocation system
        
        Args:
            network_data: Dictionary containing network information
        """
        self.capacity_matrix = np.array(network_data['capacity_matrix'])
        self.original_capacity_matrix = np.array(network_data['capacity_matrix'])
        
        # Convertir demandas al formato esperado
        demands_formatted = []
        for demand in network_data['demands']:
            if len(demand) >= 3:
                demands_formatted.append({
                    'source': int(demand[0]),
                    'destination': int(demand[1]),
                    'bandwidth': float(demand[2]),
                    'duration': 1,  # Valor por defecto
                    'price_per_unit': 1.0  # Valor por defecto
                })
        
        self.demands = demands_formatted
        
        # Crear matriz de adyacencia basada en capacidades
        self.adjacency_matrix = (self.capacity_matrix > 0).astype(int)
        self.num_nodes = len(self.capacity_matrix)
        
        # Calcular estadísticas de la red
        self.total_links = np.sum(self.adjacency_matrix) // 2  # Dividir por 2 si es no dirigida
        self.total_capacity = np.sum(self.capacity_matrix)
        self.total_demand = sum([d['bandwidth'] for d in self.demands])
        self.network_connected = self._check_connectivity()
        
        # Track allocations
        self.allocated_demands = []
        self.rejected_demands = []
        self.current_revenue = 0
        self.current_cost = 0
    
    def _check_connectivity(self) -> bool:
        """Verificar si la red está conectada usando DFS"""
        if self.num_nodes <= 1:
            return True
        
        visited = [False] * self.num_nodes
        
        def dfs(node):
            visited[node] = True
            for neighbor in range(self.num_nodes):
                if not visited[neighbor] and self.adjacency_matrix[node][neighbor] == 1:
                    dfs(neighbor)
        
        # Empezar DFS desde el primer nodo
        dfs(0)
        
        # Verificar si todos los nodos fueron visitados
        return all(visited)
    
    def calculate_path_cost(self, path: List[int], demand_bandwidth: float) -> float:
        """Calculate the cost of allocating a demand on a specific path"""
        cost = 0
        for i in range(len(path) - 1):
            node_from, node_to = path[i], path[i + 1]
            # Cost is proportional to bandwidth and path length
            cost += demand_bandwidth * 1.0  # Base cost per hop
        return cost
    
    def calculate_revenue(self, demand: Dict) -> float:
        """Calculate revenue from a demand"""
        return demand.get('bandwidth', 0) * demand.get('duration', 1) * demand.get('price_per_unit', 1.0)
    
    def find_all_paths(self, source: int, destination: int, max_hops: int = None) -> List[List[int]]:
        """Find all possible paths between source and destination"""
        if max_hops is None:
            max_hops = self.num_nodes - 1
            
        all_paths = []
        
        def dfs(current_node: int, target: int, path: List[int], visited: set):
            if len(path) > max_hops + 1:
                return
                
            if current_node == target:
                all_paths.append(path.copy())
                return
            
            for next_node in range(self.num_nodes):
                if (next_node not in visited and 
                    self.adjacency_matrix[current_node][next_node] == 1 and
                    self.capacity_matrix[current_node][next_node] > 0):
                    
                    visited.add(next_node)
                    path.append(next_node)
                    dfs(next_node, target, path, visited)
                    path.pop()
                    visited.remove(next_node)
        
        visited = {source}
        dfs(source, destination, [source], visited)
        return all_paths
    
    def can_allocate_path(self, path: List[int], bandwidth: float) -> bool:
        """Check if a path has enough capacity for the bandwidth requirement"""
        for i in range(len(path) - 1):
            node_from, node_to = path[i], path[i + 1]
            if self.capacity_matrix[node_from][node_to] < bandwidth:
                return False
        return True
    
    def allocate_path(self, path: List[int], bandwidth: float) -> None:
        """Allocate bandwidth on a path by reducing capacity"""
        for i in range(len(path) - 1):
            node_from, node_to = path[i], path[i + 1]
            self.capacity_matrix[node_from][node_to] -= bandwidth
            # If the network is undirected, also reduce the reverse direction
            if self.capacity_matrix[node_to][node_from] > 0:
                self.capacity_matrix[node_to][node_from] -= bandwidth
    
    def deallocate_path(self, path: List[int], bandwidth: float) -> None:
        """Deallocate bandwidth from a path by restoring capacity"""
        for i in range(len(path) - 1):
            node_from, node_to = path[i], path[i + 1]
            self.capacity_matrix[node_from][node_to] += bandwidth
            if self.original_capacity_matrix[node_to][node_from] > 0:
                self.capacity_matrix[node_to][node_from] += bandwidth
    
    def can_allocate_path_on_matrix(self, path: List[int], bandwidth: float, capacity_matrix: np.ndarray) -> bool:
        """Check if a path has enough capacity on a given capacity matrix"""
        for i in range(len(path) - 1):
            node_from, node_to = path[i], path[i + 1]
            if capacity_matrix[node_from][node_to] < bandwidth:
                return False
        return True
    
    def allocate_path_on_matrix(self, path: List[int], bandwidth: float, capacity_matrix: np.ndarray) -> None:
        """Allocate bandwidth on a path on a given capacity matrix"""
        for i in range(len(path) - 1):
            node_from, node_to = path[i], path[i + 1]
            capacity_matrix[node_from][node_to] -= bandwidth
            if capacity_matrix[node_to][node_from] > 0:
                capacity_matrix[node_to][node_from] -= bandwidth
    
    def evaluate_allocation_scenario(self, allocation_scenario: List[Tuple]) -> Dict:
        """Evaluate a complete allocation scenario"""
        temp_capacity = self.capacity_matrix.copy()
        
        allocated_demands = []
        total_revenue = 0
        total_cost = 0
        
        valid_scenario = True
        for demand_idx, path in allocation_scenario:
            demand = self.demands[demand_idx]
            bandwidth = demand.get('bandwidth', 0)
            
            if self.can_allocate_path_on_matrix(path, bandwidth, temp_capacity):
                self.allocate_path_on_matrix(path, bandwidth, temp_capacity)
                
                revenue = self.calculate_revenue(demand)
                cost = self.calculate_path_cost(path, bandwidth)
                
                total_revenue += revenue
                total_cost += cost
                allocated_demands.append((demand_idx, path))
            else:
                valid_scenario = False
                break
        
        if not valid_scenario:
            return {
                'valid': False,
                'acceptance_ratio': 0,
                'revenue_cost_ratio': 0,
                'allocated_demands': [],
                'total_revenue': 0,
                'total_cost': float('inf')
            }
        
        acceptance_ratio = len(allocated_demands) / len(self.demands) if self.demands else 0
        revenue_cost_ratio = total_revenue / total_cost if total_cost > 0 else 0
        
        return {
            'valid': True,
            'acceptance_ratio': acceptance_ratio,
            'revenue_cost_ratio': revenue_cost_ratio,
            'allocated_demands': allocated_demands,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'temp_capacity_matrix': temp_capacity
        }
    
    def offline_brute_force_allocation(self) -> Dict:
        """Perform offline brute-force allocation to find optimal scenario"""
        print("Iniciando asignación offline por fuerza bruta...")
        
        # Generar todos los caminos posibles para cada demanda
        demand_paths = []
        for i, demand in enumerate(self.demands):
            source = demand.get('source')
            destination = demand.get('destination')
            
            if source is None or destination is None:
                print(f"Advertencia: Demanda {i} sin origen o destino")
                continue
                
            paths = self.find_all_paths(source, destination)
            if paths:
                demand_paths.append((i, paths))
            else:
                print(f"No se encontraron caminos para demanda {i} de {source} a {destination}")
        
        if not demand_paths:
            return {
                'success': False,
                'message': 'No se encontraron caminos válidos para ninguna demanda',
                'acceptance_ratio': 0,
                'allocated_demands': [],
                'rejected_demands': list(range(len(self.demands))),
                'allocation_details': []
            }
        
        best_scenario = None
        best_metrics = {
            'acceptance_ratio': -1,
            'revenue_cost_ratio': -1
        }
        
        # Generar opciones para cada demanda
        demand_options = []
        for demand_idx, paths in demand_paths:
            options = [(demand_idx, None)]  # Opción de no asignar
            for path in paths:
                options.append((demand_idx, path))  # Opciones de asignar en diferentes caminos
            demand_options.append(options)
        
        print(f"Evaluando escenarios de asignación para {len(demand_paths)} demandas...")
        
        total_combinations = 0
        valid_combinations = 0
        
        # Generar todas las combinaciones
        for combination in itertools.product(*demand_options):
            total_combinations += 1
            
            # Filtrar opciones de no asignación y crear escenario
            scenario = [(demand_idx, path) for demand_idx, path in combination if path is not None]
            
            # Evaluar escenario
            metrics = self.evaluate_allocation_scenario(scenario)
            
            if metrics['valid']:
                valid_combinations += 1
                
                # Verificar si es el mejor escenario
                is_better = False
                if metrics['acceptance_ratio'] > best_metrics['acceptance_ratio']:
                    is_better = True
                elif (metrics['acceptance_ratio'] == best_metrics['acceptance_ratio'] and 
                      metrics['revenue_cost_ratio'] > best_metrics['revenue_cost_ratio']):
                    is_better = True
                
                if is_better:
                    best_scenario = scenario
                    best_metrics = metrics
        
        print(f"Evaluadas {total_combinations} combinaciones, {valid_combinations} fueron válidas")
        
        if best_scenario is None:
            return {
                'success': False,
                'message': 'No se encontró escenario de asignación válido',
                'acceptance_ratio': 0,
                'allocated_demands': [],
                'rejected_demands': list(range(len(self.demands))),
                'allocation_details': []
            }
        
        # Aplicar el mejor escenario
        self.capacity_matrix = best_metrics['temp_capacity_matrix'].copy()
        self.allocated_demands = [self.demands[i] for i, _ in best_scenario]
        allocated_indices = {i for i, _ in best_scenario}
        self.rejected_demands = [self.demands[i] for i in range(len(self.demands)) if i not in allocated_indices]
        self.current_revenue = best_metrics['total_revenue']
        self.current_cost = best_metrics['total_cost']
        
        # Crear detalles de asignación para mostrar
        allocation_details = []
        for demand_idx, path in best_scenario:
            demand = self.demands[demand_idx]
            allocation_details.append({
                'demand_index': demand_idx,
                'source': demand['source'],
                'destination': demand['destination'],
                'bandwidth': demand['bandwidth'],
                'path': path,
                'path_length': len(path) - 1,
                'cost': self.calculate_path_cost(path, demand['bandwidth']),
                'revenue': self.calculate_revenue(demand)
            })
        
        return {
            'success': True,
            'acceptance_ratio': best_metrics['acceptance_ratio'],
            'revenue_cost_ratio': best_metrics['revenue_cost_ratio'],
            'allocated_demands': best_scenario,
            'rejected_demands': [i for i in range(len(self.demands)) if i not in allocated_indices],
            'total_revenue': best_metrics['total_revenue'],
            'total_cost': best_metrics['total_cost'],
            'total_combinations_evaluated': total_combinations,
            'valid_combinations': valid_combinations,
            'allocation_details': allocation_details
        }
    
    def get_network_status(self) -> Dict:
        """Get current network status and statistics"""
        total_original_capacity = np.sum(self.original_capacity_matrix)
        total_remaining_capacity = np.sum(self.capacity_matrix)
        utilization = (total_original_capacity - total_remaining_capacity) / total_original_capacity if total_original_capacity > 0 else 0
        
        return {
            'total_demands': len(self.demands),
            'allocated_demands': len(self.allocated_demands),
            'rejected_demands': len(self.rejected_demands),
            'acceptance_ratio': len(self.allocated_demands) / len(self.demands) if self.demands else 0,
            'network_utilization': utilization,
            'total_revenue': self.current_revenue,
            'total_cost': self.current_cost,
            'revenue_cost_ratio': self.current_revenue / self.current_cost if self.current_cost > 0 else 0,
            'remaining_capacity': total_remaining_capacity,
            'original_capacity': total_original_capacity,
            'network_connected': self.network_connected
        }
    
    def reset_network(self):
        """Reset network to original state"""
        self.capacity_matrix = self.original_capacity_matrix.copy()
        self.allocated_demands = []
        self.rejected_demands = []
        self.current_revenue = 0
        self.current_cost = 0
        print("Red restablecida al estado original")