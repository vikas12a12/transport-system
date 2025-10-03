import streamlit as st
import pandas as pd
import random
from datetime import datetime
import os
import folium
from streamlit_folium import st_folium
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# ---------------- CONFIG ----------------
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "bookings.csv")

DRIVERS = [
    {"name": "Amit", "vehicle": "Swift Dzire - KA01AB1234"},
    {"name": "Rahul", "vehicle": "Innova - KA02CD5678"},
    {"name": "Sonal", "vehicle": "Tiago - KA03EF9012"},
    {"name": "Priya", "vehicle": "Ertiga - KA04GH3456"},
]

BASE_FARE = 40          # Base fare in INR
PER_KM = 12             # per km charge in INR
PER_PASSENGER = 10      # extra per passenger (if >1)

# ---------------- SETUP -----------------
st.set_page_config(page_title="Transport System", page_icon="🚖", layout="wide")
st.title("🚖 Transport Booking & Tracking System (All-in-One)")

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.isfile(DATA_FILE):
    pd.DataFrame(columns=["booking_id","name","phone","origin","destination",
                          "passengers","fare","driver_name","vehicle","status","booking_time"]) \
      .to_csv(DATA_FILE, index=False)

# ---------------- AUTH ------------------
with open("auth/auth_config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status:
    st.success(f"Welcome, {name}!")
elif auth_status is False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please login to access features")

# ---------------- NAVIGATION ----------------
pages = ["Home","Book Ride","Track Ride","Admin Dashboard","About"]
if auth_status:
    choice = st.sidebar.selectbox("Navigation", pages)
    
    # Load bookings
    bookings = pd.read_csv(DATA_FILE)
    
    # --------------- HOME -----------------
    if choice == "Home":
        st.subheader("🏠 Home")
        st.markdown("Welcome to the **Transport Booking System**.")
        st.image("https://img.freepik.com/free-vector/taxi-app-concept_23-2148486306.jpg", use_column_width=True)
        st.markdown("""
        **Menu Options**:
        - Book Ride
        - Track Ride
        - Admin Dashboard
        - About / Help
        """)

    # --------------- BOOK RIDE -----------------
    elif choice == "Book Ride":
        st.subheader("📌 Book Your Ride")
        user_name = st.text_input("Full Name", value=name)
        phone = st.text_input("Phone Number")
        origin = st.text_input("Origin")
        destination = st.text_input("Destination")
        passengers = st.number_input("Number of Passengers", min_value=1, max_value=10, value=1)
        
        if st.button("Book Ride"):
            if user_name and phone and origin and destination:
                fare = BASE_FARE + random.randint(5,15)*passengers  # simplified fare
                driver = random.choice(DRIVERS)
                booking_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                booking_id = int(datetime.now().timestamp())
                
                new_row = {
                    "booking_id": booking_id,
                    "name": user_name,
                    "phone": phone,
                    "origin": origin,
                    "destination": destination,
                    "passengers": passengers,
                    "fare": fare,
                    "driver_name": driver["name"],
                    "vehicle": driver["vehicle"],
                    "status": "assigned",
                    "booking_time": booking_time
                }
                
                bookings = pd.concat([bookings, pd.DataFrame([new_row])], ignore_index=True)
                bookings.to_csv(DATA_FILE, index=False)
                
                st.success(f"✅ Ride booked! Driver {driver['name']} assigned. Fare: ₹{fare}")
                
                # Display simple route map (fake coordinates demo)
                m = folium.Map(location=[28.61,77.23], zoom_start=12)
                folium.Marker([28.61,77.23], tooltip="Origin").add_to(m)
                folium.Marker([28.65,77.25], tooltip="Destination").add_to(m)
                folium.PolyLine(locations=[[28.61,77.23],[28.65,77.25]], color="blue").add_to(m)
                st_folium(m, width=700, height=450)
            else:
                st.error("Please fill all fields.")

    # --------------- TRACK RIDE -----------------
    elif choice == "Track Ride":
        st.subheader("📍 Track Your Ride")
        user_bookings = bookings[bookings["name"]==name]
        if not user_bookings.empty:
            last = user_bookings.iloc[-1]
            st.write(f"Driver: {last['driver_name']}")
            st.write(f"From: {last['origin']} → To: {last['destination']}")
            
            m = folium.Map(location=[28.61,77.23], zoom_start=12)
            folium.Marker([28.61,77.23], tooltip="Origin").add_to(m)
            folium.Marker([28.65,77.25], tooltip="Destination").add_to(m)
            folium.PolyLine(locations=[[28.61,77.23],[28.65,77.25]], color="blue").add_to(m)
            st_folium(m, width=700, height=450)
        else:
            st.info("No bookings found.")

    # --------------- ADMIN DASHBOARD -----------------
    elif choice == "Admin Dashboard":
        if username != "admin":
            st.error("Access denied! Admins only.")
        else:
            st.subheader("🛠️ Admin Dashboard")
            st.write("Total Bookings:", len(bookings))
            st.write("Total Revenue:", bookings["fare"].sum() if not bookings.empty else 0)
            st.dataframe(bookings)
            
            if st.button("Mark all assigned → completed"):
                bookings.loc[bookings["status"]=="assigned","status"]="completed"
                bookings.to_csv(DATA_FILE, index=False)
                st.success("Updated statuses to completed.")

    # --------------- ABOUT -----------------
    elif choice == "About":
        st.subheader("ℹ️ About Us")
        st.markdown("""
        This transport booking system is a **demo project using Streamlit**.
        - Booking, Tracking, Admin Dashboard in one file.
        - Made by **Vikas Kalyan & Friend**
        - Hosting: Streamlit Cloud / GitHub
        """)
else:
    st.warning("Login required to access features")
