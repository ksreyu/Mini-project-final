import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime
from tkinter import font

# Connect to SQLite database
conn = sqlite3.connect('final.db')
cursor = conn.cursor()

# Function to fetch available doctors
def fetch_doctors():
    cursor.execute("SELECT doctor_id, name, specialization FROM Doctor")
    return cursor.fetchall()

# Function to fetch available slots for a doctor on a specific date
def fetch_available_slots(doctor_id, appointment_date):
    appointment_date_obj = datetime.strptime(appointment_date, "%m/%d/%y")  
    formatted_date = appointment_date_obj.strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT ts.timeslot_id, ts.slot_time
        FROM TimeSlot ts
        LEFT JOIN Appointment a ON ts.timeslot_id = a.timeslot_id 
            AND a.appointment_date = ? 
            AND a.status = 'BOOKED'
        WHERE ts.doctor_id = ? 
        AND a.timeslot_id IS NULL
    """, (formatted_date, doctor_id))
    return cursor.fetchall()

def create_patient_window():
    global patient_window, doctor_combobox, cal, slot_combobox, appointment_combobox
    patient_window = tk.Tk()
    patient_window.title("Patient Dashboard")
    patient_window.geometry("800x600")
    patient_window.state('zoomed')

    label_font = ("Arial", 14, "bold")
    combobox_font = ("Arial", 12)
    button_font = ("Arial", 12)
    label_color = "#004d99"
    button_color = "#3399ff"
    bg_color = "#f2f2f2"

    patient_window.configure(bg=bg_color)

    # Select Doctor Label and Combobox
    tk.Label(patient_window, text="Select Doctor", font=label_font, fg=label_color, bg=bg_color).grid(row=0, column=0, padx=20, pady=10, sticky="w")
    doctor_combobox = ttk.Combobox(patient_window, font=combobox_font)
    doctor_combobox.grid(row=0, column=1, padx=20, pady=10, sticky="w")
    doctor_combobox["values"] = [f"{doc[0]}: Dr. {doc[1]} ({doc[2]})" for doc in fetch_doctors()]

    # Select Appointment Date Label and Calendar
    tk.Label(patient_window, text="Select Appointment Date", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=0, padx=20, pady=10, sticky="w")
    cal = Calendar(patient_window, selectmode="day")
    cal.grid(row=1, column=1, padx=20, pady=10, sticky="w")

    # Fetch Available Slots Button
    tk.Button(patient_window, text="Fetch Available Slots", font=button_font, bg=button_color, fg="white", command=update_slots).grid(row=2, column=0, columnspan=2, pady=10)

    # Available Slots Label and Combobox
    tk.Label(patient_window, text="Available Slots", font=label_font, fg=label_color, bg=bg_color).grid(row=3, column=0, padx=20, pady=10, sticky="w")
    slot_combobox = ttk.Combobox(patient_window, font=combobox_font)
    slot_combobox.grid(row=3, column=1, padx=20, pady=10, sticky="w")

    # Book Appointment Button
    tk.Button(patient_window, text="Book Appointment", font=button_font, bg=button_color, fg="white", command=save_appointment).grid(row=4, column=0, columnspan=2, pady=10)

    # View Appointments Button
    tk.Button(patient_window, text="View Appointments", font=button_font, bg=button_color, fg="white", command=view_patient_appointments).grid(row=5, column=2, padx=20, pady=10)

    # Cancel Appointment Section
    tk.Label(patient_window, text="Select Appointment to Cancel", font=label_font, fg=label_color, bg=bg_color).grid(row=5, column=0, padx=20, pady=10, sticky="w")
    appointment_combobox = ttk.Combobox(patient_window, font=combobox_font)
    appointment_combobox.grid(row=5, column=1, padx=20, pady=10, sticky="w")

    tk.Button(patient_window, text="View Appointments for Cancellation", font=button_font, bg=button_color, fg="white", command=view_appointment_for_cancellation).grid(row=6, column=0, columnspan=2, pady=10)
    tk.Button(patient_window, text="Cancel Appointment", font=button_font, bg=button_color, fg="white", command=delete_appointment).grid(row=7, column=0, columnspan=2, pady=10)

    # View Prescription Button
    tk.Button(patient_window, text="View Prescription", font=button_font, bg=button_color, fg="white", command=view_prescription).grid(row=8, column=0, columnspan=2, pady=10)

    # Sign Out Button
    tk.Button(patient_window, text="Sign Out", font=button_font, bg="red", fg="white", command=sign_out).grid(row=9, column=0, columnspan=2, pady=10)

    # Make all elements expand horizontally
    for i in range(3):
        patient_window.grid_columnconfigure(i, weight=1)

def view_patient_appointments():
    # Function to fetch and display patient appointments
    patient_id = logged_in_patient_id  # Assuming you have the patient ID stored
    cursor.execute("""
        SELECT a.appointment_id, d.name, a.appointment_date, ts.slot_time
        FROM Appointment a
        JOIN Doctor d ON a.doctor_id = d.doctor_id
        JOIN TimeSlot ts ON a.timeslot_id = ts.timeslot_id
        WHERE a.patient_id = ? AND a.status = 'BOOKED'
    """, (patient_id,))
    
    appointments = cursor.fetchall()
    if appointments:
        appointments_window = tk.Toplevel(patient_window)
        appointments_window.title("My Appointments")
        appointments_window.geometry("600x400")
        appointments_window.state("zoomed")

        # Styling
        header_font = ("Arial", 16, "bold")
        label_font = ("Arial", 12)
        label_color = "#004d99"
        bg_color = "#f2f2f2"

        appointments_window.configure(bg=bg_color)

        # Header Label
        tk.Label(appointments_window, text="My Appointments", font=header_font, fg=label_color, bg=bg_color).grid(row=0, column=0, columnspan=4, pady=10)

        # Appointment Headers
        tk.Label(appointments_window, text="Appointment ID", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=0, padx=10, pady=5)
        tk.Label(appointments_window, text="Doctor", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=1, padx=10, pady=5)
        tk.Label(appointments_window, text="Date", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=2, padx=10, pady=5)
        tk.Label(appointments_window, text="Time", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=3, padx=10, pady=5)

        # Displaying Appointments
        for idx, appointment in enumerate(appointments, start=2):
            appointment_id, doctor_name, appointment_date, slot_time = appointment
            
            tk.Label(appointments_window, text=appointment_id, font=label_font, bg=bg_color).grid(row=idx, column=0, padx=10, pady=5)
            tk.Label(appointments_window, text=doctor_name, font=label_font, bg=bg_color).grid(row=idx, column=1, padx=10, pady=5)
            tk.Label(appointments_window, text=appointment_date, font=label_font, bg=bg_color).grid(row=idx, column=2, padx=10, pady=5)
            tk.Label(appointments_window, text=slot_time, font=label_font, bg=bg_color).grid(row=idx, column=3, padx=10, pady=5)

    else:
        messagebox.showinfo("No Appointments", "You have no booked appointments.")

    


def create_dispensary_window():
    global dispensary_window
    dispensary_window = tk.Tk()
    dispensary_window.title("Dispensary Dashboard")
    dispensary_window.geometry("800x600")
    dispensary_window.state('zoomed')

    # Define common styling
    label_font = ("Arial", 16, "bold")
    button_font = ("Arial", 14)
    label_color = "#004d99"
    button_color = "#3399ff"
    bg_color = "#f2f2f2"

    # Set window background color
    dispensary_window.configure(bg=bg_color)

    # Welcome Label
    tk.Label(dispensary_window, text="Welcome to the Dispensary Dashboard", font=label_font, fg=label_color, bg=bg_color).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

    # Manage Inventory Button
    tk.Button(dispensary_window, text="Manage Inventory", font=button_font, bg=button_color, fg="white", command=manage_inventory).grid(row=1, column=0, columnspan=2, padx=20, pady=10)

   

    # Sign Out Button
    tk.Button(dispensary_window, text="Sign Out", font=button_font, bg="red", fg="white", command=sign_out).grid(row=3, column=0, columnspan=2, padx=20, pady=10)

    # Make all elements expand horizontally
    for i in range(2):
        dispensary_window.grid_columnconfigure(i, weight=1)




def manage_inventory():
    inventory_window = tk.Toplevel(dispensary_window)
    inventory_window.title("Update Inventory")
    inventory_window.geometry("400x300")
    inventory_window.state("zoomed")
    
    
    # Styling
    label_font = ("Arial", 12)
    button_font = ("Arial", 12)
    label_color = "#004d99"
    button_color = "#3399ff"
    bg_color = "#f2f2f2"

    inventory_window.configure(bg=bg_color)

    # Medicine Name Label and Entry
    tk.Label(inventory_window, text="Medicine Name", font=label_font, fg=label_color, bg=bg_color).grid(row=0, column=0, padx=20, pady=10, sticky="w")
    medicine_name_entry = tk.Entry(inventory_window, font=label_font)
    medicine_name_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

    # Quantity Label and Entry
    tk.Label(inventory_window, text="Quantity", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=0, padx=20, pady=10, sticky="w")
    quantity_entry = tk.Entry(inventory_window, font=label_font)
    quantity_entry.grid(row=1, column=1, padx=20, pady=10, sticky="w")

    def update_stock():
        try:
            medicine_name = medicine_name_entry.get()
            quantity = int(quantity_entry.get())

            cursor.execute("SELECT * FROM DispensaryInventory WHERE name = ?", (medicine_name,))
            if cursor.fetchone():
                cursor.execute("UPDATE DispensaryInventory SET quantity = quantity + ? WHERE name = ?", (quantity, medicine_name))
            else:
                cursor.execute("INSERT INTO DispensaryInventory (name, quantity) VALUES (?, ?)", (medicine_name, quantity))
            conn.commit()

            messagebox.showinfo("Success", "Stock updated successfully.")
            inventory_window.destroy()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid quantity.")

    # Update Stock Button
    tk.Button(inventory_window, text="Update Stock", command=update_stock, font=button_font, bg=button_color, fg="white").grid(row=2, column=0, columnspan=2, pady=20)

    # Make all elements expand horizontally
    inventory_window.grid_columnconfigure(0, weight=1)
    inventory_window.grid_columnconfigure(1, weight=1)




def create_doctor_window():
    global doctor_window, cal
    doctor_window = tk.Tk()
    doctor_window.title("Doctor Dashboard")
    doctor_window.geometry("800x600")
    doctor_window.state('zoomed')

    # Define common styling
    label_font = ("Arial", 16, "bold")
    button_font = ("Arial", 14)
    label_color = "#004d99"
    button_color = "#3399ff"
    bg_color = "#f2f2f2"

    # Set window background color
    doctor_window.configure(bg=bg_color)

    # Select Appointment Date Label and Calendar
    tk.Label(doctor_window, text="Select Appointment Date", font=label_font, fg=label_color, bg=bg_color).grid(row=0, column=0, padx=20, pady=20, sticky="w")
    cal = Calendar(doctor_window, selectmode="day")
    cal.grid(row=0, column=1, padx=20, pady=20, sticky="w")

    # View Appointments Button
    tk.Button(doctor_window, text="View Appointments", font=button_font, bg=button_color, fg="white", command=view_doctor_appointments).grid(row=1, column=0, columnspan=2, padx=20, pady=10)


    # Sign Out Button
    tk.Button(doctor_window, text="Sign Out", font=button_font, bg="red", fg="white", command=sign_out).grid(row=2, column=0, columnspan=2, padx=20, pady=10)

    # Make all elements expand horizontally
    for i in range(2):
        doctor_window.grid_columnconfigure(i, weight=1)





def update_appointment_display():
    # Logic to refresh the appointments list in both windows
    for widget in appointment_display_frame.winfo_children():
        widget.destroy()
    for appointment in appointments:  # Assume appointments is a list of current appointments
        Label(appointment_display_frame, text=appointment).pack()




# Function to handle user login
def login_user():
    global logged_in_patient_id, logged_in_doctor_id, logged_in_dispensary_id
    username = login_username_entry.get()
    password = login_password_entry.get()

    cursor.execute("SELECT patient_id FROM Patient WHERE username = ? AND password = ?", (username, password))
    patient = cursor.fetchone()

    cursor.execute("SELECT doctor_id FROM Doctor WHERE username = ? AND password = ?", (username, password))
    doctor = cursor.fetchone()

    cursor.execute("SELECT dispensary_id FROM Dispensary WHERE username = ? AND password = ?", (username, password))
    dispensary = cursor.fetchone()

    if patient:
        logged_in_patient_id = patient[0]
        login_window.destroy()
        create_patient_window()
    elif doctor:
        logged_in_doctor_id = doctor[0]
        login_window.destroy()
        create_doctor_window()
    elif dispensary:
        logged_in_dispensary_id = dispensary[0]
        login_window.destroy()
        create_dispensary_window()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def sign_out():
    # Check if patient window exists and is not destroyed
    if 'patient_window' in globals():
        try:
            if patient_window.winfo_exists():
                patient_window.destroy()
        except tk.TclError:
            pass  # Ignore error if the window is already destroyed

    # Check if doctor window exists and is not destroyed
    if 'doctor_window' in globals():
        try:
            if doctor_window.winfo_exists():
                doctor_window.destroy()
        except tk.TclError:
            pass  # Ignore error if the window is already destroyed

    # Check if dispensary window exists and is not destroyed
    if 'dispensary_window' in globals():
        try:
            if dispensary_window.winfo_exists():
                dispensary_window.destroy()
        except tk.TclError:
            pass  # Ignore error if the window is already destroyed

    # Log out and return to the main login window
    # Add code here to go back to the login screen if necessary
    create_login_window()


    
# Function to register the patient
import re  # Import the regular expression module

# Function to register the patient
def register_patient():
    name = name_entry.get()
    contact = contact_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    # Check if all fields are filled
    if not name or not contact or not username or not password:
        messagebox.showerror("Error", "All fields are required.")
        return

    # Validate the contact number (10 digits)
    if not re.match(r'^\d{10}$', contact):
        messagebox.showerror("Error", "Contact number must be exactly 10 digits.")
        return

    # Check if the username already exists
    cursor.execute("SELECT * FROM Patient WHERE username = ?", (username,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Username already exists.")
        return

    # Insert the new patient data
    try:
        cursor.execute("INSERT INTO Patient (name, contact_info, username, password) VALUES (?, ?, ?, ?)",
                       (name, contact, username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful. You can now log in.")
        registration_window.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to register: {e}")


# Function to create the login window
def create_login_window():
    global login_window, login_username_entry, login_password_entry
    login_window = tk.Tk()
    login_window.title("Clinic Management System")
    login_window.geometry("400x300")
    login_window.state('zoomed')

    # Set up a larger font and background color
    label_font = ("Arial", 16, "bold")
    entry_font = ("Arial", 14)
    
    # Configure the grid for the layout
    login_window.grid_columnconfigure(0, weight=1)
    login_window.grid_columnconfigure(1, weight=1)
    
    # Title label
    title_label = tk.Label(login_window, text="Clinic Management System", font=("Arial", 20, "bold"), bg="lightblue")
    title_label.grid(row=0, column=0, columnspan=2, pady=20, padx=10)

    # Username label and entry
    tk.Label(login_window, text="Username", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    login_username_entry = tk.Entry(login_window, font=entry_font)
    login_username_entry.grid(row=1, column=1, padx=10, pady=10)

    # Password label and entry
    tk.Label(login_window, text="Password", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    login_password_entry = tk.Entry(login_window, show="*", font=entry_font)
    login_password_entry.grid(row=2, column=1, padx=10, pady=10)

    # Login button
    tk.Button(login_window, text="Login", font=label_font, bg="green", fg="white", command=login_user).grid(row=3, column=0, columnspan=2, pady=20)

    # Register button
    tk.Button(login_window, text="Register", font=label_font, bg="blue", fg="white", command=create_registration_window).grid(row=4, column=0, columnspan=2, pady=10)
    tk.Button(login_window, text="Forgot Password?",font=label_font, bg="blue", fg="white", command=forgot_password ).grid(row=5, column=0, columnspan=2, pady=10)

    # Set window background color
    login_window.configure(bg="lightgray")



def forgot_password():
    def set_password():
        username = username_entry.get()
        new_password = password_entry.get()
        update_password_in_db(username, new_password)

    # Set up a larger font and background color
    label_font = ("Arial", 16, "bold")
    entry_font = ("Arial", 14)

    forgot_window = tk.Toplevel()
    forgot_window.state('zoomed')
    forgot_window.title("Forgot Password")

    forgot_window.grid_columnconfigure(0, weight=1)
    forgot_window.grid_columnconfigure(1, weight=1)

    tk.Label(forgot_window, text="Username:", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    username_entry = tk.Entry(forgot_window, font=entry_font)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(forgot_window, text="New Password:", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    password_entry = tk.Entry(forgot_window, show="*", font=entry_font)
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Button(forgot_window, text="Set Password", font=label_font, bg="green", fg="white", command=set_password).grid(row=3, column=0, columnspan=2, pady=20)
    tk.Button(forgot_window, text="Back", font=label_font, bg="blue", fg="white", command=forgot_window.destroy).grid(row=4, column=0, columnspan=2, pady=10)

# Function to update the password in the database
def update_password_in_db(username, new_password):
  
    # Check if the username exists
    cursor.execute("SELECT * FROM Patient WHERE username = ?", (username,))
    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Username not found.")
        conn.close()
        return

    # Update the password in the database
    try:
        cursor.execute("UPDATE Patient SET password = ? WHERE username = ?", (new_password, username))
        conn.commit()
        messagebox.showinfo("Success", "Password updated successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update password: {e}")
    finally:
        conn.close()


    



    
def create_registration_window():
    global registration_window, username_entry, password_entry, name_entry, contact_entry
    registration_window = tk.Toplevel(login_window)
    registration_window.title("Patient Registration")
    registration_window.geometry("400x400")
    registration_window.state('zoomed')

    # Set up larger font and background color
    label_font = ("Arial", 16, "bold")
    entry_font = ("Arial", 14)

    # Configure the grid layout for proper alignment
    registration_window.grid_columnconfigure(0, weight=1)
    registration_window.grid_columnconfigure(1, weight=1)
    
    # Title label
    title_label = tk.Label(registration_window, text="Patient Registration", font=("Arial", 20, "bold"), bg="lightblue")
    title_label.grid(row=0, column=0, columnspan=2, pady=20, padx=10)

    # Name label and entry
    tk.Label(registration_window, text="Name", font=label_font).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    name_entry = tk.Entry(registration_window, font=entry_font)
    name_entry.grid(row=1, column=1, padx=10, pady=10)

    # Contact info label and entry
    tk.Label(registration_window, text="Contact Info", font=label_font).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    contact_entry = tk.Entry(registration_window, font=entry_font)
    contact_entry.grid(row=2, column=1, padx=10, pady=10)

    # Username label and entry
    tk.Label(registration_window, text="Username", font=label_font).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    username_entry = tk.Entry(registration_window, font=entry_font)
    username_entry.grid(row=3, column=1, padx=10, pady=10)

    # Password label and entry
    tk.Label(registration_window, text="Password", font=label_font).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    password_entry = tk.Entry(registration_window, show="*", font=entry_font)
    password_entry.grid(row=4, column=1, padx=10, pady=10)

    # Register button
    tk.Button(registration_window, text="Register", font=label_font, bg="green", fg="white", command=register_patient).grid(row=5, column=0, columnspan=2, pady=20)

    # Close button
    tk.Button(registration_window, text="Close", font=label_font, bg="red", fg="white", command=registration_window.destroy).grid(row=6, column=0, columnspan=2, pady=10)

    # Set window background color
    registration_window.configure(bg="lightgray")



# Function to book an appointment and prevent booking the same slot again
def save_appointment():
    global logged_in_patient_id
    selected_doctor = doctor_combobox.get()

    if not selected_doctor:
        messagebox.showerror("Error", "Please select a doctor.")
        return

    doctor_id = int(selected_doctor.split(":")[0])
    appointment_date = cal.get_date()
    slot_time = slot_combobox.get()

    if not appointment_date or not slot_time:
        messagebox.showerror("Error", "All fields are required.")
        return

    try:
        formatted_date = datetime.strptime(appointment_date, '%m/%d/%y').strftime('%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Error", "Incorrect date format. Please select a date using the calendar.")
        return

    timeslot_id = int(slot_time.split(":")[0])

    # Check if the patient has already booked the same time slot with the same doctor on the same date
    cursor.execute("""
        SELECT COUNT(*)
        FROM Appointment
        WHERE patient_id = ? AND doctor_id = ? AND timeslot_id = ? AND appointment_date = ? AND status = 'BOOKED'
    """, (logged_in_patient_id, doctor_id, timeslot_id, formatted_date))
    
    if cursor.fetchone()[0] > 0:
        messagebox.showerror("Error", "You have already booked this time slot with the same doctor.")
        return

    # Proceed with booking the appointment if no duplicate is found
    try:
        cursor.execute(
            "INSERT INTO Appointment (doctor_id, patient_id, timeslot_id, appointment_date, status) "
            "VALUES (?, ?, ?, ?, 'BOOKED')",
            (doctor_id, logged_in_patient_id, timeslot_id, formatted_date)
        )
        conn.commit()
        messagebox.showinfo("Success", "Appointment booked successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to book appointment: {e}")


# Function to view appointments (including canceled ones)
def view_appointment():
    cursor.execute("""
        SELECT a.appointment_id, a.appointment_date, ts.slot_time, d.name, a.status
        FROM Appointment a
        JOIN TimeSlot ts ON a.timeslot_id = ts.timeslot_id
        JOIN Doctor d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ?
    """, (logged_in_patient_id,))
    appointments = cursor.fetchall()

    if appointments:
        appt_text = "\n".join([f"ID: {appt[0]}, Date: {appt[1]}, Time: {appt[2]}, Doctor: {appt[3]}, Status: {appt[4]}" for appt in appointments])
        messagebox.showinfo("Appointments", appt_text)
    else:
        messagebox.showinfo("No Appointments", "No appointments found.")

# Function to view appointments for cancellation
def view_appointment_for_cancellation():
    global appointment_combobox
    cursor.execute("""
        SELECT a.appointment_id, a.appointment_date, ts.slot_time, d.name, a.status
        FROM Appointment a
        JOIN TimeSlot ts ON a.timeslot_id = ts.timeslot_id
        JOIN Doctor d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ? AND a.status = 'BOOKED'
    """, (logged_in_patient_id,))
    appointments = cursor.fetchall()

    if appointments:
        appointment_combobox["values"] = [f"{appt[0]}: {appt[1]} - {appt[2]} with Dr. {appt[3]}" for appt in appointments]
        if len(appointments) > 0:
            appointment_combobox.current(0)
    else:
        messagebox.showinfo("No Appointments", "No booked appointments available for cancellation.")

# Function to cancel the selected appointment
def delete_appointment():
    selected_appointment = appointment_combobox.get()

    if not selected_appointment:
        messagebox.showerror("Error", "Please select an appointment to cancel.")
        return

    # Extract the appointment ID from the selected value
    appointment_id = int(selected_appointment.split(":")[0])

    try:
        # Update the status of the selected appointment to 'CANCELLED'
        cursor.execute("UPDATE Appointment SET status = 'CANCELLED' WHERE appointment_id = ?", (appointment_id,))
        conn.commit()

        messagebox.showinfo("Success", "Appointment canceled successfully.")
        view_appointment_for_cancellation()  # Refresh the list after cancellation
    except Exception as e:
        messagebox.showerror("Error", f"Failed to cancel the appointment: {e}")



def view_doctor_appointments():
    doctor_id = logged_in_doctor_id
    selected_date = cal.get_date()
    formatted_date = datetime.strptime(selected_date, "%m/%d/%y").strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT a.appointment_id, p.name, p.contact_info, ts.slot_time
        FROM Appointment a
        JOIN Patient p ON a.patient_id = p.patient_id
        JOIN TimeSlot ts ON a.timeslot_id = ts.timeslot_id
        WHERE a.doctor_id = ? AND a.appointment_date = ? AND a.status = 'BOOKED'
    """, (doctor_id, formatted_date))
    appointments = cursor.fetchall()

    # Define styling
    label_font = ("Arial", 14)
    button_font = ("Arial", 12, "bold")
    label_color = "#004d99"
    button_color = "#3399ff"
    bg_color = "#f2f2f2"

    # Clear previous appointment display (if any)
    for widget in doctor_window.winfo_children():
        if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
            widget.grid_forget()

    if appointments:
        for idx, appt in enumerate(appointments):
            appointment_id, patient_name, contact_info, slot_time = appt
            appt_str = f"Patient: {patient_name}, Contact: {contact_info}, Slot: {slot_time}"

            # Display appointment details
            tk.Label(doctor_window, text=appt_str, font=label_font, fg=label_color, bg=bg_color).grid(row=idx, column=0, padx=10, pady=5, sticky="w")

            # Prescribe button next to appointment details
            tk.Button(doctor_window, text="Prescribe", font=button_font, bg=button_color, fg="white", 
                      command=lambda appt_id=appointment_id: prescribe_medicine(appt_id)).grid(row=idx, column=1, padx=10, pady=5, sticky="e")

    else:
        messagebox.showinfo("No Appointments", "No appointments found for the selected date.")

