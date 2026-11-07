
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
# DUSTBIN DATABASE
# =====================================

bins = [
    {
        "id": "BIN-001",
        "name": "Main Road Dustbin",
        "location": "Main Road",
        "latitude": 22.150000,
        "longitude": 84.270000,
        "fill": 92,
        "description": "Public waste collection point"
    },
    {
        "id": "BIN-002",
        "name": "Market Dustbin",
        "location": "Market Area",
        "latitude": 22.155000,
        "longitude": 84.275000,
        "fill": 35,
        "description": "Market waste collection point"
    },
    {
        "id": "BIN-003",
        "name": "School Dustbin",
        "location": "School",
        "latitude": 22.145000,
        "longitude": 84.265000,
        "fill": 85,
        "description": "School waste collection point"
    },
    {
        "id": "BIN-004",
        "name": "Park Dustbin",
        "location": "Public Park",
        "latitude": 22.160000,
        "longitude": 84.280000,
        "fill": 60,
        "description": "Park waste collection point"
    }
]


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
# SCHOOL DUSTBIN STARTING LOCATION
# =====================================

school_bin = next(
    b for b in bins if b["id"] == "BIN-003"
)

start = (
    school_bin["latitude"],
    school_bin["longitude"]
)


# =====================================
# MESSAGE UPDATE BUTTON
# =====================================

st.header("📩 SMS MESSAGE UPDATE")

