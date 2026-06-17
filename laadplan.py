import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Fons Laadplan", layout="wide")
st.markdown("<style>.block-container { padding-top: 1rem !important; }</style>", unsafe_allow_html=True)
st.title("Fons Laadplan 1.0 🚛")

container_type = st.selectbox("1. Kies container:", ["45ft Container", "40ft Container", "20ft Container"])
max_lengte = 13550 if container_type == "45ft Container" else 12030 if container_type == "40ft Container" else 5898
max_breedte = 2426 if container_type == "45ft Container" else 2350
st.caption(f"📐 Formaat: {max_lengte} mm lang x {max_breedte} mm breed.")

if "klik_volgorde" not in st.session_state: st.session_state.klik_volgorde = []
if "reset_id" not in st.session_state: st.session_state.reset_id = 0

product_info = {
    "CP3": {"lengte": 1140, "breedte": 1140, "kleur": "#3498db", "stapelbaar": False},
    "CP7": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    "CP7 Smal": {"lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True},
    "IBC": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False}
}

st.write("### 2. Vul aantallen in per artikel:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("**CP3 (1140x1140)**")
    pallets_cp3 = st.number_input("Totaal aantal CP3", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}")
    as_v_cp3 = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_cp3_{st.session_state.reset_id}")
    as_a_cp3 = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_cp3_{st.session_state.reset_id}")
    if pallets_cp3 > 0 and "CP3" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP3")

with col2:
    st.success("**CP7 (1400x1100)**")
    pallets_cp7 = st.number_input("Totaal aantal CP7", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}")
    as_v_cp7 = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_cp7_{st.session_state.reset_id}")
    as_a_cp7 = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_cp7_{st.session_state.reset_id}")
    if pallets_cp7 > 0 and "CP7" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7")

with col3:
    st.markdown("<style>div[data-testid='stNotification'] { background-color: #9b59b6 !important; color: white !important; }</style>", unsafe_allow_html=True)
    st.info("**CP7 Smal (1100x1400)**")
    pallets_cp7_smal = st.number_input("Totaal aantal Smal", min_value=0, value=0, step=1, key=f"cp7_smal_{st.session_state.reset_id}")
    as_v_cp7_smal = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_cp7_smal_{st.session_state.reset_id}")
    as_a_cp7_smal = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_cp7_smal_{st.session_state.reset_id}")
    if pallets_cp7_smal > 0 and "CP7 Smal" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7 Smal")

with col4:
    st.warning("**IBC (1000x1200)**")
    pallets_ibc = st.number_input("Totaal aantal IBC", min_value=0, value=0, step=1, key=f"ibc_{st.session_state.reset_id}")
    as_v_ibc = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_ibc_{st.session_state.reset_id}")
    as_a_ibc = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_ibc_{st.session_state.reset_id}")
    if pallets_ibc > 0 and "IBC" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("IBC")

hoofd_cp3 = max(0, pallets_cp3 - as_v_cp3 - as_a_cp3)
hoofd_cp7 = max(0, pallets_cp7 - as_v_cp7 - as_a_cp7)
hoofd_cp7_smal = max(0, pallets_cp7_smal - as_v_cp7_smal - as_a_cp7_smal)
hoofd_ibc = max(0, pallets_ibc - as_v_ibc - as_a_ibc)
actuele_aantallen = {"CP3": hoofd_cp3, "CP7": hoofd_cp7, "CP7 Smal": hoofd_cp7_smal, "IBC": hoofd_ibc}

st.write("---")
if st.button("🗑️ Wis alle velden (Reset naar 0)", type="primary", use_container_width=True):
    st.session_state.klik_volgorde = []
    st.session_state.reset_id += 1
    st.rerun()

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
fig, ax = plt.subplots(figsize=(15, 3.5))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_aspect('equal', adjustable='box')
container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

x_onder, x_boven, ibc_paar_teller, idx = 0, 0, 0, 0
while idx < len(laad_lijst):
    item = laad_lijst[idx]
    if item["force_midden"] or item["naam_puur"] == "CP7 Smal":
        start_x = max(x_onder, x_boven)
        y_pos = (max_breedte - item["B"]) / 2
        rect = patches.Rectangle((start_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
        ax.add_patch(rect)
        ax.text(start_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        x_onder, x_boven = start_x + item["L"], start_x + item["L"]
        idx += 1
        continue
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
                x_onder, x_boven = x_pos_onder + 1000, x_pos_boven + 1200
            else:
                rect1 = patches.Rectangle((x_onder, 20), 1200, 1000, linewidth=1, edgecolor='white', facecolor=item["kleur'], alpha=0.8)
                ax.add_patch(rect1)
                ax.text(x_onder + 600, 20 + 500, "IBC (Lang)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                rect2 = patches.Rectangle((x_boven, max_breedte - 1200 - 20), 1000, 1200, linewidth=1, edgecolor='white', facecolor=item["kleur"], alpha=0.8)
                ax.add_patch(rect2)
                ax.text(x_boven + 500, max_breedte - 1200 - 20 + 600, "IBC (Breed)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                x_onder, x_boven = x_onder + 1200, x_boven + 1000
            ibc_paar_teller += 1
            idx += 2
            continue
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
        x_onder, x_boven = start_x + item["L"], start_x + item2["L"]
        max_r = max(x_onder, x_boven)
        x_onder, x_boven = max_r, max_r
        idx += 2
    else:
        x_onder, x_boven = start_x + item["L"], start_x
        idx += 1

totale_meters = max(x_onder, x_boven)
restruimte = max_lengte - totale_meters

st.write("### 3. Plan:")
if pallets_cp3+pallets_cp7+pallets_cp7_smal+pallets_ibc > 0 or as_v_cp3+as_v_cp7+as_v_cp7_smal+as_v_ibc+as_a_cp3+as_a_cp7+as_a_cp7_smal+as_a_ibc > 0:
    if restruimte >= 0: st.success(f"✅ Past! Nog {restruimte} mm over.")
    else: st.error(f"❌ Past NIET! {abs(restruimte)} mm tekort.")
    st.pyplot(fig)
    st.write(f"**Geladen:** {totale_meters} mm van {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw=CP3 | [X] Groen=CP7 | [X] Paars=CP7 Smal | [X] Geel=IBC")
else: st.info("Container is leeg. Gebruik de + en - knoppen om te beginnen.")
