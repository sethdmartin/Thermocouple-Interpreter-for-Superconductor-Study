# Thermocouple-Interpreter-for-Superconductor-Study
Python scripts created to measure the voltage offset in a thermocouple then interpret data it collected on a cooled superconductor to calculate its threshold temperature

voltage_correction.py: calculates voltage offset based off data collected at room temperature, water freezing temperature, and liquid nitrogen boiling temperature. These were hardcoded into temps.py to correct the temperatures found
temps.py: uses the polynomial function associated with the thermocouple used and the data collected at the multimeter to fit for the threshold temperature of the superconductor
in total, four trials of data exist but only the two usable ones are included here
