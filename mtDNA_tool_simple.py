#!/usr/bin/env python
# coding: utf-8

# In[4]:


import tkinter as tk
from tkinter import scrolledtext
import re
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def read_crs_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        sequence = ''.join(line.strip() for line in lines[1:] if not line.startswith('>'))
        return sequence
    except FileNotFoundError:
        return None

def reverse_complement(sequence):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'D': 'D', 'I': 'I', 'N': 'N'}
    return ''.join(complement[base] for base in reversed(sequence))

def compare_sequences(reference_sequence, user_sequence, reference_name, ignore_n):
    best_match_index = -1
    min_differences = len(user_sequence) + 1
    differences = []
    ignored_n_count = 0

    for i in range(len(reference_sequence)):
        current_differences = []
        current_ignored_n_count = 0
        for j in range(len(user_sequence)):
            if user_sequence[j] != reference_sequence[(i + j) % len(reference_sequence)]:
                if ignore_n and user_sequence[j] == 'N':
                    current_ignored_n_count += 1
                else:
                    if reference_name == "RSRS":
                        current_differences.append(f"{reference_sequence[(i + j) % len(reference_sequence)]}{(i + j) % len(reference_sequence) + 1}{user_sequence[j]}")
                    else:
                        current_differences.append(f"[{reference_sequence[(i + j) % len(reference_sequence)]}]{(i + j) % len(reference_sequence) + 1}{user_sequence[j]}")
        if len(current_differences) < min_differences:
            min_differences = len(current_differences)
            best_match_index = i
            differences = current_differences
            ignored_n_count = current_ignored_n_count

    if best_match_index == -1:
        return f"The sequence was not found in the {reference_name} sequence"

    start_pos = best_match_index + 1
    end_pos = (best_match_index + len(user_sequence)) % len(reference_sequence)
    if end_pos == 0:
        end_pos = len(reference_sequence)

    result = f"The entered sequence including {len(user_sequence)} positions\n"
    result += f"The entered sequence matches positions {start_pos} to {end_pos} in the {reference_name} sequence\n"
    if differences:
        result += f"There are {len(differences)} differences between the entered sequence and the {reference_name} sequence:\n" + "\n".join(differences)
    else:
        result += f"There are no differences between the entered sequence and the {reference_name} sequence"

    if ignore_n and ignored_n_count > 0:
        result += f"\n\nNote: The list of differences ignores {ignored_n_count} differences caused by 'N' in the input sequence."

    return result

def compare_aligned_sequences(reference_sequence, user_sequence, reference_name, ignore_n):
    best_match_index = -1
    min_differences = len(user_sequence) + 1
    differences = []
    ignored_n_count = 0

    for i in range(len(reference_sequence) - len(user_sequence) + 1):
        current_differences = []
        current_ignored_n_count = 0
        for j in range(len(user_sequence)):
            if user_sequence[j] != reference_sequence[i + j]:
                if ignore_n and user_sequence[j] == 'N':
                    current_ignored_n_count += 1
                else:
                    if reference_name == "RSRS":
                        current_differences.append(f"{reference_sequence[i + j]}{i + j + 1}{user_sequence[j]}")
                    else:
                        current_differences.append(f"[{reference_sequence[i + j]}]{i + j + 1}{user_sequence[j]}")
        if len(current_differences) < min_differences:
            min_differences = len(current_differences)
            best_match_index = i
            differences = current_differences
            ignored_n_count = current_ignored_n_count

    if best_match_index == -1:
        return f"The sequence was not found in the {reference_name} sequence"

    start_pos = best_match_index + 1
    end_pos = best_match_index + len(user_sequence)
    result = f"The entered sequence including {len(user_sequence)} positions\n"
    result += f"The entered sequence matches positions {start_pos} to {end_pos} in the {reference_name} sequence\n"
    if differences:
        result += f"There are {len(differences)} differences between the entered sequence and the {reference_name} sequence:\n" + "\n".join(differences)
    else:
        result += f"There are no differences between the entered sequence and the {reference_name} sequence"

    if ignore_n and ignored_n_count > 0:
        result += f"\n\nNote: The list of differences ignores {ignored_n_count} differences caused by 'N' in the input sequence."

    return result

def on_compare():
    result_text.config(state=tk.NORMAL)
    
    user_sequence = entry.get("1.0", "end-1c").strip()
    user_sequence = re.sub(r'\s+', '', user_sequence)

    if not re.match(r'^[AGTCDIN]+$', user_sequence):
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "The sequence contains invalid characters. Please enter a sequence containing only the characters A, G, T, C, D, I, N.")
        return

    if not user_sequence:
        result_text.insert(tk.END, "Please enter a sequence")
        return

    if reverse_var.get() == 1:
        user_sequence = reverse_complement(user_sequence)

    results = []
    ignore_n = ignore_n_var.get() == 1

    if crs_sequence is None:
        results.append("Error: Unable to read the rCRS sequence file.")
    else:
        if aligned_var.get() == 1:
            results.append(compare_sequences(crs_sequence, user_sequence, "rCRS", ignore_n))
        else:
            results.append(compare_aligned_sequences(crs_sequence, user_sequence, "rCRS", ignore_n))

    if rsrs_sequence is None:
        results.append("Error: Unable to read the RSRS sequence file.")
    else:
        if aligned_var.get() == 1:
            results.append(compare_sequences(rsrs_sequence, user_sequence, "RSRS", ignore_n))
        else:
            results.append(compare_aligned_sequences(rsrs_sequence, user_sequence, "RSRS", ignore_n))

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "\n\n".join(results))
    result_text.config(state=tk.DISABLED)

def on_reverse_change(*args):
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)

crs_sequence = read_crs_file(resource_path('rCRS.txt'))
rsrs_sequence = read_crs_file(resource_path('RSRS.txt'))

root = tk.Tk()
root.title("DNA Sequence Comparison | By Rabbi Dr. Simcha Gershon Bohrer | Version: Beta 2")

root.geometry("800x600")

label = tk.Label(root, text="Enter a mtDNA sequence for comparison:")
label.pack(pady=5)
entry = scrolledtext.ScrolledText(root, width=80, height=5)
entry.pack(pady=5)

reverse_var = tk.IntVar()
reverse_var.trace_add("write", on_reverse_change)
reverse_check = tk.Checkbutton(root, text="Input sequence is reverse complement", variable=reverse_var)
reverse_check.pack(pady=5)

aligned_var = tk.IntVar()
aligned_var.trace_add("write", on_reverse_change)
aligned_check = tk.Checkbutton(root, text="The input sequence is circular, not aligned", variable=aligned_var)
aligned_check.pack(pady=5)

ignore_n_var = tk.IntVar()
ignore_n_var.trace_add("write", on_reverse_change)
ignore_n_check = tk.Checkbutton(root, text="Ignore differences caused by 'N' in input sequence", variable=ignore_n_var)
ignore_n_check.pack(pady=5)

compare_button = tk.Button(root, text="Compare", command=on_compare)
compare_button.pack(pady=5)

result_text = scrolledtext.ScrolledText(root, width=80, height=20)
result_text.pack(pady=5)
result_text.config(state=tk.DISABLED)

root.mainloop()

