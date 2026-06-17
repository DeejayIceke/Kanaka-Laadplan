import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Compacte pagina-instelling
st.set_page_config(page_title="Fons Laadplan", layout="wide")

# CSS om de lege witruimte aan de bovenkant van het scherm op de iPhone te verminderen
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
st.write("### 2. Vul aantallen in:")
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

if st.button("🗑️ Wis alles (Reset naar 0)", type="primary", use_container_width=True):
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

# 4. Teken Layout Setup
fig, ax = plt.subplots(figsize=(15, 3.5))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_aspect('equal', adjustable='box')

container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

# Tracking van laadlijnen
x_onder = 0
x_boven = 0
ibc_paar_teller = 0

idx = 0
while idx < len(laad_lijst):
    item = laad_lijst[idx]
    
    if max_breedte == 2350 and item["naam_puur"] == "IBC":
        heeft_partner = (idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] == "IBC")
        
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
        else:
            start_x = max(x_onder, x_boven)
            rect = patches.Rectangle((start_x, 20), 1000, 1200, linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
            ax.add_patch(rect)
            ax.text(start_x + 500, 20 + 600, "IBC (Breed)", color="black", weight="bold", ha="center", va="center", fontsize=7)
            x_onder = start_x + 1000
            x_boven = start_x
            idx += 1
            continue
            
    else:
        start_x = max(x_onder, x_boven)
        
        if item["naam_puur"] == "CP7 Smal":
            y_pos = (max_breedte - item["B"]) / 2
            rect = patches.Rectangle((start_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
            ax.add_patch(rect)
            ax.text(start_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
            x_onder = start_x + item["L"]
            x_boven = start_x + item["L"]
            idx += 1
        else:
            heeft_buur = (idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] != "CP7 Smal")
            
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
restruimte = max_lengte - totale_meters

# 5. Resultaat tonen
st.write("### 3. Plan:")

if st.session_state.klik_volgorde:
    if restruimte >= 0:
        st.success(f"✅ Past! Nog {restruimte} mm over.")
    else:
        st.error(f"❌ Past NIET! {abs(restruimte)} mm tekort.")
    st.pyplot(fig)
    st.write(f"**Geladen:** {totale_meters} mm van {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw=CP3 | [X] Groen=CP7 | [X] Paars=CP7 Smal | [X] Geel=IBC")
else:
    st.info("Container is leeg. Gebruik de + en - knoppen om te beginnen.")
