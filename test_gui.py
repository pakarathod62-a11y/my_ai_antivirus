import tkinter as tk

root = tk.Tk()
root.title("Test Window")
root.geometry("400x200")

label = tk.Label(root, text="नमस्ते! Tkinter बिल्कुल सही काम कर रहा है!", font=("Helvetica", 12))
label.pack(expand=True)

root.mainloop()
