import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Kaneka Visueel Laadplan", layout="wide")
st.title("📦 Kaneka Visueel Laadplan Dashboard")
st.write("Vul direct de aantallen in. Bij 40ft/20ft containers worden IBC's automatisch in elkaar gevlochten met de juiste verhoudingen.")

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
    max_breedte = 2350  
else:
    max_lengte = 5898   
    max_breedte = 2350  

st.info(f"Geselecteerde container laadruimte: **{max_lengte} mm** lang x **{max_breedte} mm** breed.")

# Initialiseer de tracking van volgorde en aantallen
if "klik_volgorde" not in st.session_state:
    st.session_state.klik_volgorde = []
if "reset_id" not in st.session_state:
    st.session_state.reset_id = 0

# Definieer de vaste productspecificaties
product_info = {
    "CP3": {"lengte": 1140, "breedte": 1140, "kleur": "#3498db", "stapelbaar": False},
    "CP7": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    "CP7 Smal": {"lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True},
    "IBC": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False}
}

# 2. Invoer Pallets
st.subheader("2. Vul het aantal pallets in")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pallets_cp3 = st.number_input("Aantal CP3 (1140x1140)", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}")
    if pallets_cp3 > 0 and "CP3" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("CP3")

with col2:
    pallets_cp7 = st.number_input("Aantal CP7 (1400x1100)", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}")
    if pallets_cp7 > 0 and "CP7" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("CP7")

with col3:
    pallets_cp7_smal = st.number_input("Aantal CP7 Smal (1100x1400)", min_value=0, value=0, step=1, key=f"cp7_smal_{st.session_state.reset_id}")
    if pallets_cp7_smal > 0 and "CP7 Smal" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("CP7 Smal")

with col4:
    pallets_ibc = st.number_input("Aantal IBC's (1000x1200)", min_value=0, value=0, step=1, key=f"ibc_{st.session_state.reset_id}")
    if pallets_ibc > 0 and "IBC" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("IBC")

actuele_aantallen = {"CP3": pallets_cp3, "CP7": pallets_cp7, "CP7 Smal": pallets_cp7_smal, "IBC": pallets_ibc}
st.session_state.klik_volgorde = [art for art in st.session_state.klik_volgorde if actuele_aantallen[art] > 0]

# De WISKNOP
st.write("---")
if st.button("🗑️ Wis alle velden en container (Reset volledig naar 0)", type="primary", use_container_width=True):
    st.session_state.klik_volgorde = []
    st.session_state.reset_id += 1
    st.rerun()

# 3. Logistieke Logica: Bouw de individuele vloerplaatsen op
laad_lijst = []
for art_naam in st.session_state.klik_volgorde:
    total_pallets = actuele_aantallen[art_naam]
    info = product_info[art_naam]
    
    vloerplaatsen = int(math.ceil(total_pallets / 2)) if info["stapelbaar"] else int(total_pallets)
    overgebleven = total_pallets
    
    for _ in range(vloerplaatsen):
        if info["stapelbaar"]:
            hoogte_label = " (2H)" if overgebleven >= 2 else " (1H)"
            overgebleven -= 2
        else:
            hoogte_label = ""
            
        laad_lijst.append({
            "naam": f"{art_naam}{hoogte_label}", 
            "naam_puur": art_naam,
            "L": info["lengte"], 
            "B": info["breedte"], 
            "kleur": info["kleur"]
        })

# Rijen maken op basis van de containerbreedte met de slimme geschakelde logica voor IBC's
rijen = []
tijdelijke_rij = []
huidige_breedte_in_rij = 0
ibc_omgedraaid = False

for item in laad_lijst:
    is_ibc_in_smalle_container = (max_breedte == 2350 and item["naam_puur"] == "IBC")
    
    if is_ibc_in_smalle_container and len(tijdelijke_rij) == 1 and tijdelijke_rij[0]["naam_puur"] == "IBC":
        item_gekopieerd = item.copy()
        first_item = tijdelijke_rij[0]
        
        if not ibc_omgedraaid:
            # Eerste ligt dwars (breed=1200, lang=1000)
            first_item["L"] = 1000
            first_item["B"] = 1200
            first_item["naam"] = "IBC (Breed)"
            
            # De 2e zetten we rechtop (breed=1000, lang=1200)
            item_gekopieerd["L"] = 1200
            item_gekopieerd["B"] = 1000
            item_gekopieerd["naam"] = "IBC (Lang)"
        else:
            # Rij omdraaien voor stabiele vlecht
            first_item["L"] = 1200
            first_item["B"] = 1000
            first_item["naam"] = "IBC (Lang)"
            
            item_gekopieerd["L"] = 1000
            item_gekopieerd["B"] = 1200
            item_gekopieerd["naam"] = "IBC (Breed)"
            
        first_item["vlecht_mode"] = True
        item_gekopieerd["vlecht_mode"] = True
        
        tijdelijke_rij.append(item_gekopieerd)
        rijen.append(tijdelijke_rij)
        ibc_omgedraaid = not ibc_omgedraaid  # Wissel voor de volgende rij
        tijdelijke_rij = []
        huidige_breedte_in_rij = 0
    
    elif (huidige_breedte_in_rij + item["B"] <= max_breedte) and (len(tijdelijke_rij) < 2):
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
fig, ax = plt.subplots(figsize=(15, 3.5))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_xlabel("Lengte container (mm)")
ax.set_ylabel("Breedte container (mm)")

# CRITIALE FIX: Dwing gelijke verhoudingen af (Schermvullend uitrekken voorkomen)
ax.set_aspect('equal', adjustable='box')

# Teken containeromtrek
container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

huidige_x = 0
totale_meters = 0

# Teken elke rij pallets
for rij in rijen:
    # Gecorrigeerde vlecht-lengte: twee in elkaar gehaakte rijen IBC's kosten samen exact 2200 mm laadlengte (dus gemiddeld 1100 per rij)
    if "vlecht_mode" in rij[0] and len(rij) == 2:
        rij_lengte = 1100
    else:
        rij_lengte = max([item["L"] for item in rij])
    
    is_alleen_cp7_smal = len(rij) == 1 and rij[0]["naam_puur"] == "CP7 Smal"
    
    for index, item in enumerate(rij):
        if is_alleen_cp7_smal:
            y_pos = (max_breedte - item["B"]) / 2
        else:
            if "vlecht_mode" in item:
                # Gevlochten IBC's strak positioneren op basis van hun gecorrigeerde breedte
                y_pos = 20 if index == 0 else max_breedte - item["B"] - 20
            else:
                y_pos = 20 if index == 0 else max_breedte - item["B"] - 20
        
        rect = patches.Rectangle((huidige_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
        ax.add_patch(rect)
        ax.text(huidige_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        
    huidige_x += rij_lengte
    totale_meters += rij_lengte

restruimte = max_lengte - totale_meters

# 5. Resultaat tonen
st.subheader("3. Resultaat & Visuele Indeling")

if st.session_state.klik_volgorde:
    if restruimte >= 0:
        st.success(f"Dit past! Je hebt nog {restruimte} mm over in de container.")
    else:
        st.error(f"Dit past NIET! Je komt {abs(restruimte)} mm tekort.")

    st.pyplot(fig)
    st.write(f"**Gebruikte lengte:** {totale_meters} mm van de {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw = CP3 | [X] Groen = CP7 | [X] Paars = CP7 Smal | [X] Geel = IBC")
else:
    st.info("De container is nog leeg. Gebruik de + en - knoppen bij de aantallen om direct te laden.")

