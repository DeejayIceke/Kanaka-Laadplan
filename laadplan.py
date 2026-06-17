import streamlit as st
import math

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
    "CP3": {"lengte": 1140, "emoji": "🟦", "stapelbaar": False},
    "CP7": {"lengte": 1400, "emoji": "🟩", "stapelbaar": True},
    "CP7 Smal": {"lengte": 1100, "emoji": "🟪", "stapelbaar": True},
    "IBC": {"lengte": 1000, "emoji": "🟨", "stapelbaar": False}
}

st.write("### 2. Vul aantallen in per artikel:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("<div style='background-color:#3498db; padding:0.5rem; border-radius:0.5rem; color:white; font-weight:bold; text-align:center;'>CP3 (1140x1140)</div>", unsafe_allow_html=True)
    pallets_cp3 = st.number_input("Totaal aantal CP3", min_value=0, value=0, step=1, key=f"cp3_{st.session_state.reset_id}")
    as_v_cp3 = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_cp3_{st.session_state.reset_id}")
    as_a_cp3 = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_cp3_{st.session_state.reset_id}")
    if pallets_cp3 > 0 and "CP3" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP3")

with col2:
    st.markdown("<div style='background-color:#2ecc71; padding:0.5rem; border-radius:0.5rem; color:white; font-weight:bold; text-align:center;'>CP7 (1400x1100)</div>", unsafe_allow_html=True)
    pallets_cp7 = st.number_input("Totaal aantal CP7", min_value=0, value=0, step=1, key=f"cp7_{st.session_state.reset_id}")
    as_v_cp7 = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_cp7_{st.session_state.reset_id}")
    as_a_cp7 = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_cp7_{st.session_state.reset_id}")
    if pallets_cp7 > 0 and "CP7" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7")

with col3:
    st.markdown("<div style='background-color:#9b59b6; padding:0.5rem; border-radius:0.5rem; color:white; font-weight:bold; text-align:center;'>CP7 Smal (1100x1400)</div>", unsafe_allow_html=True)
    pallets_cp7_smal = st.number_input("Totaal aantal Smal", min_value=0, value=0, step=1, key=f"cp7_smal_{st.session_state.reset_id}")
    as_v_cp7_smal = st.number_input("Midden VOORAAN", min_value=0, value=0, step=1, key=f"v_cp7_smal_{st.session_state.reset_id}")
    as_a_cp7_smal = st.number_input("Midden ACHTERAAN", min_value=0, value=0, step=1, key=f"a_cp7_smal_{st.session_state.reset_id}")
    if pallets_cp7_smal > 0 and "CP7 Smal" not in st.session_state.klik_volgorde: st.session_state.klik_volgorde.append("CP7 Smal")

with col4:
    st.markdown("<div style='background-color:#f1c40f; padding:0.5rem; border-radius:0.5rem; color:black; font-weight:bold; text-align:center;'>IBC (1000x1200)</div>", unsafe_allow_html=True)
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
            laad_lijst.append({"naam": f"{art_naam}{h_label}", "naam_puur": art_naam, "L": info["lengte"], "emoji": info["emoji"], "force_midden": force_midden})

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

rijen = []
tijdelijke_rij = []
idx = 0
ibc_paar_teller = 0

while idx < len(laad_lijst):
    item = laad_lijst[idx]
    if item["force_midden"] or item["naam_puur"] == "CP7 Smal":
        if tijdelijke_rij: rijen.append(tijdelijke_rij); tijdelijke_rij = []
        rijen.append([item])
        idx += 1
        continue
    if max_breedte == 2350 and item["naam_puur"] == "IBC":
        heeft_partner = (idx + 1 < len(laad_lijst) and laad_lijst[idx+1]["naam_puur"] == "IBC" and not laad_lijst[idx+1]["force_midden"])
        if heeft_partner:
            item2 = laad_lijst[idx+1].copy()
            if ibc_paar_teller % 2 == 0:
                item["naam"], item2["naam"] = "IBC (Breed)", "IBC (Lang)"
            else:
                item["naam"], item2["naam"] = "IBC (Lang)", "IBC (Breed)"
            rijen.append([item, item2])
            ibc_paar_teller += 1
            idx += 2
            continue
    tijdelijke_rij.append(item)
    if len(tijdelijke_rij) == 2: rijen.append(tijdelijke_rij); tijdelijke_rij = []
    idx += 1
if tijdelijke_rij: rijen.append(tijdelijke_rij)

totale_meters = 0
st.write("### 3. Plan (Kopschot links ➔ Deur rechts):")

# Visuele Tekst-Plattegrond opbouwen
plattegrond_boven = ""
plattegrond_onder = ""

for r in rijen:
    if len(r) == 1:
        # Pallet staat alleen in het midden (Aslast of CP7 Smal)
        rij_lengte = r[0]["L"]
        plattegrond_boven += "⬜⬜"
        plattegrond_onder += f"{r[0]['emoji']}{r[0]['naam']}"
    else:
        # Twee pallets naast elkaar
        rij_lengte = max(r[0]["L"], r[1]["L"])
        plattegrond_boven += f"{r[1]['emoji']}{r[1]['naam']}"
        plattegrond_onder += f"{r[0]['emoji']}{r[0]['naam']}"
    
    plattegrond_boven += " | "
    plattegrond_onder += " | "
    totale_meters += rij_lengte

restruimte = max_lengte - totale_meters

if pallets_cp3+pallets_cp7+pallets_cp7_smal+pallets_ibc > 0:
    if restruimte >= 0: st.success(f"✅ Past! Nog {restruimte} mm over.")
    else: st.error(f"❌ Past NIET! {abs(restruimte)} mm tekort.")
    
    # Toon de plattegrond strak onder elkaar
    st.code(f"LINKERKANT CONTAINER (BOVEN): {plattegrond_boven}\nRECHTERKANT CONTAINER (ONDER): {plattegrond_onder}")
    st.write(f"**Geladen:** {totale_meters} mm van {max_lengte} mm.")
    st.write("💡 **Legenda:** 🟦=CP3 | 🟩=CP7 | 🟪=CP7 Smal | 🟨=IBC | ⬜=Leeg")
else:
    st.info("Container is leeg. Gebruik de + en - knoppen om te beginnen.")
