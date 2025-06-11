# KPIs para la asignación de red virtual

# Constants for cost and revenue per Mbps
COST_PER_MBPS = 1.0  # Change as needed
REVENUE_PER_MBPS = 10.0  # Change as needed

def acceptance_ratio(allocated_demands, total_demands):
    """Calcula el ratio de aceptación de demandas."""
    if total_demands == 0:
        return 0.0
    return len(allocated_demands) / total_demands

def revenue_cost_ratio(total_revenue, total_cost):
    """Calcula el ratio ingresos/costos."""
    if total_cost == 0:
        return 0.0
    return total_revenue / total_cost

def total_revenue(allocated_details, revenue_per_mbps=1.0):
    """Suma los ingresos de las demandas asignadas usando el parámetro de revenue por Mbps."""
    return sum(detail.get('revenue', 0) * revenue_per_mbps for detail in allocated_details)

def total_cost(allocated_details, cost_per_mbps=1.0):
    """Suma los costos de las demandas asignadas usando el parámetro de coste por Mbps."""
    return sum(detail.get('cost', 0) * cost_per_mbps for detail in allocated_details)

def num_demands_assigned(allocated_demands):
    """Cuenta las demandas asignadas."""
    return len(allocated_demands)

def num_demands_rejected(rejected_demands):
    """Cuenta las demandas rechazadas."""
    return len(rejected_demands)

def total_combinations_evaluated(result):
    """Obtiene el número de combinaciones evaluadas."""
    return result.get('total_combinations_evaluated', 'N/A')

def valid_combinations(result):
    """Obtiene el número de combinaciones válidas."""
    return result.get('valid_combinations', 'N/A')
