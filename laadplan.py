import streamlit as st, math, matplotlib.pyplot as plt, matplotlib.patches as patches
st.set_page_config(page_title="Fons Laadplan", layout="wide")
st.markdown("<style>.block-container { padding-top: 1rem !important; } div[data-testid='stNotification'] { background-color: #9b59b6 !important; color: white !important; }</style>", unsafe_allow_html=True)

st.title("Fons Laadplan 1.0 🚛")

container_type = st.selectbox(
    "1. Kies container:", 
    ["45ft Container (13550 x 2426 mm)", "40ft Container (12030 x 2350 mm)", "20ft Container (5898 x 2350 mm)"]
)

if "45ft" in container_type:
    max_lengte = 13550  
    max_breedte = 2426  
elif "40ft" in container_type:
    max_lengte = 12030  
    max_breedte = 2350  
else:
    max_lengte = 5898   
    max_breedte = 2350  

if "klik_volgorde" not in st.session_state: st.session_state.klik_volgorde = []
if "reset_id" not in st.session_state: st.session_state.reset_id = 0

product_info = {
    "CP3": {"lengte": 1150, "breedte": 1150, "kleur": "#3498db", "stapelbaar": False},
    "CP7": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    "CP7 Smal": {"lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True},
    "IBC": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False}
}

col_titel, col_wis = st.columns([3, 1])
with col_titel:
    st.write("### 2. Vul aantal pallets in:")
with col_wis:
    if st.button("🗑️ Wis alles", type="primary", use_container_width=True):
        st.session_state.klik_volgorde = []
        st.session_state.reset_id += 1
        st.rerun()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("**CP3 (1150x1150)**")
    pallets_cp3 = st.number_input("Totaal aantal CP3", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}")
    if pallets_cp3 > 0 and "CP3" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP3")

with col2:
    st.success("**CP7 (1400x1100)**")
    pallets_cp7 = st.number_input("Totaal aantal CP7", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}")
    if pallets_cp7 > 0 and "CP7" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7")

with col3:
    st.info("**CP7 Smal (1100x1400)**")
    pallets_cp7_smal = st.number_input("Totaal aantal Smal", min_value=0, value=0, step=1, key=f"cp7_smal_{st.session_state.reset_id}")
    if pallets_cp7_smal > 0 and "CP7 Smal" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7 Smal")

with col4:
    st.warning("**IBC (1000x1200)**")
    pallets_ibc = st.number_input("Totaal aantal IBC", min_value=0, value=0, step=1, key=f"ibc_{st.session_state.reset_id}")
    if pallets_ibc > 0 and "IBC" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("IBC")

as_v_cp3, as_a_cp3 = 0, 0
as_v_cp7, as_a_cp7 = 0, 0
as_v_cp7_smal, as_a_cp7_smal = 0, 0
as_v_ibc, as_a_ibc = 0, 0

