import tkinter as tk
from tkinter import ttk
import subprocess
import os
import webbrowser

def update_dropdowns():
    dataset_files = os.listdir('datasets')
    dataset_combobox['values'] = dataset_files
    pipeline_files = os.listdir('pipelines')
    pipeline_combobox['values'] = pipeline_files

def run_script():
    dataset = dataset_combobox.get()
    pipeline = pipeline_combobox.get()
    frac = frac_entry.get()
    granularity = granularity_combobox.get()

    command = f"python prolit_run.py --dataset datasets/{dataset} --pipeline pipelines/{pipeline} --frac {frac} --granularity_level {granularity}"
    subprocess.run(command, shell=True)

def open_neo4j_browser():
    webbrowser.open("http://localhost:7474/browser/")

def run_notebook():
    # Adjust the path to your notebook as needed
    notebook_path = "NaturalLanguageGraphExploitation/text2cypher_approach.ipynb"
    # Command to execute all cells in the notebook
    command = f"jupyter nbconvert --to notebook --execute {notebook_path} --output {notebook_path}"
    subprocess.run(command, shell=True)
    print("Notebook executed successfully.")

app = tk.Tk()
app.title("PROLIT")

# Set the theme color to blue and increase font size for better visibility
app.configure(bg='#34495e')
font_style = ('Helvetica', 12)

# Dropdown for dataset files
tk.Label(app, text="Choose Dataset:", bg='#34495e', fg='white', font=font_style).pack(pady=10)
dataset_combobox = ttk.Combobox(app, width=47, font=font_style)
dataset_combobox.pack(pady=5)

# Dropdown for pipeline files
tk.Label(app, text="Choose Pipeline:", bg='#34495e', fg='white', font=font_style).pack(pady=10)
pipeline_combobox = ttk.Combobox(app, width=47, font=font_style)
pipeline_combobox.pack(pady=5)

# Entry for fraction
tk.Label(app, text="Fraction:", bg='#34495e', fg='white', font=font_style).pack(pady=10)
frac_entry = tk.Entry(app, width=20, font=font_style)
frac_entry.pack(pady=5)

# Combobox for granularity level
tk.Label(app, text="Granularity Level:", bg='#34495e', fg='white', font=font_style).pack(pady=10)
granularity_combobox = ttk.Combobox(app, width=20, font=font_style, values=[1, 2, 3, 4])
granularity_combobox.pack(pady=5)

# Button to update dropdowns
update_button = tk.Button(app, text="Update Lists", command=update_dropdowns, bg='#3498db', fg='white', font=font_style)
update_button.pack(pady=10)

# Button to execute the script
run_button = tk.Button(app, text="Run Script", command=run_script, bg='#3498db', fg='white', font=font_style)
run_button.pack(pady=10)

# Button to open Neo4j Browser
neo4j_button = tk.Button(app, text="Open Neo4j Browser", command=open_neo4j_browser, bg='#3498db', fg='white', font=font_style)
neo4j_button.pack(pady=10)

# Update dropdowns on startup
update_dropdowns()

app.mainloop()
