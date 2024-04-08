from gurobipy import GRB, Model
import pandas as pd

url = "https://raw.githubusercontent.com/rbaid-9/Models_Assignment3/main/costs.csv"
cost_data = pd.read_csv(url)

# Extracting data
num_sites = len(cost_data)
fixed_costs = cost_data['Fixed'].tolist()
variable_costs = cost_data['Variable'].tolist()

# Create a new optimization model
model = Model("Regional Warehouses")

# Decision variables
x = model.addVars(num_sites, lb=0, vtype=GRB.INTEGER, name="Storage")
y = model.addVars(num_sites, vtype=GRB.BINARY, name="Selection")

# Objective function
total_fixed_costs = sum(fixed_costs[i] * y[i] for i in range(num_sites))
total_variable_costs = sum(variable_costs[i] * x[i] for i in range(num_sites))
model.setObjective(total_fixed_costs + total_variable_costs, GRB.MINIMIZE)

# Constraints
constraints = {}

# Storage capacity constraints
for i in range(num_sites):
    constraints[f"StorageCapacity_Lower_{i}"] = model.addConstr(175000 <= x[i], name=f"StorageCapacity_Lower_{i}")
    constraints[f"StorageCapacity_Upper_{i}"] = model.addConstr(x[i] <= 375000, name=f"StorageCapacity_Upper_{i}")

# Minimum warehouses among sites 6-16
constraints["MinimumWarehouses_6_16"] = model.addConstr(sum(y[i] for i in range(6, 17)) >= 4, name="MinimumWarehouses_6_16")

# Maximum warehouses among even numbered sites
constraints["MaximumEvenWarehouses"] = model.addConstr(sum(y[i] for i in range(2, num_sites, 2)) <= 6, name="MaximumEvenWarehouses")

# Site 1 and 2 exclusion
constraints["Site1_2_Exclusion"] = model.addConstr(y[0] + y[1] <= 1, name="Site1_2_Exclusion")

# Sites 19-22 exclusion
constraints["Sites19_22_Exclusion"] = model.addConstr(sum(y[i] for i in range(19, 23)) <= 1, name="Sites19_22_Exclusion")

# Sites 1-5 selection
constraints["Sites1_5_Selection"] = model.addConstr(sum(y[i] for i in range(1, 6)) <= 5, name="Sites1_5_Selection")

# Odd sites selection among sites 21-27
constraints["OddSites_Selection"] = model.addConstr(sum(y[i] for i in range(21, num_sites, 2)) >= 1, name="OddSites_Selection")

# Equal warehouse counts between sites 1-14 and 15-27
constraints["EqualWarehouseCounts"] = model.addConstr(sum(y[i] for i in range(1, 15)) == sum(y[i] for i in range(15, num_sites)), name="EqualWarehouseCounts")

# Equal unit counts between sites 1-9 and 19-27
constraints["EqualUnitCounts"] = model.addConstr(sum(y[i] for i in range(1, 10)) == sum(y[i] for i in range(19, num_sites)), name="EqualUnitCounts")

# Solve the model
model.optimize()

# Print the selected sites and their corresponding storage units
print("Selected sites and their storage units:")
for i in range(num_sites):
    if y[i].x > 0.5:
        print(f"Site {i+1} is chosen with {x[i].x} units stored.")

# Print the total cost
print("Total cost:", model.objVal)