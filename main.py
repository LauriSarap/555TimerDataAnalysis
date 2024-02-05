import os
import pandas
import numpy as np
import data_processor

data_dir = "data/"
processed_dir = "processed/"
cycle_dir = "cycles/"
final_dir = "final/"
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)
if not os.path.exists(cycle_dir):
    os.makedirs(cycle_dir)
if not os.path.exists(final_dir):
    os.makedirs(final_dir)

# Preprocess data
#data_processor.preprocess_data(data_dir, processed_dir)

# Create cycles data
#data_processor.process_cycles_data(processed_dir, cycle_dir)

# Create final data
data_processor.calculate_average_cycle_lengths(cycle_dir, final_dir)