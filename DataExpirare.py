import tkinter
import customtkinter
import os
import threading
from datetime import datetime
from tkinter import messagebox
from win10toast import ToastNotifier
import pystray
from pystray import MenuItem as Item
from PIL import Image

# Initialize toaster for notifications
toaster = ToastNotifier()

# Set to keep track of notified products
notified_products = set()


# Function to add the product and save to file
def add_date():
    name = name_entry.get()
    exp_date = date_entry.get()

    # Automatically format the date to YYYY-MM
    if len(exp_date) == 6 and exp_date.isdigit():
        exp_date = f"{exp_date[:4]}-{exp_date[4:]}"

    # Validate date format
    try:
        datetime.strptime(exp_date, '%Y-%m')
    except ValueError:
        messagebox.showerror("Data invalida", "Data trebuie sa fie in formatul YYYYMM sau YYYY-MM.")
        return

    # Adds product to listbox
    contacts_listbox.insert(tkinter.END, name + " - " + exp_date)

    # Save product to file
    save_product_to_file(name, exp_date)

    # Clears entries data
    name_entry.delete(0, tkinter.END)
    date_entry.delete(0, tkinter.END)

    # Check for upcoming expirations
    check_expirations()


# Function to save product to file
def save_product_to_file(name, exp_date):
    with open('products.txt', 'a') as file:
        file.write(f'{name} - {exp_date}\n')


# Function to load products from file
def load_products_from_file():
    if os.path.exists('products.txt'):
        with open('products.txt', 'r') as file:
            for line in file:
                contacts_listbox.insert(tkinter.END, line.strip())


# Function to check expiration dates and notify
def check_expirations():
    for i in range(contacts_listbox.size()):
        line = contacts_listbox.get(i)
        check_expiration_for_line(line)


def check_expiration_for_line(line):
    try:
        name, exp_date = line.split(' - ')
        exp_date = datetime.strptime(exp_date, '%Y-%m')
        current_date = datetime.now()
        days_until_expiration = (exp_date - current_date).days
        if 0 <= days_until_expiration <= 30:
            # Check if the product has already been notified
            if (name, exp_date) not in notified_products:
                # Show a warning message
                messagebox.showwarning("Expira curand", f"Produsul '{name}' va expira luna urmatoare!")
                # Show a Windows notification using win10toast in a separate thread
                threading.Thread(target=send_notification, args=(name,), daemon=True).start()
                # Add the product to the set of notified products
                notified_products.add((name, exp_date))
    except ValueError:
        pass


def send_notification(name):
    toaster.show_toast(
        "Expira curand",
        f"Produsul '{name}' va expira luna urmatoare!",
        icon_path='icon.ico',  # Use the icon for the notification
        duration=10  # Notification stays for 10 seconds
    )


def quit_application(icon, item):
    icon.stop()
    window.quit()


def show_window(icon, item):
    icon.stop()
    window.after(0, window.deiconify)


def hide_window():
    window.withdraw()
    image = Image.open("icon.png")  # Load the icon image for the tray
    menu = (Item('Deschide', show_window), Item('Inchide', quit_application))
    icon = pystray.Icon("name", image, "Data Expirare", menu)
    threading.Thread(target=icon.run, daemon=True).start()


# Function to edit a product
def edit_product():
    try:
        selected_index = contacts_listbox.curselection()[0]
        selected_text = contacts_listbox.get(selected_index)
        name, exp_date = selected_text.split(' - ')
        name_entry.delete(0, tkinter.END)
        name_entry.insert(0, name)
        date_entry.delete(0, tkinter.END)
        date_entry.insert(0, exp_date.replace('-', ''))
        contacts_listbox.delete(selected_index)
        remove_product_from_file(selected_text)
    except IndexError:
        messagebox.showerror("Eroare", "Selectati un produs pentru a-l edita.")


# Function to delete a product
def delete_product():
    try:
        selected_index = contacts_listbox.curselection()[0]
        selected_text = contacts_listbox.get(selected_index)
        contacts_listbox.delete(selected_index)
        remove_product_from_file(selected_text)
    except IndexError:
        messagebox.showerror("Eroare", "Selectati un produs pentru a-l sterge.")


# Function to remove product from file
def remove_product_from_file(product_line):
    if os.path.exists('products.txt'):
        with open('products.txt', 'r') as file:
            lines = file.readlines()
        with open('products.txt', 'w') as file:
            for line in lines:
                if line.strip() != product_line:
                    file.write(line)


# Creates the main window
window = tkinter.Tk()
window.configure(bg='#262626')
window.title("Data Expirare")
window.iconbitmap('icon.ico')  # Set the window icon

# Handle closing of the window
window.protocol("WM_DELETE_WINDOW", hide_window)

# Creates a frame to hold the widgets
frame = tkinter.Frame(window, background='#262626')
frame.pack()

# Creates labels for name and date
name_label = customtkinter.CTkLabel(
    master=frame,
    text="Produs:",
    text_color="black",
    width=120,
    height=25,
    fg_color=("white", "gray75"),
    bg_color="#262626",
    corner_radius=8)
name_label.grid(row=0, column=0, padx=7, pady=10)

tel_label = customtkinter.CTkLabel(
    master=frame,
    text="Data (YYYYMM):",
    text_color="black",
    width=120,
    height=25,
    fg_color=("white", "gray75"),
    bg_color="#262626",
    corner_radius=8)
tel_label.grid(row=1, column=0)

# Creates entries for name and date
name_entry = customtkinter.CTkEntry(
    master=frame,
    text_color="white",
    border_width=2,
    border_color="#d3d3d3",
    bg_color="#262626",
    fg_color="#262626",
    corner_radius=5)
name_entry.grid(row=0, column=1, padx=7)

date_entry = customtkinter.CTkEntry(
    master=frame,
    text_color="white",
    border_width=2,
    border_color="#d3d3d3",
    bg_color="#262626",
    fg_color="#262626",
    corner_radius=5)
date_entry.grid(row=1, column=1)

# Creates a button to add a product date
add_button = customtkinter.CTkButton(
    master=frame,
    command=add_date,
    text="Salveaza",
    text_color="white",
    hover=True,
    hover_color="black",
    height=40,
    width=120,
    border_width=2,
    corner_radius=20,
    border_color="black",
    bg_color="#262626",
    fg_color="#262626",
)
add_button.grid(row=2, column=0, columnspan=2, pady=15)

# Create buttons to edit and delete selected product
edit_button = customtkinter.CTkButton(
    master=frame,
    command=edit_product,
    text="Editeaza",
    text_color="white",
    hover=True,
    hover_color="black",
    height=40,
    width=60,
    border_width=2,
    corner_radius=20,
    border_color="black",
    bg_color="#262626",
    fg_color="#262626",
)
edit_button.grid(row=3, column=0, padx=5, pady=5)

delete_button = customtkinter.CTkButton(
    master=frame,
    command=delete_product,
    text="Sterge",
    text_color="white",
    hover=True,
    hover_color="black",
    height=40,
    width=60,
    border_width=2,
    corner_radius=20,
    border_color="black",
    bg_color="#262626",
    fg_color="#262626",
)
delete_button.grid(row=3, column=1, padx=5, pady=5)

# Creates a listbox to show the products
contacts_listbox = tkinter.Listbox(window, bg="#262626", fg="white")
contacts_listbox.pack()

# Load products from file when the application starts
load_products_from_file()

# Check expirations when the application starts
check_expirations()

window.mainloop()
