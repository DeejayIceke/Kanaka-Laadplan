import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Kaneka Visueel Laadplan", layout="wide")
st.title("📦 Kaneka Visueel Laadplan Dashboard")
st.write("Vul direct de aantallen in. De app laadt de pallets automatisch in de volgorde van jouw invoer.")

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

# Initialiseer de dynamische geschiedenis in het geheugen
if "laad_geschiedenis" not in st.session_state:
    st.session_state.laad_geschiedenis = []
if "vorige_aantallen" not in st.session_state:
    st.session_state.vorige_aantallen = {"CP3": 0, "CP7": 0, "CP7 Smal": 0, "IBC": 0}
if "reset_id" not in st.session_state:
    st.session_state.reset_id = 0

# Definieer de vaste productspecificaties
product_info = {
    "CP3": {"lengte": 1140, "breedte": 1140, "kleur": "#3498db", "stapelbaar": False},
    "CP7": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    "CP7 Smal": {"lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True},
    "IBC": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False}
}

# 2. Invoer Pallets - Directe invoer naast elkaar
st.subheader("2. Vul het aantal pallets in")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pallets_cp3 = st.number_input("Aantal CP3 (1140x1140)", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}")
with col2:
    pallets_cp7 = st.number_input("Aantal CP7 (1400x1100)", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}")
with col3:
    pallets_cp7_smal = st.number_input("Aantal CP7 Smal (1100x1400)", min_value=0, value=0, step=1, key=f"cp7_smal_{st.session_state.reset_id}")
with col4:
    pallets_ibc = st.number_input("Aantal IBC's (1000x1200)", min_value=0, value=0, step=1, key=f"ibc_{st.session_state.reset_id}")

# Live detecteren welk invoerveld is veranderd en dit ACHTERAAN toevoegen
actuele_aantallen = {"CP3": pallets_cp3, "CP7": pallets_cp7, "CP7 Smal": pallets_cp7_smal, "IBC": pallets_ibc}
heeft_wijziging = False

for art, aantal in actuele_aantallen.items():
    vorige = st.session_state.vorige_aantallen.get(art, 0)
    if aantal > vorige:
        # Er zijn pallets bijgekomen -> voeg het verschil als nieuwe partij achteraan toe!
        st.session_state.laad_geschiedenis.append({"naam": art, "aantal": aantal - vorige})
        heeft_wijziging = True
    elif aantal < vorige:
        # Er zijn pallets afgehaald -> verminder de stappen in de geschiedenis van achter naar voren
        verschil = vorige - aantal
        for item in reversed(st.session_state.laad_geschiedenis):
            if item["naam"] == art:
                if item["aantal"] >= verschil:
                    item["aantal"] -= verschil
                    verschil = 0
                    break
                else:
                    verschil -= item["aantal"]
                    item["aantal"] = 0
        # Schoon lege items op
        st.session_state.laad_geschiedenis = [i for i in st.session_state.laad_geschiedenis if i["aantal"] > 0]
        heeft_wijziging = True

if heeft_wijziging:
    st.session_state.vorige_aantallen = actuele_aantallen.copy()
    st.rerun()

# De WISKNOP die direct alle invoervelden en het plan leegmaakt
st.write("---")
if st.button("🗑️ Wis alle velden en container (Reset volledig naar 0)", type="primary", use_container_width=True):
    st.session_state.laad_geschiedenis = []
    st.session_state.vorige_aantallen = {"CP3": 0, "CP7": 0, "CP7 Smal": 0, "IBC": 0}
    st.session_state.reset_id += 1
    st.rerun()

# 3. Logistieke Logica: Bouw de laadlijst op
laad_lijst = []
# Onthoud hoeveel pallets er per type al zijn verwerkt voor de juiste (1H/2H) labels
teller_per_type = {"CP3": 0, "CP7": 0, "CP7 Smal": 0, "IBC": 0}

for item in st.session_state.laad_geschiedenis:
    info = product_info[item["naam"]]
    
    if info["stapelbaar"]:
        vloerplaatsen = int(math.ceil(item["aantal"] / 2))
    else:
        vloerplaatsen = int(item["aantal"])
        
    overgebleven = item["aantal"]
    
    for _ in range(vloerplaatsen):
        if info["stapelbaar"]:
            hoogte_label = " (2H)" if overgebleven >= 2 else " (1H)"
            overgebleven -= 2
        else:
            hoogte_label = ""
            
        laad_lijst.append({
            "naam": f"{item['naam']}{hoogte_label}", 
            "naam_puur": item["naam"],
            "L": info["lengte"], 
            "B": info["breedte"], 
            "kleur": info["kleur"]
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

# 5. Resultaat tonen
st.subheader("3. Resultaat & Visuele Indeling")

if st.session_state.laad_geschiedenis:
    if restruimte >= 0:
        st.success(f"Dit past! Je hebt nog {restruimte} mm over in de container.")
    else:
        st.error(f"Dit past NIET! Je komt {abs(restruimte)} mm tekort.")

    st.pyplot(fig)
    st.write(f"**Gebruikte lengte:** {totale_meters} mm van de {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw = CP3 | [X] Groen = CP7 | [X] Paars = CP7 Smal | [X] Geel = IBC")
else:
    st.info("De container is nog leeg. Gebruik de + en - knoppen bij de aantallen om direct te laden.")
