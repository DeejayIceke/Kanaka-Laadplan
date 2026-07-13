import streamlit as st, math, matplotlib.pyplot as plt, matplotlib.patches as patches
st.set_page_config(page_title="Fons Laadplan", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; }
        div[data-testid="stColumn"] { display: flex; flex-direction: column; }
        .custom-box {
            padding: 0.45rem; border-radius: 0.5rem; color: white; font-weight: bold; 
            font-size: 14px; text-align: center; margin-bottom: 0.25rem;
            min-height: 43px; display: flex; align-items: center; justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Fons Laadplan 🚛")
st.title("Fons Laadplan 1.0 🚛")

container_type = st.selectbox(
    "1. Kies container:", 
    ["45ft Container (13550 x 2426 mm)", "40ft Container (12030 x 2350 mm)", "20ft Container (5898 x 2350 mm)"]
)

max_lengte = 13550 if "45ft" in container_type else 12030 if "40ft" in container_type else 5898
max_breedte = 2426 if "45ft" in container_type else 2350

if "klik_volgorde" not in st.session_state: st.session_state.klik_volgorde = []
if "reset_id" not in st.session_state: st.session_state.reset_id = 0

# CP7 Smal is hier verwijderd uit de hoofdproducten, we laden hem dynamisch via de aslast
product_info = {
    "CP3": {"lengte": 1150, "breedte": 1150, "kleur": "#3498db", "stapelbaar": False},
    "CP7": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True},
    "IBC": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False},
    "CP9": {"lengte": 1150, "breedte": 1150, "kleur": "#e67e22", "stapelbaar": False},
    "Maatwerk": {"lengte": 1000, "breedte": 1000, "kleur": "#7f8c8d", "stapelbaar": False}
}

# DIRECT GEFIXT: De haakjes bevatten nu een verplichte 2 zodat Streamlit NOOIT meer crasht!
col_titel, col_wis = st.columns(2)
with col_titel: st.write("### 2. Vul aantal pallets in:")
with col_wis:
    if st.button("🗑️ Wis alles", type="primary", use_container_width=True):
        st.session_state.klik_volgorde = []
        st.session_state.reset_id += 1
        st.rerun()

# Terug naar 5 strakke hoofd-kolommen zonder de losse CP7 Smal knop
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown('<div class="custom-box" style="background-color:#3498db;">CP3 (1150x1150)</div>', unsafe_allow_html=True)
    pallets_cp3 = st.number_input("Aantal CP3", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}", label_visibility="collapsed")
    if pallets_cp3 > 0 and "CP3" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP3")

with col2:
    st.markdown('<div class="custom-box" style="background-color:#2ecc71;">CP7 (1400x1100)</div>', unsafe_allow_html=True)
    pallets_cp7_totaal = st.number_input("Aantal CP7", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}", label_visibility="collapsed")

with col3:
    st.markdown('<div class="custom-box" style="background-color:#f1c40f; color:black;">IBC (1000x1200)</div>', unsafe_allow_html=True)
    pallets_ibc = st.number_input("Aantal IBC", min_value=0, value=0, step=1, key=f"ibc_{st.session_state.reset_id}", label_visibility="collapsed")
    if pallets_ibc > 0 and "IBC" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("IBC")

with col4:
    st.markdown('<div class="custom-box" style="background-color:#e67e22;">CP9 (1150x1150)</div>', unsafe_allow_html=True)
    pallets_cp9 = st.number_input("Aantal CP9", min_value=0, value=0, step=1, key=f"cp9_{st.session_state.reset_id}", label_visibility="collapsed")
    if pallets_cp9 > 0 and "CP9" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP9")

with col5:
    st.markdown('<div class="custom-box" style="background-color:#7f8c8d;">Maatwerk 📐</div>', unsafe_allow_html=True)
    pallets_mw = st.number_input("Aantal Maatwerk", min_value=0, value=0, step=1, key=f"mw_{st.session_state.reset_id}", label_visibility="collapsed")
    if pallets_mw > 0:
        if "Maatwerk" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("Maatwerk")
        mw_L = st.number_input("L (mm):", min_value=1, value=1000, step=10, key=f"mw_l_{st.session_state.reset_id}")
        mw_B = st.number_input("B (mm):", min_value=1, value=1000, step=10, key=f"mw_b_{st.session_state.reset_id}")
        product_info["Maatwerk"]["lengte"] = mw_L
        product_info["Maatwerk"]["breedte"] = mw_B

