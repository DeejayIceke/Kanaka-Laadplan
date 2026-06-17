import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Kaneka Visueel Laadplan", layout="wide")
st.title("📦 Kaneka Visueel Laadplan Dashboard")
st.write("Bereken de resterende ruimte en bekijk de visuele indeling van de container.")

# 1. Container Keuze - Terug naar de 3 gevraagde basistypes
st.subheader("1. Kies het containertype")
container_type = st.selectbox(
    "Containertype", 
    ["45ft Container", "40ft Container", "20ft Container"]
)

# De exacte binnenmaten (Breedte op 2426 mm gezet zodat IBC's naast elkaar passen)
if container_type == "45ft Container":
    max_lengte = 13550  
    max_breedte = 2426  
elif container_type == "40ft Container":
    max_lengte = 12030  
    max_breedte = 2426  
else:
    max_lengte = 5898   
    max_breedte = 2426  

st.info(f"Geselecteerde container laadruimte: **{max_lengte} mm** lang x **{max_breedte} mm** breed.")

# 2. Invoer Pallets - Alles weer tegelijk zichtbaar naast elkaar!
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

# Handmatige knop om alles in één keer te wissen naar 0
if st.button("🗑️ Wis alle velden (Reset naar 0)", type="secondary"):
    st.rerun()

# Vloerplaatsen bepalen (CP3 en IBC = 1 hoog, CP7 = 2 hoog)
vloer_cp3 = int(pallets_cp3)
vloer_cp7 = int(math.ceil(pallets_cp7 / 2))
vloer_cp7_smal = int(math.ceil(pallets_cp7_smal / 2))
vloer_ibc = int(pallets_ibc)

# Logistieke Logica (Volgorde van invoer: CP3 -> CP7 -> CP7 Smal -> IBC)
artikelen = [
    {"naam": "CP3", "totaal_pallets": pallets_cp3, "vloer": vloer_cp3, "lengte": 1140, "breedte": 1140, "kleur": "#3498db", "stapelbaar": False},
    {"naam": "CP7", "totaal_pallets": pallets_cp7, "vloer": vloer_cp7, "lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    {"naam": "CP7 Smal", "totaal_pallets": pallets_cp7_smal, "vloer": vloer_cp7_smal, "lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True},
    {"naam": "IBC", "totaal_pallets": pallets_ibc, "vloer": vloer_ibc, "lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False}
]

# Lijst opbouwen van alle individuele vloerplaatsen
laad_lijst = []
for art in artikelen:
    overgebleven_pallets = art["totaal_pallets"]
    for i in range(art["vloer"]):
        if art["stapelbaar"]:
            hoogte_label = " (2H)" if overgebleven_pallets >= 2 else " (1H)"
            overgebleven_pallets -= 2
        else:
            hoogte_label = ""
            
        laad_lijst.append({
            "naam": f"{art['naam']}{hoogte_label}", 
            "naam_puur": art["naam"],
            "L": art["lengte"], 
            "B": art["breedte"], 
            "kleur": art["kleur"]
        })

# Rijen maken op basis van de containerbreedte
rijen = []
tijdelijke_rij = []
huidige_breedte_in_rij = 0

for item in laad_lijst:
    if (huidige_breedte_in_rij + item["B"] <= max_breedte) and (len(tijdelijke_rij) < 2):
        tijdelijke_rij.append(item)
        huidige_breedte_in_rij += item["B"]
    else:
        if tijdelijke_rij:
            rijen.append(tijdelijke_rij)
        tijdelijke_rij = [item]
        huidige_breedte_in_rij = item["B"]

if tijdelijke_rij:
    rijen.append(tijdelijke_rij)

# Teken Layout Berekening
fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_xlabel("Lengte container (mm)")
ax.set_ylabel("Breedte container (mm)")

container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

huidige_x = 0
totale_meters = 0

# Teken elke rij pallets
for rij in rijen:
    rij_lengte = max([item["L"] for item in rij])
    
    # Gecorrigeerd: Kijk naar het eerste item in de rij (rij[0]) in plaats van de hele lijst
    is_alleen_cp7_smal = len(rij) == 1 and rij[0]["naam_puur"] == "CP7 Smal"
    
    for index, item in enumerate(rij):
        if is_alleen_cp7_smal:
            y_pos = (max_breedte - item["B"]) / 2
        else:
            y_pos = 20 if index == 0 else max_breedte - item["B"] - 20
        
        rect = patches.Rectangle((huidige_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
        ax.add_patch(rect)
        ax.text(huidige_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=8)
        
    huidige_x += rij_lengte
    totale_meters += rij_lengte

restruimte = max_lengte - totale_meters

# 3. Resultaat tonen
st.subheader("3. Resultaat & Visuele Indeling")

if restruimte >= 0:
    st.success(f"Dit past! Je hebt nog {restruimte} mm over in de container.")
else:
    st.error(f"Dit past NIET! Je komt {abs(restruimte)} mm tekort.")

st.pyplot(fig)

st.write(f"**Gebruikte lengte:** {totale_meters} mm van de {max_lengte} mm.")
st.write("💡 **Legenda:** [X] Blauw = CP3 | [X] Groen = CP7 | [X] Paars = CP7 Smal | [X] Geel = IBC")