if pallets_cp3 > 0 or pallets_cp7 > 0 or pallets_cp7_smal > 0 or pallets_ibc > 0:
    with st.expander("⚖️ Klik hier voor extra aslast-regelingen (Midden vooraan/achteraan)"):
        st.write("Stuur hier de pallets naar het midden van de container. Dit wordt direct afgetrokken van het totaal.")
        v_col1, v_col2, v_col3, v_col4 = st.columns(4)
        with v_col1:
            if pallets_cp3 > 0:
                as_v_cp3 = st.number_input("CP3 Midden VOORAAN", min_value=0, max_value=pallets_cp3, value=0, step=1, key=f"v_cp3_{st.session_state.reset_id}")
                as_a_cp3 = st.number_input("CP3 Midden ACHTERAAN", min_value=0, max_value=pallets_cp3 - as_v_cp3, value=0, step=1, key=f"a_cp3_{st.session_state.reset_id}")
        with v_col2:
            if pallets_cp7 > 0:
                as_v_cp7 = st.number_input("CP7 Midden VOORAAN", min_value=0, max_value=pallets_cp7, value=0, step=1, key=f"v_cp7_{st.session_state.reset_id}")
                as_a_cp7 = st.number_input("CP7 Midden ACHTERAAN", min_value=0, max_value=pallets_cp7 - as_v_cp7, value=0, step=1, key=f"a_cp7_{st.session_state.reset_id}")
        with v_col3:
            if pallets_cp7_smal > 0:
                as_v_cp7_smal = st.number_input("Smal Midden VOORAAN", min_value=0, max_value=pallets_cp7_smal, value=0, step=1, key=f"v_cp7_smal_{st.session_state.reset_id}")
                as_a_cp7_smal = st.number_input("Smal Midden ACHTERAAN", min_value=0, max_value=pallets_cp7_smal - as_v_cp7_smal, value=0, step=1, key=f"a_cp7_smal_{st.session_state.reset_id}")
        with v_col4:
            if pallets_ibc > 0:
                as_v_ibc = st.number_input("IBC Midden VOORAAN", min_value=0, max_value=pallets_ibc, value=0, step=1, key=f"v_ibc_{st.session_state.reset_id}")
                as_a_ibc = st.number_input("IBC Midden ACHTERAAN", min_value=0, max_value=pallets_ibc - as_v_ibc, value=0, step=1, key=f"a_ibc_{st.session_state.reset_id}")

hoofd_cp3 = max(0, pallets_cp3 - as_v_cp3 - as_a_cp3)
hoofd_cp7 = max(0, pallets_cp7 - as_v_cp7 - as_a_cp7)
hoofd_cp7_smal = max(0, pallets_cp7_smal - as_v_cp7_smal - as_a_cp7_smal)
hoofd_ibc = max(0, pallets_ibc - as_v_ibc - as_a_ibc)
actuele_aantallen = {"CP3": hoofd_cp3, "CP7": hoofd_cp7, "CP7 Smal": hoofd_cp7_smal, "IBC": hoofd_ibc}

st.write("---")

laad_lijst = []
def voeg_partij_toe(art_naam, aantal, force_midden):
    if aantal > 0:
        info = product_info[art_naam]
        vloer = int(math.ceil(aantal / 2)) if info["stapelbaar"] else int(aantal)
        overgebleven = aantal
        for _ in range(vloer):
            h_label = " (2H)" if info["stapelbaar"] and overgebleven >= 2 else (" (1H)" if info["stapelbaar"] else "")
            overgebleven -= 2
            laad_lijst.append({"naam": f"{art_naam}{h_label}", "naam_puur": art_naam, "L": info["lengte"], "B": info["breedte"], "kleur": info["kleur"], "force_midden": force_midden})

voeg_partij_toe("CP3", as_v_cp3, force_midden=True)
voeg_partij_toe("CP7", as_v_cp7, force_midden=True)
voeg_partij_toe("CP7 Smal", as_v_cp7_smal, force_midden=True)
voeg_partij_toe("IBC", as_v_ibc, force_midden=True)
for art_naam in st.session_state.klik_volgorde:
    if art_naam in actuele_aantallen: voeg_partij_toe(art_naam, actuele_aantallen[art_naam], force_midden=False)
voeg_partij_toe("CP3", as_a_cp3, force_midden=True)
voeg_partij_toe("CP7", as_a_cp7, force_midden=True)
voeg_partij_toe("CP7 Smal", as_a_cp7_smal, force_midden=True)
voeg_partij_toe("IBC", as_a_ibc, force_midden=True)
# NIEUWE RIJLOGICA: Verdeel alle pallets waterdicht in opeenvolgende rijen van max 2 stuks
rijen = []
tijdelijke_rij = []
ibc_paar_teller = 0

