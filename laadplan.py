import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Kaneka Visueel Laadplan", layout="wide")
st.title("📦 Kaneka Visueel Laadplan Dashboard")
st.write("Bereken de resterende ruimte en bekijk de visuele indeling van de container.")

# 1. Container Keuze
st.subheader("1. Kies het containertype")
container_type = st.selectbox("Containertype", ["45ft Container", "40ft Container", "20ft Container"])

# Container maten bepalen (Lengte x Breedte in mm)
if container_type == "45ft Container":
    max_lengte = 13550
elif container_type == "40ft Container":
    max_lengte = 12030
else:
    max_lengte = 5898

max_breedte = 2350  # Gemiddelde binnenbreedte container
st.info(f"Geselecteerde container laadruimte: **{max_lengte} mm** lang x **{max_breedte} mm** breed.")

# 2. Invoer Pallets
st.subheader("2. Vul het aantal pallets in")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pallets_cp3 = st.number_input("Aantal CP3 Pallets (1140x1140)", min_value=0, value=0, step=1)
with col2:
    pallets_cp7 = st.number_input("Aantal CP7 Pallets (1400x1100)", min_value=0, value=0, step=1)
with col3:
    pallets_cp7_smal = st.number_input("Aantal CP7 Smal (1100x1400)", min_value=0, value=0, step=1)
with col4:
    pallets_ibc = st.number_input("Aantal IBC's (1000x1200)", min_value=0, value=0, step=1)

# Vloerplaatsen bepalen op basis van jouw regels (CP3 en IBC = 1 hoog, CP7 = 2 hoog)
vloer_cp3 = int(pallets_cp3)
vloer_cp7 = int(math.ceil(pallets_cp7 / 2))
vloer_cp7_smal = int(math.ceil(pallets_cp7_smal / 2))
vloer_ibc = int(pallets_ibc)

# Logistieke Logica
artikelen = [
    {"naam": "CP3", "vloer": vloer_cp3, "lengte": 1140, "breedte": 1140, "kleur": "#3498db"},
    {"naam": "CP7", "vloer": vloer_cp7, "lengte": 1400, "breedte": 1100, "kleur": "#2ecc71"},
    {"naam": "CP7 Smal", "vloer": vloer_cp7_smal, "lengte": 1100, "breedte": 1400, "kleur": "#9b59b6"},
    {"naam": "IBC", "vloer": vloer_ibc, "lengte": 1000, "breedte": 1200, "kleur": "#f1c40f"}
]

# Lijst opbouwen van álle individuele vloerplaatsen die geladen moeten worden
laad_lijst = []
for art in artikelen:
    for _ in range(art["vloer"]):
        laad_lijst.append({"naam": art["naam"], "L": art["lengte"], "B": art["breedte"], "kleur": art["kleur"]})

# Sorteer de laadlijst van lang naar kort om de langste pallets eerst te laden (efficiënter)
laad_lijst.sort(key=lambda x: x["L"], reverse=True)

# Pallets virtueel in rijen van 2 plaatsen
rijen = []
tijdelijke_rij = []

for item in laad_lijst:
    tijdelijke_rij.append(item)
    if len(tijdelijke_rij) == 2:
        rijen.append(tijdelijke_rij)
        tijdelijke_rij = []

if len(tijdelijke_rij) > 0:
    rijen.append(tijdelijke_rij)

# Teken Layout Berekening
fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_xlabel("Lengte container (mm)")
ax.set_ylabel("Breedte container (mm)")

# Teken de containeromtrek
container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

huidige_x = 0
totale_meters = 0

# Teken elke rij pallets in de container
for rij in rijen:
    rij_lengte = max([item["L"] for item in rij])
    
    # Controleer of we de breedte verdelen (links en rechts)
    for index, item in enumerate(rij):
        # Y-positie bepalen: eerste item onderaan (y=100), tweede item bovenaan (y=max_breedte - breedte - 100)
        y_pos = 100 if index == 0 else max_breedte - item["B"] - 100
        
        rect = patches.Rectangle((huidige_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
        ax.add_patch(rect)
        # Label op de pallet schrijven
        ax.text(huidige_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=8)
        
    huidige_x += rij_lengte
    totale_meters += rij_lengte

restruimte = max_lengte - totale_meters

# Resultaat tonen
st.subheader("3. Resultaat & Visuele Indeling")

if restruimte >= 0:
    st.success(f"✅ Dit past! Je hebt nog **{restruimte} mm** over in de container.")
else:
    st.error(f"❌ Dit past NIET! Je komt **{abs(restruimte)} mm** tekort.")

# Toon de getekende container
st.pyplot(fig)

st.write(f"**Gebruikte lengte:** {totale_meters} mm van de {max_lengte} mm.")
st.markdown("💡 **Legenda:** <span style='color:#3498db'>■</span> CP3 | <span style='color:#2ecc71'>■</span> CP7 | <span style='color:#9b59b6'>■</span> CP7 Smal | <span style='color:#f1c40f'>■</span> IBC", unsafe_allowed_html=True)

st.write(f"Gebruikte lengte: {totale_meters} mm van de {max_lengte} mm.")