# Prescribe medicine function stays the same as before, but we might improve its layout too.
def prescribe_medicine(appointment_id):
    prescription_window = tk.Toplevel(doctor_window)
    prescription_window.title("Prescribe Medicine")
    prescription_window.state("zoomed")


    # Define common styling
    label_font = ("Arial", 14)
    button_font = ("Arial", 12, "bold")
    entry_font = ("Arial", 12)
    label_color = "#004d99"
    button_color = "#3399ff"
    bg_color = "#f2f2f2"

    prescription_window.configure(bg=bg_color)

    tk.Label(prescription_window, text="Medicine:", font=label_font, fg=label_color, bg=bg_color).grid(row=0, column=0, padx=10, pady=10)
    cursor.execute("SELECT name FROM DispensaryInventory WHERE quantity > 0")
    medicines = cursor.fetchall()
    medicine_combobox = ttk.Combobox(prescription_window, font=entry_font)
    medicine_combobox["values"] = [med[0] for med in medicines]
    medicine_combobox.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(prescription_window, text="Dosage (e.g., 1-0-1):", font=label_font, fg=label_color, bg=bg_color).grid(row=1, column=0, padx=10, pady=10)
    dosage_combobox = ttk.Combobox(prescription_window, font=entry_font)
    dosage_combobox["values"] = ["1-0-1", "1-0-0", "1-1-1"]
    dosage_combobox.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(prescription_window, text="Quantity:", font=label_font, fg=label_color, bg=bg_color).grid(row=2, column=0, padx=10, pady=10)
    quantity_entry = tk.Entry(prescription_window, font=entry_font)
    quantity_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(prescription_window, text="Notes:", font=label_font, fg=label_color, bg=bg_color).grid(row=3, column=0, padx=10, pady=10)
    notes_entry = tk.Text(prescription_window, height=5, width=30, font=entry_font)
    notes_entry.grid(row=3, column=1, padx=10, pady=10)

    # Save Prescription Button
    tk.Button(prescription_window, text="Save Prescription", font=button_font, bg=button_color, fg="white", 
              command=lambda: save_prescription(appointment_id, medicine_combobox.get(), dosage_combobox.get(), quantity_entry.get(), notes_entry.get("1.0", tk.END).strip())
             ).grid(row=4, column=0, columnspan=2, padx=10, pady=20)