if st.button(
    "🔄 MESSAGE UPDATE",
    use_container_width=True
):

    # Demonstration message using sample data
    st.session_state.message_received = True

    st.session_state.sms_message = (
        f"SMART DUSTBIN MESSAGE RECEIVED\n"
        f"Dustbin ID: {school_bin['id']}\n"
        f"Garbage Level: {school_bin['fill']}%\n"
        f"Latitude: {school_bin['latitude']:.6f}\n"
        f"Longitude: {school_bin['longitude']:.6f}\n"
        f"Status: {'FULL' if school_bin['fill'] >= 80 else 'NORMAL'}"
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
# SELECT DESTINATION DUSTBIN
# =====================================

st.divider()

st.header("📍 SELECT DESTINATION DUSTBIN")

destination_bins = [
    b for b in bins
    if b["id"] != "BIN-003"
]

selected_id = st.selectbox(
    "Choose destination dustbin",
    [b["id"] for b in destination_bins]
)

selected = next(
    b for b in destination_bins
    if b["id"] == selected_id
)

destination = (
    selected["latitude"],
    selected["longitude"]
)


# =====================================
# SELECTED DUSTBIN DETAILS
# =====================================

st.header("🗑️ DESTINATION DUSTBIN DETAILS")

c1, c2, c3 = st.columns(3)

c1.metric("Dustbin ID", selected["id"])

c2.metric(
    "Garbage Level",
    f"{selected['fill']}%"
)

status = (
    "FULL" if selected["fill"] >= 80
    else "WARNING" if selected["fill"] >= 50
    else "NORMAL"
)

c3.metric("Status", status)

st.write("**Name:**", selected["name"])

st.write("**Location:**", selected["location"])

st.write("**Description:**", selected["description"])

st.write(
    "**Latitude:**",
    f"{selected['latitude']:.6f}"
)

st.write(
    "**Longitude:**",
    f"{selected['longitude']:.6f}"
)

st.progress(selected["fill"] / 100)

if selected["fill"] >= 80:
    st.error("⚠️ Dustbin is FULL. Collection required.")
elif selected["fill"] >= 50:
    st.warning("Dustbin is approaching full capacity.")
else:
    st.success("Dustbin is operating normally.")


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
# ROAD ROUTE CALCULATION
# =====================================

def get_route(start, destination):

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start[1]},{start[0]};"
        f"{destination[1]},{destination[0]}"
    )

    try:

        response = requests.get(
            url,
            params={
                "overview": "full",
                "geometries": "geojson"
            },
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != "Ok":
            return None

        route = data["routes"][0]

        return {
            "distance": route["distance"] / 1000,
            "time": route["duration"] / 60,
            "coordinates": route["geometry"]["coordinates"]
        }

    except (
        requests.RequestException,
        ValueError,
        KeyError,
        IndexError
    ):
        return None


# =====================================
# SATELLITE MAP
# =====================================

st.divider()

st.header("🛰️ SATELLITE MAP")

m = folium.Map(
    location=list(start),
    zoom_start=16,
    tiles=None
)

# Satellite imagery

folium.TileLayer(
    tiles=(
        "https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    attr="Esri World Imagery",
    name="Satellite View"
).add_to(m)

# Street map

folium.TileLayer(
    "OpenStreetMap",
    name="Street Map"
).add_to(m)


# =====================================
# SCHOOL DUSTBIN MARKER
# =====================================

folium.Marker(
    location=list(start),
    tooltip="School Dustbin BIN-003",
    popup="""
    <b>SCHOOL DUSTBIN</b><br>
    ID: BIN-003<br>
    Garbage: 85%<br>
    Status: FULL
    """,
    icon=folium.Icon(
        color="red",
        icon="trash",
        prefix="fa"
    )
).add_to(m)


# =====================================
# OTHER DUSTBIN MARKERS
# =====================================

for b in bins:

    if b["id"] == "BIN-003":
        continue

    fill = b["fill"]

    if fill >= 80:
        color = "red"
        status = "FULL"

    elif fill >= 50:
        color = "orange"
        status = "WARNING"

    else:
        color = "green"
        status = "NORMAL"

    popup = f"""
    <b>{b['name']}</b><br>
    ID: {b['id']}<br>
    Garbage: {fill}%<br>
    Location: {b['location']}<br>
    Latitude: {b['latitude']}<br>
    Longitude: {b['longitude']}<br>
    Status: {status}
    """

    folium.Marker(
        location=[
            b["latitude"],
            b["longitude"]
        ],
        popup=folium.Popup(
            popup,
            max_width=300
        ),
        tooltip=b["name"],
        icon=folium.Icon(
            color=color,
            icon="trash",
            prefix="fa"
        )
    ).add_to(m)


# =====================================
# ROUTE FROM SCHOOL DUSTBIN
# =====================================

st.header("🚛 DUSTBIN COLLECTION ROUTE")

straight_distance = calculate_distance(
    start[0],
    start[1],
    destination[0],
    destination[1]
)

route = get_route(
    start,
    destination
)

if route:

    route_points = [
        [lat, lon]
        for lon, lat in route["coordinates"]
    ]

    folium.PolyLine(
        route_points,
        color="#00AA55",
        weight=6,
        opacity=0.9,
        tooltip="School to Selected Dustbin"
    ).add_to(m)

    col1, col2 = st.columns(2)

    col1.metric(
        "Road Distance",
        f"{route['distance']:.2f} km"
    )

    col2.metric(
        "Estimated Travel Time",
        f"{route['time']:.0f} minutes"
    )

    st.success("Road route calculated successfully.")

else:

    st.warning(
        "Road routing unavailable. "
        "Showing straight-line distance instead."
    )

    st.metric(
        "Straight-line Distance",
        f"{straight_distance:.2f} km"
    )


# Fit map

m.fit_bounds([
    start,
    destination
])

folium.LayerControl().add_to(m)

st_folium(
    m,
    height=550,
    use_container_width=True
)


# =====================================
# GOOGLE MAPS NAVIGATION
# =====================================

google_maps_url = (
    "https://www.google.com/maps/dir/?api=1"
    f"&origin={start[0]},{start[1]}"
    f"&destination={destination[0]},{destination[1]}"
    "&travelmode=driving"
)

st.link_button(
    "🧭 OPEN GOOGLE MAPS NAVIGATION",
    google_maps_url
)


# =====================================
# ALL DUSTBIN DETAILS
# =====================================

st.divider()

st.header("📋 ALL DUSTBIN DETAILS")

for b in bins:

    with st.expander(
        f"{b['id']} - {b['name']}"
    ):

        st.write("Location:", b["location"])

        st.write(
            "Garbage Level:",
            f"{b['fill']}%"
        )

        st.write(
            "Latitude:",
            f"{b['latitude']:.6f}"
        )

        st.write(
            "Longitude:",
            f"{b['longitude']:.6f}"
        )

        st.write("Description:", b["description"])

        st.progress(b["fill"] / 100)


# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "Smart Dustbin Management System | "
    "Arduino Uno R3 | SIM900A | Python | Streamlit"
)