as_v_cp3, as_a_cp3 = 0, 0
as_v_cp7, as_a_cp7 = 0, 0
as_v_ibc, as_a_ibc = 0, 0
as_v_cp9, as_a_cp9 = 0, 0
as_v_mw, as_a_mw = 0, 0

richting_v_cp7 = "Lang (1400x1100)"
richting_a_cp7 = "Lang (1400x1100)"

if pallets_cp3 + pallets_cp7_totaal + pallets_ibc + pallets_cp9 + pallets_mw > 0:
    with st.expander("⚖️ Klik hier voor extra aslast-regelingen (Midden vooraan/achteraan)"):
        v_col1, v_col2, v_col3, v_col4, v_col5 = st.columns(5)
        with v_col1:
            if pallets_cp3 > 0:
                as_v_cp3 = st.number_input("CP3 VOR", min_value=0, max_value=pallets_cp3, value=0, step=1, key=f"v_cp3_{st.session_state.reset_id}")
                as_a_cp3 = st.number_input("CP3 ACH", min_value=0, max_value=pallets_cp3 - as_v_cp3, value=0, step=1, key=f"a_cp3_{st.session_state.reset_id}")
        with v_col2:
            if pallets_cp7_totaal > 0:
                as_v_cp7 = st.number_input("CP7 VOR", min_value=0, max_value=pallets_cp7_totaal, value=0, step=1, key=f"v_cp7_{st.session_state.reset_id}")
                if as_v_cp7 > 0:
                    richting_v_cp7 = st.radio("Richting VOR:", ["Lang (1400x1100)", "Smal (1100x1400)"], key=f"r_v_cp7_{st.session_state.reset_id}")

                as_a_cp7 = st.number_input("CP7 ACH", min_value=0, max_value=pallets_cp7_totaal - as_v_cp7, value=0, step=1, key=f"a_cp7_{st.session_state.reset_id}")
                if as_a_cp7 > 0:
                    richting_a_cp7 = st.radio("Richting ACH:", ["Lang (1400x1100)", "Smal (1100x1400)"], key=f"r_a_cp7_{st.session_state.reset_id}")
        with v_col3:
            if pallets_ibc > 0:
                as_v_ibc = st.number_input("IBC VOR", min_value=0, max_value=pallets_ibc, value=0, step=1, key=f"v_ibc_{st.session_state.reset_id}")
                as_a_ibc = st.number_input("IBC ACH", min_value=0, max_value=pallets_ibc - as_v_ibc, value=0, step=1, key=f"a_ibc_{st.session_state.reset_id}")
        with v_col4:
            if pallets_cp9 > 0:
                as_v_cp9 = st.number_input("CP9 VOR", min_value=0, max_value=pallets_cp9, value=0, step=1, key=f"v_cp9_{st.session_state.reset_id}")
                as_a_cp9 = st.number_input("CP9 ACH", min_value=0, max_value=pallets_cp9 - as_v_cp9, value=0, step=1, key=f"a_cp9_{st.session_state.reset_id}")
        with v_col5:
            if pallets_mw > 0:
                as_v_mw = st.number_input("MW VOR", min_value=0, max_value=pallets_mw, value=0, step=1, key=f"v_mw_{st.session_state.reset_id}")
                as_a_mw = st.number_input("MW ACH", min_value=0, max_value=pallets_mw - as_v_mw, value=0, step=1, key=f"a_mw_{st.session_state.reset_id}")

hoofd_cp7 = max(0, pallets_cp7_totaal - as_v_cp7 - as_a_cp7)
if pallets_cp7_totaal > 0 and "CP7" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7")

with col2:
    if pallets_cp7_totaal > 0: st.write(f"➡️ **Gewone CP7 over:** {hoofd_cp7}")
# INFO-TEKST IS HIER VOLLEDIG VERWIJDERD VOOR MEER RUIMTE

hoofd_cp3 = max(0, pallets_cp3 - as_v_cp3 - as_a_cp3)
hoofd_ibc = max(0, pallets_ibc - as_v_ibc - as_a_ibc)
hoofd_cp9 = max(0, pallets_cp9 - as_v_cp9 - as_a_cp9)
hoofd_mw = max(0, pallets_mw - as_v_mw - as_a_mw)
actuele_aantallen = {"CP3": hoofd_cp3, "CP7": hoofd_cp7, "IBC": hoofd_ibc, "CP9": hoofd_cp9, "Maatwerk": hoofd_mw}

