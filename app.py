
import streamlit as st
import folium
import requests
import math
from datetime import datetime
from streamlit_folium import st_folium


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Smart Dustbin Management",
    page_icon="♻️",
    layout="wide"
)


# =====================================
# GREEN THEME
# =====================================

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
    height: 45px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# SINGLE DUSTBIN DATABASE
# =====================================

dustbin = {
    "id": "BIN-001",
    "name": "Smart Dustbin",
    "location": "Registered Location",
    "latitude": 22.1500000,
    "longitude": 84.2700000,
    "fill": 0,
    "description": "Smart waste collection point"
}


# =====================================
# SESSION STATE
# =====================================

if "message_received" not in st.session_state:
    st.session_state.message_received = False

if "sms_message" not in st.session_state:
    st.session_state.sms_message = "No message received yet."

if "last_update" not in st.session_state:
    st.session_state.last_update = "Not updated"


# =====================================
# HEADER
# =====================================

st.title("♻️ SMART DUSTBIN MANAGEMENT SYSTEM")

st.subheader(
    "IoT Waste Monitoring and Collection Navigation"
)

st.success("Smart Waste Management Dashboard")

st.divider()


# =====================================
# DUSTBIN LOCATION
# =====================================

start = (
    dustbin["latitude"],
    dustbin["longitude"]
)


# =====================================
# MESSAGE UPDATE BUTTON
# =====================================

st.header("📩 SMS MESSAGE UPDATE")

if st.button(
    "🔄 MESSAGE UPDATE",
    use_container_width=True
):

    st.session_state.message_received = True

    st.session_state.sms_message = (
        f"SMART DUSTBIN MESSAGE RECEIVED\n"
        f"Dustbin ID: {dustbin['id']}\n"
        f"Garbage Level: {dustbin['fill']}%\n"
        f"Latitude: {dustbin['latitude']:.7f}\n"
        f"Longitude: {dustbin['longitude']:.7f}\n"
        f"Status: NORMAL"
    )

    st.session_state.last_update = (
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    )


if st.session_state.message_received:

    st.success("✅ SMS RECEIVED")

    st.code(st.session_state.sms_message)

    st.caption(
        "Last updated: " + st.session_state.last_update
    )

else:

    st.warning("Waiting for SMS message. Press Message Update.")


# =====================================
# DUSTBIN DETAILS
# =====================================

st.divider()

st.header("🗑️ DUSTBIN DETAILS")

c1, c2, c3 = st.columns(3)

c1.metric("Dustbin ID", dustbin["id"])

c2.metric(
    "Garbage Level",
    f'{dustbin["fill"]}%'
)

c3.metric("Status", "NORMAL")

st.write("**Name:**", dustbin["name"])

st.write("**Location:**", dustbin["location"])

st.write("**Description:**", dustbin["description"])

st.write(
    "**Latitude:**",
    f'{dustbin["latitude"]:.7f}'
)

st.write(
    "**Longitude:**",
    f'{dustbin["longitude"]:.7f}'
)

st.progress(dustbin["fill"] / 100)


# =====================================
# DISTANCE CALCULATION
# =====================================

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


# =====================================
# SATELLITE MAP
# =====================================

st.divider()

st.header("🛰️ SATELLITE MAP")

m = folium.Map(
    location=list(start),
    zoom_start=17,
    tiles=None
)

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="Satellite View"
).add_to(m)

folium.TileLayer(
    "OpenStreetMap",
    name="Street Map"
).add_to(m)


# =====================================
# SINGLE DUSTBIN MARKER
# =====================================

folium.Marker(
    location=list(start),
    tooltip="Smart Dustbin BIN-001",
    popup=f"""
    <b>SMART DUSTBIN</b><br>
    ID: {dustbin['id']}<br>
    Garbage: {dustbin['fill']}%<br>
    Latitude: {dustbin['latitude']}<br>
    Longitude: {dustbin['longitude']}
    """,
    icon=folium.Icon(
        color="green",
        icon="trash",
        prefix="fa"
    )
).add_to(m)

folium.Circle(
    location=list(start),
    radius=30,
    color="green",
    fill=True,
    fill_opacity=0.15
).add_to(m)

folium.LayerControl().add_to(m)

st_folium(
    m,
    height=550,
    use_container_width=True
)


# =====================================
# GOOGLE MAPS LOCATION
# =====================================

google_maps_url = (
    "https://www.google.com/maps/search/?api=1"
    f"&query={dustbin['latitude']},{dustbin['longitude']}"
)

st.link_button(
    "📍 OPEN DUSTBIN LOCATION IN GOOGLE MAPS",
    google_maps_url
)


# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "Smart Dustbin Management System | "
    "Arduino Uno R3 | SIM900A | Python | Streamlit"
)