def save_prescription(appointment_id, medicine, dosage, quantity, notes):
    # Check if quantity is provided and valid
    if not quantity:
        messagebox.showerror("Error", "Quantity cannot be empty.")
        return

    try:
        quantity = int(quantity)  # Ensure quantity is an integer
    except ValueError:
        messagebox.showerror("Error", "Invalid quantity. Please enter a valid number.")
        return

    if not medicine:
        messagebox.showerror("Error", "Please select a medicine.")
        return

    if not dosage:
        messagebox.showerror("Error", "Please select a dosage.")
        return

    # Save prescription and update dispensary stock
    cursor.execute("INSERT INTO Prescription (appointment_id, medicine, dosage, quantity, notes) VALUES (?, ?, ?, ?, ?)",
                   (appointment_id, medicine, dosage, quantity, notes))
    conn.commit()

    cursor.execute("UPDATE DispensaryInventory SET quantity = quantity - ? WHERE name = ?", (quantity, medicine))
    conn.commit()
   

    messagebox.showinfo("Success", "Prescription saved.")
    
    





def view_prescription():
    cursor.execute("""
        SELECT p.medicine, p.dosage, p.quantity, p.notes
        FROM Prescription p
        JOIN Appointment a ON p.appointment_id = a.appointment_id
        WHERE a.patient_id = ?
    """, (logged_in_patient_id,))
    prescriptions = cursor.fetchall()

    if prescriptions:
        pres_window = tk.Toplevel(patient_window)
        pres_window.title("Prescriptions")

        # Set up a grid layout
        for i, pres in enumerate(prescriptions):
            med, dosage, qty, notes = pres
            pres_str = f"Medicine: {med}, Dosage: {dosage}, Quantity: {qty}, Notes: {notes}"

            # Create a label with a larger font and color
            label_font = font.Font(size=12, weight='bold')  # Adjust size and weight
            label = tk.Label(pres_window, text=pres_str, font=label_font, fg="blue")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")  # Align left

        # Create a close button
        close_button = tk.Button(pres_window, text="Close", command=pres_window.destroy, font=label_font, bg="lightgray")
        close_button.grid(row=len(prescriptions), column=0, pady=10)
    else:
        messagebox.showinfo("No Prescriptions", "No prescriptions found.")




# Function to update available slots and prevent booking in the past
def update_slots():
    selected_doctor = doctor_combobox.get()
    if not selected_doctor:
        messagebox.showerror("Error", "Please select a doctor.")
        return

    doctor_id = int(selected_doctor.split(":")[0])
    selected_date = cal.get_date()

    # Convert the selected date to a datetime object
    selected_date_obj = datetime.strptime(selected_date, '%m/%d/%y')
    current_date_obj = datetime.now()

    # Check if the selected date is in the past
    if selected_date_obj < current_date_obj:
        messagebox.showerror("Error", "Cannot book appointments in the past.")
        return

    # Fetch available slots for the selected doctor and date
    available_slots = fetch_available_slots(doctor_id, selected_date)

    slot_combobox["values"] = [f"{slot[0]}: {slot[1]}" for slot in available_slots]
    if available_slots:
        slot_combobox.current(0)  # Select the first available slot
    else:
        messagebox.showinfo("No Slots Available", "No available slots for the selected date.")


# Start the application
create_login_window()
tk.mainloop()
