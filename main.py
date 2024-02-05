import os
import pandas
import numpy as np
import data_processor

data_dir = "data/"
processed_dir = "processed/"
cycle_dir = "cycles/"
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)
if not os.path.exists(cycle_dir):
    os.makedirs(cycle_dir)

# Preprocess data
#data_processor.preprocess_data(data_dir, processed_dir)

# Identify cycles
current_test_file = "processed_Ra_1M_1000Hz_2024-02-05_13-16-00.csv"

test_file_path = os.path.join(processed_dir, current_test_file)
test_data = pandas.read_csv(test_file_path, sep=',')
cycles = data_processor.identify_cycles(test_data)

# Calculate periods
original_file_name = current_test_file.replace('processed_', '')
new_cycles_file_name = f"cycles_{original_file_name}"
periods = data_processor.calculate_periods(cycles, cycle_dir=cycle_dir, new_cycles_file_name=new_cycles_file_name)
