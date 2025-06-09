#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# יבוא חבילות נדרשות
import tkinter as tk
from tkinter import scrolledtext
import re
import os
import sys

# פונקצייה לקבלת מיקום מוחלט של קובץ המכיל את רצף הייחוס של הדנא המיטוכונדרי
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# קריאת הקובץ של רצף הייחוס
def read_crs_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        sequence = ''.join(line.strip() for line in lines[1:] if not line.startswith('>'))
        return sequence
    except FileNotFoundError:
        return None

# הפיכת רצף דנ"א מגדיל אחד למקבילה שלו בגדיל הנגדי של הדנ"א
def reverse_complement(sequence):
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'D': 'D', 'I': 'I', 'N': 'N'}
    return ''.join(complement[base] for base in reversed(sequence))


# הפונקצייה הראשית שמשווה את רצף הנבדק לרצף ההתייחסות
# החישוב קצת משתנה אם הרצף של הנבדק הוא מעגלי מהסוף להתחלה או שהוא מיושר לפי הסדר מההתחלה לסוף
def compare_sequences(reference_sequence, user_sequence, reference_name, ignore_n, aligned=False):
    
    best_match_index = -1
    min_differences = len(user_sequence) + 1
    differences = []
    ignored_n_count = 0

    # קביעת אורך הלולאה בהתאם לסוג ההשוואה
    loop_range = range(len(reference_sequence)) if not aligned else range(len(reference_sequence) - len(user_sequence) + 1)

    # לולאת ההשוואה הראשית
    for i in loop_range:
        current_differences = []
        current_ignored_n_count = 0
        for j in range(len(user_sequence)):
            ref_index = (i + j) % len(reference_sequence) if not aligned else i + j

            if user_sequence[j] != reference_sequence[ref_index]:
                if ignore_n and user_sequence[j] == 'N':
                    current_ignored_n_count += 1
                else:
                    # הגדרת הפורמט של ההדפסה עבור מה שיש ברצף ההתייחסות במיקום זה
                    reference_index = f"{reference_sequence[ref_index]}" if reference_name == "RSRS" else f"[{reference_sequence[ref_index]}]"
                    # הגדרת הרצף של 24 המקומות שקודם המוטצייה ברצף של הנבדק כדי שיוכלו להעתיק זאת לקובץ איי.בי.1 לבדיקת איכות הקריאה במיקום זה
                    TTT = f"{user_sequence[j-(24 if j >=24 else j):j]}{user_sequence[j]}"
                    TTT = f"{reverse_complement(TTT)} left end" if reverse_var.get() == 1 else f"{TTT} right end"
                    # הגדרת ההדפסה הסופית 
                    current_differences.append(f"{reference_index}{ref_index + 1}{user_sequence[j]}               ab1 file: {TTT}")
                        
        if len(current_differences) < min_differences:
            min_differences = len(current_differences)
            best_match_index = i
            differences = current_differences
            ignored_n_count = current_ignored_n_count

    if best_match_index == -1:
        return f"The sequence was not found in the {reference_name} sequence"

    start_pos = best_match_index + 1
    end_pos = (best_match_index + len(user_sequence)) % len(reference_sequence) if not aligned else best_match_index + len(user_sequence)
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