laad_lijst = []
def voeg_partij_toe_aslast(art_naam, aantal, richting):
    if aantal > 0:
        info = product_info[art_naam].copy()
        if art_naam == "CP7" and "Smal" in richting:
            info["lengte"], info["breedte"], info["kleur"] = 1100, 1400, "#9b59b6"

        vloer = int(math.ceil(aantal / 2)) if info["stapelbaar"] else int(aantal)
        overgebleven = aantal
        for _ in range(vloer):
            h_label = " (2H)" if info["stapelbaar"] and overgebleven >= 2 else (" (1H)" if info["stapelbaar"] else "")
            overgebleven -= 2
            laad_lijst.append({"naam": f"{art_naam}{h_label}", "naam_puur": art_naam, "L": info["lengte"], "B": info["breedte"], "kleur": info["kleur"], "force_midden": True})

def voeg_partij_toe(art_naam, aantal):
    if aantal > 0:
        info = product_info[art_naam]
        vloer = int(math.ceil(aantal / 2)) if info["stapelbaar"] else int(aantal)
        overgebleven = aantal
        for _ in range(vloer):
            h_label = " (2H)" if info["stapelbaar"] and overgebleven >= 2 else (" (1H)" if info["stapelbaar"] else "")
            
            if art_naam == "CP7" and overgebleven >= 2:
                gekozen_kleur = "#1b5e20"  # Stevig Donker Bosgroen (2H)
            elif art_naam == "CP7":
                gekozen_kleur = "#00ff66"  # Fel Neon Lichtgroen (1H)
            else:
                gekozen_kleur = info["kleur"]  # Standaardkleur voor de rest

            overgebleven -= 2
            laad_lijst.append({"naam": f"{art_naam}{h_label}", "naam_puur": art_naam, "L": info["lengte"], "B": info["breedte"], "kleur": gekozen_kleur, "force_midden": False})


voeg_partij_toe_aslast("CP3", as_v_cp3, "Lang")
voeg_partij_toe_aslast("CP7", as_v_cp7, richting_v_cp7)
voeg_partij_toe_aslast("IBC", as_v_ibc, "Lang")
voeg_partij_toe_aslast("CP9", as_v_cp9, "Lang")
voeg_partij_toe_aslast("Maatwerk", as_v_mw, "Lang")

for art_naam in st.session_state.klik_volgorde:
    if art_naam in actuele_aantallen: voeg_partij_toe(art_naam, actuele_aantallen[art_naam])

voeg_partij_toe_aslast("CP3", as_a_cp3, "Lang")
voeg_partij_toe_aslast("CP7", as_a_cp7, richting_a_cp7)
voeg_partij_toe_aslast("IBC", as_a_ibc, "Lang")
voeg_partij_toe_aslast("CP9", as_a_cp9, "Lang")
voeg_partij_toe_aslast("Maatwerk", as_a_mw, "Lang")
fig, ax = plt.subplots(figsize=(15, 3.5))
ax.set_xlim(0, max_lengte); ax.set_ylim(0, max_breedte); ax.set_aspect('equal', adjustable='box')
container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

