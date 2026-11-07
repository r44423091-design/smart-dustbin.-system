
import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime


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

div.stButton > button:hover {
    background-color: #166534;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# DUSTBIN INFORMATION
# =====================================

dustbin = {
    "id": "BIN-001",
    "name": "Smart Dustbin",
    "location": "Registered Location",
    "latitude": 22.163481,
    "longitude": 84.28116,
    "fill": 75,
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

if "garbage_level" not in st.session_state:
    st.session_state.garbage_level = 0


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
# MESSAGE UPDATE BUTTON
# =====================================

st.header("📩 SMS MESSAGE UPDATE")

if st.button(
    "🔄 MESSAGE UPDATE",
    use_container_width=True,
    key="message_update"
):

    st.session_state.message_received = True

    st.session_state.sms_message = (
        "SMART DUSTBIN MESSAGE RECEIVED\n"
        f"Dustbin ID: {dustbin['id']}\n"
        f"Garbage Level: {st.session_state.garbage_level}%\n"
        f"Latitude: {dustbin['latitude']:.7f}\n"
        f"Longitude: {dustbin['longitude']:.7f}\n"
        f"Status: {'medium' if st.session_state.garbage_level >= 80 else 'NORMAL'}"
    )

    st.session_state.last_update = (
        datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    )


if st.session_state.message_received:

    st.success("✅ SMS RECEIVED")

    st.code(
        st.session_state.sms_message,
        language=None
    )

    st.caption(
        "Last updated: " + st.session_state.last_update
    )

else:

    st.warning(
        "Waiting for SMS message. Press Message Update."
    )


# =====================================
# GARBAGE DETAILS
# =====================================

st.divider()

st.header("🗑️ GARBAGE DETAILS")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Dustbin ID",
    dustbin["id"]
)

col2.metric(
    "Garbage Level",
    f"{st.session_state.garbage_level}%"
)

if st.session_state.garbage_level >= 80:
    status = "FULL"
elif st.session_state.garbage_level >= 50:
    status = "WARNING"
else:
    status = "NORMAL"

col3.metric(
    "Status",
    status
)

st.progress(
    st.session_state.garbage_level / 100
)

st.write(
    "**Dustbin Name:**",
    dustbin["name"]
)

st.write(
    "**Location:**",
    dustbin["location"]
)

st.write(
    "**Description:**",
    dustbin["description"]
)


# =====================================
# GPS LOCATION
# =====================================

st.divider()

st.header("📍 DUSTBIN GPS LOCATION")

col1, col2 = st.columns(2)

col1.info(
    f"Latitude: {dustbin['latitude']:.7f}"
)

col2.info(
    f"Longitude: {dustbin['longitude']:.7f}"
)


# =====================================
# SATELLITE MAP
# =====================================

st.divider()

st.header("🛰️ SATELLITE MAP")

# Recreate map on every Streamlit rerun

m = folium.Map(
    location=[
        dustbin["latitude"],
        dustbin["longitude"]
    ],
    zoom_start=17,
    tiles=None
)


# Satellite layer

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="Satellite View"
).add_to(m)


# Street layer

folium.TileLayer(
    "OpenStreetMap",
    name="Street Map"
).add_to(m)


# Dustbin marker

folium.Marker(
    location=[
        dustbin["latitude"],
        dustbin["longitude"]
    ],
    tooltip="Smart Dustbin BIN-001",
    popup=folium.Popup(
        f"""
        <b>SMART DUSTBIN</b><br>
        Dustbin ID: {dustbin['id']}<br>
        Garbage Level: {st.session_state.garbage_level}%<br>
        Latitude: {dustbin['latitude']:.7f}<br>
        Longitude: {dustbin['longitude']:.7f}<br>
        Status: {status}
        """,
        max_width=300
    ),
    icon=folium.Icon(
        color="red" if st.session_state.garbage_level >= 80 else "green",
        icon="trash",
        prefix="fa"
    )
).add_to(m)


# Dustbin location circle

folium.Circle(
    location=[
        dustbin["latitude"],
        dustbin["longitude"]
    ],
    radius=30,
    color="green",
    fill=True,
    fill_opacity=0.15
).add_to(m)


# Map layer control

folium.LayerControl().add_to(m)


# Display map

st_folium(
    m,
    height=550,
    use_container_width=True,
    key="smart_dustbin_map"
)


# =====================================
# GOOGLE MAPS LOCATION
# =====================================

st.divider()

st.header("🧭 GOOGLE MAPS NAVIGATION")

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
    "Smart Dustbin Monitoring System | "
    "Arduino Uno R3 | SIM900A | Python | Streamlit"
)
