
import streamlit as st
import folium
import requests
import math

from streamlit_folium import st_folium

st.set_page_config(
    page_title="Smart Dustbin Navigation",
    page_icon="♻️",
    layout="wide"
)

# -------------------------------
# GREEN THEME
# -------------------------------

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
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# DUSTBIN DATA
# -------------------------------

bins = [
    {
        "id": "BIN-001",
        "name": "Main Road Dustbin",
        "latitude": 22.150000,
        "longitude": 84.270000,
        "fill": 92,
        "location": "Main Road",
        "description": "Public waste collection point",
        "status": "Full"
    },
    {
        "id": "BIN-002",
        "name": "Market Dustbin",
        "latitude": 22.155000,
        "longitude": 84.275000,
        "fill": 35,
        "location": "Market Area",
        "description": "Market waste collection point",
        "status": "Normal"
    },
    {
        "id": "BIN-003",
        "name": "School Dustbin",
        "latitude": 22.145000,
        "longitude": 84.265000,
        "fill": 85,
        "location": "School Area",
        "description": "School waste collection point",
        "status": "Full"
    }
]

# -------------------------------
# HEADER
# -------------------------------

st.title("♻️ SMART DUSTBIN MANAGEMENT")
st.subheader("Satellite Monitoring & Garbage Collection Navigation")

st.divider()

# -------------------------------
# TRUCK LOCATION
# -------------------------------

st.sidebar.header("🚛 Truck Location")

truck_lat = st.sidebar.number_input(
    "Truck Latitude",
    value=22.140000,
    format="%.6f"
)

truck_lon = st.sidebar.number_input(
    "Truck Longitude",
    value=84.260000,
    format="%.6f"
)

truck = (truck_lat, truck_lon)

# -------------------------------
# SELECT DUSTBIN
# -------------------------------

st.header("🗑️ Select Dustbin")

selected_id = st.selectbox(
    "Choose a dustbin",
    [b["id"] for b in bins]
)

selected = next(
    b for b in bins if b["id"] == selected_id
)

# -------------------------------
# DISTANCE CALCULATION
# -------------------------------

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


# -------------------------------
# ROAD ROUTE
# -------------------------------

def get_route(start, end):

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start[1]},{start[0]};"
        f"{end[1]},{end[0]}"
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

    except (requests.RequestException, ValueError, KeyError):
        return None


# -------------------------------
# DUSTBIN DETAILS
# -------------------------------

st.header("📋 Dustbin Information")

c1, c2, c3 = st.columns(3)

c1.metric("Dustbin ID", selected["id"])
c2.metric("Garbage Level", f'{selected["fill"]}%')
c3.metric("Status", selected["status"])

st.write("**Name:**", selected["name"])
st.write("**Location:**", selected["location"])
st.write("**Description:**", selected["description"])

st.write(
    "**Latitude:**",
    f'{selected["latitude"]:.6f}'
)

st.write(
    "**Longitude:**",
    f'{selected["longitude"]:.6f}'
)

st.progress(selected["fill"] / 100)

if selected["fill"] >= 80:
    st.error("⚠️ Dustbin is FULL. Collection required.")
elif selected["fill"] >= 50:
    st.warning("Dustbin is getting full.")
else:
    st.success("Dustbin is operating normally.")

# -------------------------------
# SATELLITE MAP
# -------------------------------

st.header("🛰️ GOOGLE MAP STYLE SATELLITE VIEW")

m = folium.Map(
    location=[
        selected["latitude"],
        selected["longitude"]
    ],
    zoom_start=15,
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

# Truck marker

folium.Marker(
    truck,
    tooltip="Garbage Collection Truck",
    popup="Truck Current Location",
    icon=folium.Icon(
        color="blue",
        icon="truck",
        prefix="fa"
    )
).add_to(m)

# All dustbin markers

for b in bins:

    color = (
        "red" if b["fill"] >= 80
        else "orange" if b["fill"] >= 50
        else "green"
    )

    popup = f"""
    <b>{b['name']}</b><br>
    ID: {b['id']}<br>
    Garbage: {b['fill']}%<br>
    Location: {b['location']}<br>
    Latitude: {b['latitude']}<br>
    Longitude: {b['longitude']}<br>
    Status: {b['status']}
    """

    folium.Marker(
        [b["latitude"], b["longitude"]],
        popup=folium.Popup(popup, max_width=300),
        tooltip=b["id"],
        icon=folium.Icon(
            color=color,
            icon="trash",
            prefix="fa"
        )
    ).add_to(m)

# -------------------------------
# ROUTE TO SELECTED BIN
# -------------------------------

destination = (
    selected["latitude"],
    selected["longitude"]
)

route = get_route(truck, destination)

straight_distance = calculate_distance(
    truck_lat,
    truck_lon,
    destination[0],
    destination[1]
)

st.header("🚛 GARBAGE COLLECTION ROUTE")

if route:

    road_distance = route["distance"]
    travel_time = route["time"]

    route_points = [
        [lat, lon]
        for lon, lat in route["coordinates"]
    ]

    folium.PolyLine(
        route_points,
        color="green",
        weight=6,
        opacity=0.9,
        tooltip="Driving Route"
    ).add_to(m)

    st.success("Driving route calculated successfully.")

    a, b = st.columns(2)

    a.metric(
        "Road Distance",
        f"{road_distance:.2f} km"
    )

    b.metric(
        "Estimated Travel Time",
        f"{travel_time:.0f} minutes"
    )

else:

    st.warning(
        "Road route unavailable. Showing straight-line distance."
    )

    st.metric(
        "Straight-line Distance",
        f"{straight_distance:.2f} km"
    )

    st.info("Estimated driving time is unavailable.")

folium.LayerControl().add_to(m)

m.fit_bounds([
    truck,
    destination
])

st_folium(
    m,
    height=550,
    use_container_width=True
)

# -------------------------------
# GOOGLE MAPS NAVIGATION
# -------------------------------

google_url = (
    "https://www.google.com/maps/dir/?api=1"
    f"&origin={truck_lat},{truck_lon}"
    f"&destination={selected['latitude']},{selected['longitude']}"
    "&travelmode=driving"
)

st.link_button(
    "🧭 OPEN GOOGLE MAPS NAVIGATION",
    google_url
)

# -------------------------------
# FOOTER
# -------------------------------

st.divider()

st.caption(
    "Smart Dustbin System | Arduino Uno | SIM900A | Python | Streamlit"
)