# פונקציית חישוב התוצאות והדפסתם באמצעות פונקציית ההשוואה שהוגדרה לעיל
def on_compare():
    # פתיחת תיבת הטקסט לעריכה
    result_text.config(state=tk.NORMAL)
    
    # תיקון וסידור הרצף של המשתמש שהוזן
    user_sequence = entry.get("1.0", "end-1c").strip()
    user_sequence = re.sub(r'\s+', '', user_sequence)

    # טיפול במקרה שמזינים רצף לא נכון
    if not re.match(r'^[AGTCDIN]+$', user_sequence):
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "The sequence contains invalid characters. \nPlease enter a sequence containing only the characters A, G, T, C, D, I, N.")
        return

    # טיפול במקרה שלא הזינו שום רצף של משתמש
    if not user_sequence:
        result_text.insert(tk.END, "Please enter a sequence")
        return

    # אם הזינו רצף משתמש רוורס, תחילה יש להמיר אותו לרצף קדמי באמצעות פונקצייה שהוגדרה לעיל כי רצף ההתייחסות הוא קדמי 
    if reverse_var.get() == 1:
        user_sequence = reverse_complement(user_sequence)

    results = []
    ignore_n = ignore_n_var.get() == 1
    it_is_aligned = aligned_var.get() == 0
    
    # אם לא מסומן שרק רוצים לבצע היפוך/יישור של הרצף
    if reverse_only_var.get() == 0:
    
        # חישוב התוצאות עבור רצף CRS
        if crs_sequence is None:
            results.append("Error: Unable to read the rCRS sequence file.")
        else:
            results.append(compare_sequences(crs_sequence, user_sequence, "rCRS", ignore_n, aligned = it_is_aligned))

        # חישוב התוצאות עבור רצף RSRS
        if rsrs_sequence is None:
            results.append("Error: Unable to read the RSRS sequence file.")
        else:
            results.append(compare_sequences(rsrs_sequence, user_sequence, "RSRS", ignore_n, aligned = it_is_aligned))
     
        # מחיקת מה שיש בתיבת הטקסט, הוספת התוצאות לשם, וסגירת תיבת הטקסט לעריכה
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n\n".join(results))
        result_text.config(state=tk.DISABLED)
        
    # אם מסומן שרך רוצים לבצע יישור/היפוך של הרצף
    elif reverse_only_var.get() == 1:
        # קריאת הפונקציה לביצוע ההיפוך וההחלפה והכנסה של התוצאות לתיבת הטקסט
        result = reverse_complement(user_sequence)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Input is:\n{user_sequence}\n\n")
        result_text.insert(tk.END, f"Output is - reverse/align bases only:\n{result[::-1]}\n\n") 
        result_text.insert(tk.END, f"Output is - reverse/align bases and Changing the writing direction:\n{result}")
        result_text.config(state=tk.DISABLED) 

        
# פונקצייה שמוחקת את מה שיש בתיבת התוצאות במקרה שקוראים לה
def on_reverse_change(*args):
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)

if __name__ == '__main__':
    
    # קריאת שני קובצי רצפי הייחוס
    crs_sequence = read_crs_file(resource_path('rCRS.txt'))
    rsrs_sequence = read_crs_file(resource_path('RSRS.txt'))

    # הגדרת החלון הראשי של התוכנה
    root = tk.Tk()
    root.title("mtDNA Sequence Comparison (+Reverse sequence tool) | By Rabbi Dr. Simcha Gershon Bohrer | Version: 18/08/2024")
    root.geometry("800x600")
    label = tk.Label(root, text="Enter/paste a mtDNA sequence for comparison (Caps-Lock On)", font="david 18 bold")
    label.pack(pady=5)
    entry = scrolledtext.ScrolledText(root, width=80, height=5)
    entry.pack(pady=5)

    # הגדרת כפתור שאומר שרצף המשתמש שהוזן הוא מעגלי כלומר קטע מסוף הרצף ולאחריו קטע מתחילת הרצף ולא מדובר ברצף ישר מההתחלה לסוף
    aligned_var = tk.IntVar()
    aligned_var.trace_add("write", on_reverse_change)
    aligned_check = tk.Checkbutton(root, text="The input sequence is circular - from HVS1 to HVS2", variable=aligned_var)
    #aligned_var.set(1)
    aligned_check.pack(pady=5)
    
    # הגדרת כפתור שאומר שרצף המשתמש שהוזן הוא ברוורס
    reverse_var = tk.IntVar()
    reverse_var.trace_add("write", on_reverse_change)
    reverse_check = tk.Checkbutton(root, text="Input sequence is Reverse complement", variable=reverse_var)
    reverse_check.pack(pady=5)

    # הגדרת כפתור שאומר להתעלם מ N ברצף
    ignore_n_var = tk.IntVar()
    ignore_n_var.trace_add("write", on_reverse_change)
    ignore_n_check = tk.Checkbutton(root, text="Ignore differences caused by 'N' in input sequence", variable=ignore_n_var)
    ignore_n_check.pack(pady=5)
    
    # הגדרת כפתור שאומר להפוך את הרצף בלבד ולא להשוות לרצץ הייחוס
    reverse_only_var = tk.IntVar()
    reverse_only_var.trace_add("write", on_reverse_change)
    reverse_only_check = tk.Checkbutton(root, text="Reverse/align the sequence only (=Reverse sequence tool)", variable=reverse_only_var)
    reverse_only_check.pack(pady=5)

    # הגדרת כפתור חישוב הנתונים
    compare_button = tk.Button(root, text="Compare", command=on_compare)
    compare_button.pack(pady=5)

    # הגדרת תיבת הטקסט עבור התוצאות
    result_text = scrolledtext.ScrolledText(root, width=80, height=20)
    result_text.pack(pady=5)
    result_text.config(state=tk.DISABLED)

    # הפעלת החלון בריצה קבועה
    root.mainloop()

