import os
import pandas
import numpy as np
import data_processor

data_dir = "data/"
processed_dir = "processed/"
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)
#data_processor.preprocess_data(data_dir, processed_dir)

# Data analysis
test_file_path = os.path.join(processed_dir, "processed_Rb_5M_1000Hz_2024-02-05_13-48-16.csv")
test_data = pandas.read_csv(test_file_path, sep=',')

# Initialize variables to track the charging and discharging phases
charging_start_time = None
discharging_start_time = None
cycles = []

# Iterate over the rows of the DataFrame
for index, row in test_data.iterrows():
    output_voltage = row['Output Voltage']
    current_time = row['Time']

    if charging_start_time is None and output_voltage > 1:
        charging_start_time = current_time
    if charging_start_time is None and output_voltage < 1:
        discharging_start_time = current_time

    elif charging_start_time is not None and discharging_start_time is None and output_voltage < 3:
        discharging_start_time = current_time

    elif discharging_start_time is not None and output_voltage > 3:
        cycles.append({
            'Charging Start': charging_start_time,
            'Charging End': np.round(discharging_start_time - 0.001, 3),
            'Discharging Start': discharging_start_time,
            'Discharging End': np.round(current_time - 0.001, 3),
            'Period Start': charging_start_time,
            'Period End': np.round(current_time - 0.001, 3)
        })
        # Reset for the next cycle
        charging_start_time = current_time
        discharging_start_time = None

if cycles:
    cycles.pop(0)

for i, cycle in enumerate(cycles, 1):
    print(f"Cycle {i}:")
    print(f"  Charging Start: {cycle['Charging Start']}, Charging End: {cycle['Charging End']}")
    print(f"  Discharging Start: {cycle['Discharging Start']}, Discharging End: {cycle['Discharging End']}")
    print(f"  Total Period Start: {cycle['Period Start']}, Total Period End: {cycle['Period End']}")

# Print the total number of full cycles
print(f"Total number of full cycles found: {len(cycles)}")
