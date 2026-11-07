
import streamlit as st
import folium
from streamlit_folium import st_folium
import math
from datetime import datetime

# ==================================
# PAGE CONFIGURATION
# ==================================

st.set_page_config(
    page_title="Smart Dustbin System",
    page_icon="♻️",
    layout="wide"
)

# ==================================
# GREEN BACKGROUND
# ==================================

st.markdown("""
<style>
.stApp {
    background-color: #E8F5E9;
}

h1, h2, h3 {
    color: #14532D;
}

[data-testid="stSidebar"] {
    background-color: #C8E6C9;
}

div.stButton > button {
    background-color: #15803D;
    color: white;
    border-radius: 10px;
    border: none;
    height: 45px;
    font-weight: bold;
}

div.stButton > button:hover {
    background-color: #166534;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# ==================================
# DUSTBIN DETAILS
# ==================================

BIN_ID = "BIN-001"

LATITUDE = 22.150000
LONGITUDE = 84.270000

# Initial garbage level
if "garbage_level" not in st.session_state:
    st.session_state.garbage_level = 0

if "sms_received" not in st.session_state:
    st.session_state.sms_received = False

if "last_update" not in st.session_state:
    st.session_state.last_update = "Not updated"

if "sms_message" not in st.session_state:
    st.session_state.sms_message = "No SMS received yet"


# ==================================
# DISTANCE CALCULATION
# ==================================

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2)**2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2)**2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ==================================
# HEADER
# ==================================

st.title("♻️ SMART DUSTBIN MONITORING SYSTEM")

st.subheader("IoT Based Smart Waste Management")

st.success("Smart Dustbin Dashboard")


# ==================================
# MESSAGE UPDATE BUTTON
# ==================================

st.header("📩 SMS MESSAGE UPDATE")

if st.button("🔄 MESSAGE UPDATE", use_container_width=True):

    # Demonstration SMS event
    st.session_state.sms_received = True

    st.session_state.sms_message = (
        "SMS RECEIVED: Smart Dustbin BIN-001 "
        "Garbage Level: "
        + str(st.session_state.garbage_level)
        + "% | Latitude: 22.150000 "
        "Longitude: 84.270000"
    )

    st.session_state.last_update = (
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    )

    st.rerun()


if st.session_state.sms_received:

    st.success("✅ SMS RECEIVED")

    st.info(st.session_state.sms_message)

else:

    st.warning("Waiting for SMS message...")


# ==================================
# GARBAGE DETAILS
# ==================================

st.header("🗑️ GARBAGE DETAILS")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Garbage Level",
        f"{st.session_state.garbage_level}%"
    )

with col2:
    st.metric(
        "Dustbin ID",
        BIN_ID
    )

with col3:
    st.metric(
        "Status",
        "FULL" if st.session_state.garbage_level >= 80
        else "NORMAL"
    )

st.progress(
    st.session_state.garbage_level / 100
)

st.write(
    "**Last Update:**",
    st.session_state.last_update
)


# ==================================
# LOCATION DETAILS
# ==================================

st.header("📍 DUSTBIN LOCATION")

col1, col2 = st.columns(2)

with col1:
    st.info(f"Latitude: {LATITUDE:.6f}")

with col2:
    st.info(f"Longitude: {LONGITUDE:.6f}")


# ==================================
# SATELLITE MAP
# ==================================

st.header("🛰️ SATELLITE VIEW")

m = folium.Map(
    location=[LATITUDE, LONGITUDE],
    zoom_start=17,
    tiles=None
)

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri Satellite Imagery",
    name="Satellite View"
).add_to(m)

folium.Marker(
    [LATITUDE, LONGITUDE],
    tooltip="BIN-001",
    popup=(
        f"Dustbin ID: {BIN_ID}<br>"
        f"Garbage Level: "
        f"{st.session_state.garbage_level}%"
    ),
    icon=folium.Icon(
        color="red"
        if st.session_state.garbage_level >= 80
        else "green",
        icon="trash",
        prefix="fa"
    )
).add_to(m)

folium.LayerControl().add_to(m)

st_folium(
    m,
    width=None,
    height=500,
    use_container_width=True
)


# ==================================
# DISTANCE CALCULATION
# ==================================

st.header("🚛 DISTANCE CALCULATION")

truck_lat = st.number_input(
    "Truck Latitude",
    value=22.140000,
    format="%.6f"
)

truck_lon = st.number_input(
    "Truck Longitude",
    value=84.260000,
    format="%.6f"
)

distance = calculate_distance(
    truck_lat,
    truck_lon,
    LATITUDE,
    LONGITUDE
)

st.metric(
    "Distance to Dustbin",
    f"{distance:.2f} KM"
)

st.link_button(
    "🧭 NAVIGATE TO DUSTBIN",
    f"https://www.google.com/maps/dir/?api=1"
    f"&destination={LATITUDE},{LONGITUDE}"
    "&travelmode=driving"
)


# ==================================
# FOOTER
# ==================================

st.divider()

st.caption(
    "Smart Dustbin Monitoring System | "
    "Arduino Uno + SIM900A + Python Streamlit"
)
