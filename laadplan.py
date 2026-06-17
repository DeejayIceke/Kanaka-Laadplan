import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Kaneka Visueel Laadplan", layout="wide")
st.title("📦 Kaneka Visueel Laadplan Dashboard")
st.write("Bepaal de exacte laadvolgorde door partijen stap voor stap achteraan aan te sluiten.")

# 1. Container Keuze
st.subheader("1. Kies het containertype")
container_type = st.selectbox(
    "Containertype", 
    ["45ft Container", "40ft Container", "20ft Container"]
)

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

# Initialiseer de partijen-wachtrij in het geheugen
if "laad_blokken" not in st.session_state:
    st.session_state.laad_blokken = []

# Definieer de vaste productspecificaties
product_info = {
    "CP3": {"lengte": 1140, "breedte": 1140, "kleur": "#3498db", "stapelbaar": False},
    "CP7": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    "CP7 Smal": {"lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True},
    "IBC": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False}
}

# 2. Invoer Pallets - Overzichtelijk naast elkaar
st.subheader("2. Stel je partij samen en sluit achteraan aan")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pallets_cp3 = st.number_input("Aantal CP3 (1140x1140)", min_value=0, value=0, step=1, key="tmp_cp3")
    if pallets_cp3 > 0:
        if st.button("Schuif CP3 achteraan ➔", key="add_cp3", use_container_width=True):
            st.session_state.laad_blokken.append({"naam": "CP3", "aantal": pallets_cp3})
            st.rerun()

with col2:
    pallets_cp7 = st.number_input("Aantal CP7 (1400x1100)", min_value=0, value=0, step=1, key="tmp_cp7")
    if pallets_cp7 > 0:
        if st.button("Schuif CP7 achteraan ➔", key="add_cp7", use_container_width=True):
            st.session_state.laad_blokken.append({"naam": "CP7", "aantal": pallets_cp7})
            st.rerun()

with col3:
    pallets_cp7_smal = st.number_input("Aantal CP7 Smal (1100x1400)", min_value=0, value=0, step=1, key="tmp_cp7_smal")
    if pallets_cp7_smal > 0:
        if st.button("Schuif CP7 Smal achteraan ➔", key="add_cp7_smal", use_container_width=True):
            st.session_state.laad_blokken.append({"naam": "CP7 Smal", "aantal": pallets_cp7_smal})
            st.rerun()

with col4:
    pallets_ibc = st.number_input("Aantal IBC's (1000x1200)", min_value=0, value=0, step=1, key="tmp_ibc")
    if pallets_ibc > 0:
        if st.button("Schuif IBC achteraan ➔", key="add_ibc", use_container_width=True):
            st.session_state.laad_blokken.append({"naam": "IBC", "aantal": pallets_ibc})
            st.rerun()

# De WISKNOP die de container volledig leegmaakt
st.write("---")
if st.button("🗑️ Wis alle velden en container (Reset volledig naar 0)", type="primary", use_container_width=True):
    st.session_state.laad_blokken = []
    st.rerun()

# Toon de actuele opgebouwde laadlijst onder elkaar met individuele verwijderoptie
if st.session_state.laad_blokken:
    st.write("### 📜 Huidige laadvolgorde (van kopschot links naar deur rechts):")
    for index, blok in enumerate(st.session_state.laad_blokken):
        l_col, r_col = st.columns([6, 1])
        with l_col:
            st.write(f"**Partij {index + 1}:** {blok['aantal']}x {blok['naam']}")
        with r_col:
            if st.button("❌", key=f"del_{index}"):
                st.session_state.laad_blokken.pop(index)
                st.rerun()

# 3. Logistieke Logica: Bouw de individuele vloerplaatsen op exact in volgorde van de blokken
laad_lijst = []
for blok in st.session_state.laad_blokken:
    info = product_info[blok["naam"]]
    
    if info["stapelbaar"]:
        vloerplaatsen = int(math.ceil(blok["aantal"] / 2))
    else:
        vloerplaatsen = int(blok["aantal"])
        
    overgebleven_pallets = blok["aantal"]
    
    for _ in range(vloerplaatsen):
        if info["stapelbaar"]:
            hoogte_label = " (2H)" if overgebleven_pallets >= 2 else " (1H)"
            overgebleven_pallets -= 2
        else:
            hoogte_label = ""
            
        laad_lijst.append({
            "naam": f"{blok['naam']}{hoogte_label}", 
            "naam_puur": blok["naam"],
            "L": info["lengte"], 
            "B": info["breedte"], 
            "kleur": info["kleur"]
        })

# Rijen maken op basis van de containerbreedte (behoudt de exacte blokvolgorde)
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

# 4. Teken Layout Berekening
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
    is_alleen_cp7_smal = len(rij) == 1 and rij["naam_puur"] == "CP7 Smal"
    
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

# 5. Resultaat tonen
st.subheader("3. Resultaat & Visuele Indeling")

if st.session_state.laad_blokken:
    if restruimte >= 0:
        st.success(f"Dit past! Je hebt nog {restruimte} mm over in de container.")
    else:
        st.error(f"Dit past NIET! Je komt {abs(restruimte)} mm tekort.")

    st.pyplot(fig)
    st.write(f"**Gebruikte lengte:** {totale_meters} mm van de {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw = CP3 | [X] Groen = CP7 | [X] Paars = CP7 Smal | [X] Geel = IBC")
else:
    st.info("De container is nog leeg. Stel hierboven een partij samen en klik op 'Schuif achteraan' om te laden.")