for item in laad_lijst:
    if item["force_midden"] or item["naam_puur"] == "CP7 Smal":
        if tijdelijke_rij:
            rijen.append(tijdelijke_rij)
            tijdelijke_rij = []
        rijen.append([item])
    elif max_breedte == 2350 and item["naam_puur"] == "IBC":
        if tijdelijke_rij:
            rijen.append(tijdelijke_rij)
            tijdelijke_rij = []
        tijdelijke_rij.append(item)
        if len(tijdelijke_rij) == 1 and idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] == "IBC" and not laad_lijst[idx+1]["force_midden"]:
            pass # Wacht op de partner IBC in de lus
        if len(tijdelijke_rij) == 2 or idx == len(laad_lijst) - 1:
            rijen.append(tijdelijke_rij)
            tijdelijke_rij = []
    else:
        tijdelijke_rij.append(item)
        if len(tijdelijke_rij) == 2:
            rijen.append(tijdelijke_rij)
            tijdelijke_rij = []

if tijdelijke_rij:
    rijen.append(tijdelijke_rij)

fig, ax = plt.subplots(figsize=(15, 3.5))
ax.set_xlim(0, max_lengte); ax.set_ylim(0, max_breedte); ax.set_aspect('equal', adjustable='box')
container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

huidige_x = 0
for rij in rijen:
    rij_lengte = max([item["L"] for item in rij])
    is_midden_rij = len(rij) == 1 and (rij[0]["force_midden"] or rij[0]["naam_puur"] == "CP7 Smal")
    
    # Check voor gevlochten IBC's in een smalle container
    is_ibc_vlecht_rij = max_breedte == 2350 and len(rij) == 2 and rij[0]["naam_puur"] == "IBC" and rij[1]["naam_puur"] == "IBC"
    if is_ibc_vlecht_rij:
        rij_lengte = 1100  # Gecorrigeerde vlecht-laadlengte

    for index, item in enumerate(rij):
        vulling_kleur = "#e74c3c" if (huidige_x + item["L"] > max_lengte) else item["kleur"]
        
        if is_midden_rij:
            y_pos = (max_breedte - item["B"]) / 2
            rect = patches.Rectangle((huidige_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=vulling_kleur, alpha=0.8)
            ax.add_patch(rect)
            ax.text(huidige_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        elif is_ibc_vlecht_rij:
            if ibc_paar_teller % 2 == 0:
                l_dim = 1000 if index == 0 else 1200
                b_dim = 1200 if index == 0 else 1000
                lbl = "IBC (Breed)" if index == 0 else "IBC (Lang)"
                y_pos = 20 if index == 0 else max_breedte - b_dim - 20
            else:
                l_dim = 1200 if index == 0 else 1000
                b_dim = 1000 if index == 0 else 1200
                lbl = "IBC (Lang)" if index == 0 else "IBC (Breed)"
                y_pos = 20 if index == 0 else max_breedte - b_dim - 20
                
            rect = patches.Rectangle((huidige_x, y_pos), l_dim, b_dim, linewidth=1, edgecolor='white', facecolor=vulling_kleur, alpha=0.8)
            ax.add_patch(rect)
            ax.text(huidige_x + (l_dim/2), y_pos + (b_dim/2), lbl, color="black", weight="bold", ha="center", va="center", fontsize=7)
        else:
            y_pos = 20 if index == 0 else max_breedte - item["B"] - 20
            rect = patches.Rectangle((huidige_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=vulling_kleur, alpha=0.8)
            ax.add_patch(rect)
            ax.text(huidige_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
            
    if is_ibc_vlecht_rij:
        ibc_paar_teller += 1
    huidige_x += rij_lengte

restruimte = max_lengte - huidige_x
st.write("### 3. Plan:")
if pallets_cp3+pallets_cp7+pallets_cp7_smal+pallets_ibc > 0 or as_v_cp3+as_v_cp7+as_v_cp7_smal+as_v_ibc+as_a_cp3+as_a_cp7+as_a_cp7_smal+as_a_ibc > 0:
    if restruimte >= 0: st.success(f"✅ Past! Nog {restruimte} mm over.")
    else: st.error(f"❌ Past NIET! {abs(restruimte)} mm tekort.")
    st.pyplot(fig)
    st.write(f"**Geladen:** {huidige_x} mm van {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw=CP3 | [X] Groen=CP7 | [X] Paars=CP7 Smal | [X] Geel=IBC | [X] ROOD = Past Niet")
else: st.info("Container is leeg. Gebruik de + en - knoppen om te beginnen.")
