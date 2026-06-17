import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Compacte pagina-instelling
st.set_page_config(page_title="Fons Laadplan", layout="wide")

# CSS voor minder scrollen op mobiel
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    </style>
""", unsafe_allow_html=True)

st.title("Fons Laadplan 🚛")

# 1. Container Keuze
container_type = st.selectbox(
    "1. Kies container:", 
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

st.caption(f"📐 Formaat: {max_lengte} mm lang x {max_breedte} mm breed.")

# Initialiseer het geheugen
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

# 2. Invoer Hoofdaantallen (Normaal/Dubbel laden)
st.write("### 2. Vul hoofdaantallen in (Dubbel laden):")
col1, col2, col3, col4 = st.columns(4)

with col1:
    pallets_cp3 = st.number_input("Aantal CP3", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}")
    if pallets_cp3 > 0 and "CP3" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("CP3")

with col2:
    pallets_cp7 = st.number_input("Aantal CP7", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}")
    if pallets_cp7 > 0 and "CP7" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("CP7")

with col3:
    pallets_cp7_smal = st.number_input("Aantal CP7 Smal", min_value=0, value=0, step=1, key=f"cp7_smal_{st.session_state.reset_id}")
    if pallets_cp7_smal > 0 and "CP7 Smal" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("CP7 Smal")

with col4:
    pallets_ibc = st.number_input("Aantal IBC's", min_value=0, value=0, step=1, key=f"ibc_{st.session_state.reset_id}")
    if pallets_ibc > 0 and "IBC" not in st.session_state.klik_volgorde:
        st.session_state.klik_volgorde.append("IBC")

# Optionele Aslast regelingen
st.write("### ⚖️ Extra Aslast Regelingen Midden (Optioneel):")
col_v1, col_v2 = st.columns(2)
with col_v1:
    aslast_v_type = st.selectbox("Type in het midden VOORAAN:", ["Geen", "CP3", "CP7", "CP7 Smal", "IBC"], key=f"as_v_t_{st.session_state.reset_id}")
with col_v2:
    aslast_v_aantal = st.number_input("Aantal stuks vooraan:", min_value=0, value=0, step=1, key=f"as_v_a_{st.session_state.reset_id}")

col_a1, col_a2 = st.columns(2)
with col_a1:
    aslast_a_type = st.selectbox("Type in het midden ACHTERAAN:", ["Geen", "CP3", "CP7", "CP7 Smal", "IBC"], key=f"as_a_t_{st.session_state.reset_id}")
with col_a2:
    aslast_a_aantal = st.number_input("Aantal stuks achteraan:", min_value=0, value=0, step=1, key=f"as_a_a_{st.session_state.reset_id}")

actuele_aantallen = {"CP3": pallets_cp3, "CP7": pallets_cp7, "CP7 Smal": pallets_cp7_smal, "IBC": pallets_ibc}
st.session_state.klik_volgorde = [art for art in st.session_state.klik_volgorde if actuele_aantallen[art] > 0]

# De WISKNOP
if st.button("🗑️ Wis alles (Reset naar 0)", type="primary", use_container_width=True):
    st.session_state.klik_volgorde = []
    st.session_state.reset_id += 1
    st.rerun()

# 3. Logistieke Logica: Bouw de complete laadlijst op
laad_lijst = []

def voeg_aslast_toe(art_naam, aantal):
    if art_naam != "Geen" and aantal > 0:
        info = product_info[art_naam]
        vloer = int(math.ceil(aantal / 2)) if info["stapelbaar"] else int(aantal)
        overgebleven = aantal
        for _ in range(vloer):
            h_label = " (2H)" if info["stapelbaar"] and overgebleven >= 2 else (" (1H)" if info["stapelbaar"] else "")
            overgebleven -= 2
            laad_lijst.append({
                "naam": f"{art_naam}{h_label}", "naam_puur": art_naam,
                "L": info["lengte"], "B": info["breedte"], "kleur": info["kleur"], "force_midden": True
            })

# DEEL 1: Vooraan in het midden
voeg_aslast_toe(aslast_v_type, aslast_v_aantal)

# DEEL 2: De normale hoofdaantallen (volgorde van klikken)
for art_naam in st.session_state.klik_volgorde:
    total_pallets = actuele_aantallen[art_naam]
    info = product_info[art_naam]
    vloerplaatsen = int(math.ceil(total_pallets / 2)) if info["stapelbaar"] else int(total_pallets)
    overgebleven = total_pallets
    for _ in range(vloerplaatsen):
        h_label = " (2H)" if info["stapelbaar"] and overgebleven >= 2 else (" (1H)" if info["stapelbaar"] else "")
        overgebleven -= 2
        laad_lijst.append({
            "naam": f"{art_naam}{h_label}", "naam_puur": art_naam,
            "L": info["lengte"], "B": info["breedte"], "kleur": info["kleur"], "force_midden": False
        })

# DEEL 3: Achteraan in het midden
voeg_aslast_toe(aslast_a_type, aslast_a_aantal)

# 4. Teken Layout Setup
fig, ax = plt.subplots(figsize=(15, 3.5))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_aspect('equal', adjustable='box')

container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

x_onder = 0
x_boven = 0
ibc_paar_teller = 0

idx = 0
while idx < len(laad_lijst):
    item = laad_lijst[idx]
    
    # Aslast / Geforceerd midden (of de CP7 Smal die altijd alleen staat)
    if item["force_midden"] or item["naam_puur"] == "CP7 Smal":
        start_x = max(x_onder, x_boven)
        y_pos = (max_breedte - item["B"]) / 2
        rect = patches.Rectangle((start_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
        ax.add_patch(rect)
        ax.text(start_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        x_onder = start_x + item["L"]
        x_boven = start_x + item["L"]
        idx += 1
        continue

    # Gevlochten IBC logica (Alleen voor de normale, niet-geforceerde IBC's in 40ft/20ft)
    if max_breedte == 2350 and item["naam_puur"] == "IBC":
        heeft_partner = (idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] == "IBC" and not laad_lijst[idx+1]["force_midden"])
        if heeft_partner:
            if ibc_paar_teller % 2 == 0:
                x_pos_onder = max(x_onder, x_boven) if ibc_paar_teller == 0 else x_onder
                rect1 = patches.Rectangle((x_pos_onder, 20), 1000, 1200, linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
                ax.add_patch(rect1)
                ax.text(x_pos_onder + 500, 20 + 600, "IBC (Breed)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                
                x_pos_boven = max(x_onder, x_boven) if ibc_paar_teller == 0 else x_boven
                rect2 = patches.Rectangle((x_pos_boven, max_breedte - 1000 - 20), 1200, 1000, linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
                ax.add_patch(rect2)
                ax.text(x_pos_boven + 600, max_breedte - 1000 - 20 + 500, "IBC (Lang)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                
                x_onder = x_pos_onder + 1000
                x_boven = x_pos_boven + 1200
            else:
                rect1 = patches.Rectangle((x_onder, 20), 1200, 1000, linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
                ax.add_patch(rect1)
                ax.text(x_onder + 600, 20 + 500, "IBC (Lang)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                
                rect2 = patches.Rectangle((x_boven, max_breedte - 1200 - 20), 1000, 1200, linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
                ax.add_patch(rect2)
                ax.text(x_boven + 500, max_breedte - 1200 - 20 + 600, "IBC (Breed)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                
                x_onder += 1200
                x_boven += 1000
            ibc_paar_teller += 1
            idx += 2
            continue

    # Normale pallets zijkanten (per 2 naast elkaar)
    start_x = max(x_onder, x_boven)
    heeft_buur = (idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] != "CP7 Smal" and not laad_lijst[idx+1]["force_midden"])
    
    rect1 = patches.Rectangle((start_x, 20), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
    ax.add_patch(rect1)
    ax.text(start_x + (item["L"]/2), 20 + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
    
    if heeft_buur:
        item2 = laad_lijst[idx+1]
        rect2 = patches.Rectangle((start_x, max_breedte - item2["B"] - 20), item2["L"], item2["B"], linewidth=1, edgecolor='white', facecolor=item2["kleur"], alpha=0.8)
        ax.add_patch(rect2)
        ax.text(start_x + (item2["L"]/2), max_breedte - item2["B"] - 20 + (item2["B"]/2), item2["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        x_onder = start_x + item["L"]
        x_boven = start_x + item2["L"]
        max_r = max(x_onder, x_boven)
        x_onder = max_r
        x_boven = max_r
        idx += 2
    else:
        x_onder = start_x + item["L"]
        x_boven = start_x
        idx += 1

# Eindstand bepalen
totale_meters = max(x_onder, x_boven)
