import customtkinter as ctk
import threading
import requests
import time
from datetime import datetime
import random

last_rfid = None
ARDUINO_SERVER_URL = "http://172.20.10.12:8080/rfid"  # Arduino IP og port (avhenger av nettverket)
PHP_SERVER_URL = "http://172.20.10.7/attendance_system/log_attendance.php"

# Sitater for motivasjon og oppmuntring
morning_quotes = [
    "Rise and shine! Let's make today amazing!",
    "Every morning is a new opportunity to chase your dreams.",
    "Success is built one productive day at a time.",
    "Dream big, work hard, and stay focused.",
    "The early bird gets the worm, but the motivated bird gets everything!"
]

checkout_quotes = [
    "Great work today! You’re one step closer to your goals.",
    "Celebrate your wins, no matter how small!",
    "Your dedication is your superpower. Keep it up!",
    "Effort is never wasted. Today’s sweat is tomorrow’s success.",
    "Your perseverance is paying off. Stay motivated!"
]

# Get tilfeldig sitater basert på type (morgen eller utsjekk)
def get_random_quote(quote_type):
    if quote_type == "morning":
        return random.choice(morning_quotes)
    elif quote_type == "checkout":
        return random.choice(checkout_quotes)

# Funksjon for å håndtere RFID-skanning
def scan_rfid():
    global last_rfid

    # Oppdater GUI til "jobber-status"
    instructions.set("Scanning kortet ditt... vennligst vent.")
    progress_bar.start()  # denne Start progressbaren bare når skanningen begynner

    def process_rfid():
        global last_rfid
        try:
            # Send HTTP GET-forespørsel til Arduino-serveren for å hente RFID-data fra kortleseren (RFID - RC522)
            response = requests.get(ARDUINO_SERVER_URL, timeout=5)
            response.raise_for_status()
            rfid_data = response.text.strip()
            print(f"Respons fra Arduino: {rfid_data}")

            if "Siste RFID:" in rfid_data:
                rfid = rfid_data.split(": ")[1].strip()

                # Sjekk om RFID er ny (for å unngå duplikater under samme skanning)
                if rfid == last_rfid:
                    print("Duplikat RFID oppdaget. Ignorerer.")
                    instructions.set("Kort allerede registrert. Vennligst prøv igjen.")
                    return

                last_rfid = rfid  # Oppdater siste RFID (for å unngå duplikater som scanner samme kort flere ganger)

                # Fortsett med behandling av RFID som vanlig
                payload = {'rfid_tag': rfid}
                response = requests.post(PHP_SERVER_URL, data=payload, timeout=5)
                response_data = response.json()

                if response_data.get("status") == "success":
                    name = response_data.get("name", "Ukjent medlem")
                    message = response_data.get("message", "Ingen melding")
                    total_hours = response_data.get("total_hours", 0)

                    instructions.set(message)
                    welcome_label.set(f"Velkommen, {name}!")
                    total_hours_label.set(f"Totale timer: {total_hours:.2f}")
                    datetime_label.set(f"Dato og tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    quote.set(get_random_quote("morning" if "Innsjekk" in message else "checkout"))
                else:
                    ctk.CTkMessagebox(title="Feil", message=response_data.get("message", "Ukjent feil"), icon="warning")
            else:
                print("Ugyldig respons fra Arduino. Ignorerer.")
        except requests.exceptions.RequestException as e:
            instructions.set("Kunne ikke koble til serveren.")
            print(f"Feil: {e}")
        finally:
            progress_bar.stop()  # Stopp progressbaren uansett utfall 
            root.after(3000, scan_rfid)  # Gjenta skanningen etter en kort forsinkelse

    # Starter en ny tråd for å behandle RFID
    threading.Thread(target=process_rfid).start()

# Funksjon for å åpne manuell logging-skjerm
def open_manual_logging_screen():
    for widget in root.winfo_children():
        widget.pack_forget()

    # Manuell logging-seksjon
    ctk.CTkLabel(root, text="Manuell innsjekk/utsjekk", font=("Helvetica", 18, "bold")).pack(pady=20)

    # Tekstfelt for studentnummer
    student_number_entry = ctk.CTkEntry(root, placeholder_text="Skriv inn studentnummer")
    student_number_entry.pack(pady=10)

    # Tekstfelt for RFID
    rfid_entry = ctk.CTkEntry(root, placeholder_text="Skriv inn RFID")
    rfid_entry.pack(pady=10)

    def log_manually():
        student_number = student_number_entry.get().strip()
        rfid_tag = rfid_entry.get().strip()

        if not student_number and not rfid_tag:
            ctk.CTkMessagebox(title="Feil", message="Vennligst fyll inn enten studentnummer eller RFID.", icon="warning")
            return

        payload = {}
        if student_number:
            payload['student_number'] = student_number
        if rfid_tag:
            payload['rfid_tag'] = rfid_tag

        try:
            response = requests.post(PHP_SERVER_URL, data=payload, timeout=5)
            response_data = response.json()

            if response_data.get("status") == "success":
                ctk.CTkMessagebox(title="Suksess", message=response_data.get("message"), icon="check")
            else:
                ctk.CTkMessagebox(title="Feil", message=response_data.get("message"), icon="warning")
        except requests.exceptions.RequestException as e:
            print(f"Feil ved forespørsel: {e}")
            ctk.CTkMessagebox(title="Feil", message="Kunne ikke koble til serveren.", icon="warning")

    # Logg manuelt-knapp
    ctk.CTkButton(root, text="Logg inn manuelt", command=log_manually).pack(pady=20)

    # Tilbake-knapp
    ctk.CTkButton(root, text="Tilbake", command=show_main_screen).pack(pady=10)

# Funksjon for å vise hovedskjermen
def show_main_screen():
    for widget in root.winfo_children():
        widget.pack_forget()

    instructions_label.pack(pady=20)
    progress_bar.pack(pady=20)
    manual_log_button.pack(pady=10)

# Opprett GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Medlemsportal")
root.geometry("700x600")

# Instruksjoner
instructions = ctk.StringVar(value="Velkommen! Scan kortet ditt for å sjekke inn/ut.")
instructions_label = ctk.CTkLabel(root, textvariable=instructions, font=("Helvetica", 18), text_color="#00ADEF", wraplength=600)

# Progress Bar
progress_bar = ctk.CTkProgressBar(root, orientation="horizontal", mode="indeterminate", width=500)

# Logg inn manuelt-knapp 
manual_log_button = ctk.CTkButton(root, text="Logg manuelt", command=open_manual_logging_screen)

# Start GUI
show_main_screen()
root.after(1000, scan_rfid)
root.mainloop()
