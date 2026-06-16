import streamlit as st
import math

st.set_page_config(page_title="Kaneka Laadplan Dashboard", layout="wide")
st.title("📦 Kaneka Laadplan Dashboard")
st.write("Bereken nauwkeurig de resterende ruimte in je container, inclusief slimme mix-rijen.")

# 1. Container Keuze
st.subheader("1. Kies het containertype")
container_type = st.selectbox("Containertype", ["45ft Container", "40ft Container", "20ft Container"])

# Container lengtes bepalen
if container_type == "45ft Container":
    max_lengte = 13550
elif container_type == "40ft Container":
    max_lengte = 12030
else:
    max_lengte = 5898

st.info(f"Geselecteerde container laadruimte: **{max_lengte} mm**")

# 2. Invoer Pallets
st.subheader("2. Vul het aantal pallets in (inclusief stapeling)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    pallets_cp3 = st.number_input("Aantal CP3 Pallets (1140x1140)", min_value=0, value=0, step=1)
with col2:
    pallets_cp7 = st.number_input("Aantal CP7 Pallets (1400x1100)", min_value=0, value=0, step=1)
with col3:
    pallets_cp7_smal = st.number_input("Aantal CP7 Smal (1100x1400)", min_value=0, value=0, step=1)
with col4:
    pallets_ibc = st.number_input("Aantal IBC's (1000x1200)", min_value=0, value=0, step=1)

# Handmatige opgave vloerplaatsen (want we stapelen soms 2 hoog)
st.subheader("3. Controleer de vloerplaatsen (Rijen op de grond)")
st.write("Vul in hoeveel stapels/vloerplaatsen dit fysiek inneemt:")

c1, c2, c3, c4 = st.columns(4)
with c1:
    vloer_cp3 = st.number_input("Vloerplaatsen CP3", min_value=0, value=int(math.ceil(pallets_cp3 / 2)) if pallets_cp3 > 0 else 0)
with c2:
    vloer_cp7 = st.number_input("Vloerplaatsen CP7", min_value=0, value=int(math.ceil(pallets_cp7 / 2)) if pallets_cp7 > 0 else 0)
with c3:
    vloer_cp7_smal = st.number_input("Vloerplaatsen CP7 Smal", min_value=0, value=int(math.ceil(pallets_cp7_smal / 2)) if pallets_cp7_smal > 0 else 0)
with c4:
    vloer_ibc = st.number_input("Vloerplaatsen IBC", min_value=0, value=int(math.ceil(pallets_ibc / 2)) if pallets_ibc > 0 else 0)

# Logistieke Logica Berekening
artikelen = [
    {"naam": "CP3", "vloer": vloer_cp3, "lengte": 1140},
    {"naam": "CP7", "vloer": vloer_cp7, "lengte": 1400},
    {"naam": "CP7 Smal", "vloer": vloer_cp7_smal, "lengte": 1100},
    {"naam": "IBC", "vloer": vloer_ibc, "lengte": 1000}
]

totale_meters = 0
oneven_restjes = []

# Bereken eerst de volledig bezette rijen (per 2 stuks op de vloer)
for art in artikelen:
    volle_rijen = art["vloer"] // 2
    totale_meters += volle_rijen * art["lengte"]
    
    # Check of er een losse pallet overblijft (oneven aantal vloerplaatsen)
    if art["vloer"] % 2 != 0:
        oneven_restjes.append(art["lengte"])

# Combineer de oneven restjes slim naast elkaar
aantal_restjes = len(oneven_restjes)
if aantal_restjes > 0:
    # Sorteer van lang naar kort
    oneven_restjes.sort(reverse=True)
    # Pak paartjes van 2 die naast elkaar in 1 rij gaan. De langste pallet bepaalt de rijlengte.
    for i in range(0, aantal_restjes, 2):
        totale_meters += oneven_restjes[i]

restruimte = max_lengte - totale_meters

# 4. Resultaat tonen
st.subheader("4. Resultaat")

if restruimte >= 0:
    st.success(f"✅ Dit past! Je hebt nog **{restruimte} mm** over in de container.")
else:
    st.error(f"❌ Dit past NIET! Je komt **{abs(restruimte)} mm** tekort.")

# Visuele weergave
st.progress(min(max(totale_meters / max_lengte, 0.0), 1.0))
st.write(f"Gebruikte lengte: {totale_meters} mm van de {max_lengte} mm.")
