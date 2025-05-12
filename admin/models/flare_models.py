class Pipe:
    def __init__(self, name, equivalent_length, diameter, outlet_pressure, roughness, cross_area, 
                 flow_rate=None, avg_temperature=None, avg_molecular_weight=None, mach_number=None,
                 friction_factor=None, inlet_pressure=None, reynolds_number=None):
        self.name = name
        self.equivalent_length = equivalent_length          
        self.diameter = diameter          
        self.outlet_pressure = outlet_pressure          
        self.roughness = roughness 
        self.cross_area = cross_area         
        
        # 需要计算的值
        self.flow_rate = flow_rate          
        self.avg_temperature = avg_temperature          
        self.avg_molecular_weight = avg_molecular_weight     
        self.mach_number = mach_number          
        self.reynolds_number = reynolds_number
        self.friction_factor = friction_factor   
        self.inlet_pressure = inlet_pressure

    def __repr__(self):
        return f"Pipe({self.name}, L={self.equivalent_length}, D={self.diameter})"

class DischargePoint:
    def __init__(self, node_id, flow_rate=None, pressure=None, temperature=None, 
                 molecular_weight=None, max_backpressure=None, viscosity=None):
        self.node_id = node_id
        self.flow_rate = flow_rate        # 单位: kg/h
        self.pressure = pressure          # 单位: Pa
        self.temperature = temperature    # 单位: K
        self.molecular_weight = molecular_weight  # 单位: g/mol
        self.max_backpressure = max_backpressure  # 单位: Pa
        self.viscosity = viscosity        # 单位: Pa·s

    def __repr__(self):
        return f"DischargePoint({self.node_id}, flow={self.flow_rate}, p={self.pressure}, t={self.temperature})" 