x_onder, x_boven, ibc_paar_teller, idx = 0, 0, 0, 0
while idx < len(laad_lijst):
    item = laad_lijst[idx]
    if item["force_midden"]:
        start_x = max(x_onder, x_boven)
        vulling_kleur = "#e74c3c" if (start_x + item["L"] > max_lengte) else item["kleur"]
        y_pos = (max_breedte - item["B"]) / 2
        rect = patches.Rectangle((start_x, y_pos), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=vulling_kleur, alpha=0.8)
        ax.add_patch(rect)
        ax.text(start_x + (item["L"]/2), y_pos + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=11)
        x_onder, x_boven = start_x + item["L"], start_x + item["L"]
        idx += 1
        continue
    if max_breedte == 2350 and item["naam_puur"] == "IBC":
        heeft_partner = (idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] == "IBC" and not laad_lijst[idx+1]["force_midden"])
        if heeft_partner:
            if ibc_paar_teller % 2 == 0:
                x_pos_onder = max(x_onder, x_boven) if ibc_paar_teller == 0 else x_onder
                vulling_kleur1 = "#e74c3c" if (x_pos_onder + 1000 > max_lengte) else item["kleur"]
                rect1 = patches.Rectangle((x_pos_onder, 20), 1000, 1200, linewidth=1, edgecolor='white', facecolor=vulling_kleur1, alpha=0.8)
                ax.add_patch(rect1)
                ax.text(x_pos_onder + 500, 20 + 600, "IBC (Breed)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                x_pos_boven = max(x_onder, x_boven) if ibc_paar_teller == 0 else x_boven
                vulling_kleur2 = "#e74c3c" if (x_pos_boven + 1200 > max_lengte) else item["kleur"]
                rect2 = patches.Rectangle((x_pos_boven, max_breedte - 1000 - 20), 1200, 1000, linewidth=1, edgecolor='white', facecolor=vulling_kleur2, alpha=0.8)
                ax.add_patch(rect2)
                ax.text(x_pos_boven + 600, max_breedte - 1000 - 20 + 500, "IBC (Lang)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                x_onder, x_boven = x_pos_onder + 1000, x_pos_boven + 1200
            else:
                vulling_kleur1 = "#e74c3c" if (x_onder + 1200 > max_lengte) else item["kleur"]
                rect1 = patches.Rectangle((x_onder, 20), 1200, 1000, linewidth=1, edgecolor='white', facecolor=vulling_kleur1, alpha=0.8)
                ax.add_patch(rect1)
                ax.text(x_onder + 600, 20 + 500, "IBC (Lang)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                vulling_kleur2 = "#e74c3c" if (x_boven + 1000 > max_lengte) else item["kleur"]
                rect2 = patches.Rectangle((x_boven, max_breedte - 1200 - 20), 1000, 1200, linewidth=1, edgecolor='white', facecolor=vulling_kleur2, alpha=0.8)
                ax.add_patch(rect2)
                ax.text(x_boven + 500, max_breedte - 1200 - 20 + 600, "IBC (Breed)", color="black", weight="bold", ha="center", va="center", fontsize=7)
                x_onder, x_boven = x_onder + 1200, x_boven + 1000
            ibc_paar_teller += 1; idx += 2; continue
    if x_onder <= x_boven:
        vulling_kleur = "#e74c3c" if (x_onder + item["L"] > max_lengte) else item["kleur"]
        rect = patches.Rectangle((x_onder, 20), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=vulling_kleur, alpha=0.8)
        ax.add_patch(rect)
        ax.text(x_onder + (item["L"]/2), 20 + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        x_onder += item["L"]
    else:
        vulling_kleur = "#e74c3c" if (x_boven + item["L"] > max_lengte) else item["kleur"]
        rect = patches.Rectangle((x_boven, max_breedte - item["B"] - 20), item["L"], item["B"], linewidth=1, edgecolor='white', facecolor=vulling_kleur, alpha=0.8)
        ax.add_patch(rect)
        ax.text(x_boven + (item["L"]/2), max_breedte - item["B"] - 20 + (item["B"]/2), item["naam"], color="black", weight="bold", ha="center", va="center", fontsize=7)
        x_boven += item["L"]
    idx += 1

totale_meters = max(x_onder, x_boven); restruimte = max_lengte - totale_meters
st.write("### 3. Plan:")
if pallets_cp3+pallets_cp7_totaal+pallets_ibc+pallets_cp9+pallets_mw > 0 or as_v_cp3+as_v_cp7+as_v_ibc+as_v_cp9+as_v_mw+as_a_cp3+as_a_cp7+as_a_ibc+as_a_cp9+as_a_mw > 0:
    if restruimte >= 0: st.success(f"✅ Past! Nog {restruimte} mm over.")
    else: st.error(f"❌ Past NIET! {abs(restruimte)} mm tekort.")
    st.pyplot(fig)
    st.write(f"**Geladen:** {totale_meters} mm van {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw=CP3 | [X] Groen=CP7 (Lang) | [X] Paars=CP7 (Smal) | [X] Geel=IBC | [X] Oranje=CP9 | [X] Grijs=Maatwerk | [X] ROOD = Past Niet")
else: st.info("Container is leeg. Gebruik de + en - knoppen om te beginnen.")
