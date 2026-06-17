import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Kaneka Flexibel Laadplan", layout="wide")
st.title("📦 Kaneka Flexibel Laadplan Dashboard")
st.write("Bepaal zelf de exacte laadvolgorde door artikelen stap voor stap toe te voegen.")

# 1. Container Keuze
st.subheader("1. Kies het containertype")
container_type = st.selectbox(
    "Containertype", 
    ["45ft HC PW 9.1", "40ft HC PW 9.6", "40ft Open Top"]
)

if container_type == "45ft HC PW 9.1":
    max_lengte = 13550
    max_breedte = 2426
elif container_type == "40ft HC PW 9.6":
    max_lengte = 12030
    max_breedte = 2440
else:
    max_lengte = 12030
    max_breedte = 2345

st.info(f"Geselecteerde container laadruimte: **{max_lengte} mm** lang x **{max_breedte} mm** breed.")

# 2. Dynamische Wachtrij initialiseren in het geheugen van de app
if "laad_wachtrij" not in st.session_state:
    st.session_state.laad_wachtrij = []

# Definieer de vaste productspecificaties
product_info = {
    "CP3 Pallet (1140x1140)": {"lengte": 1140, "breedte": 1140, "kleur": "#3498db", "stapelbaar": False, "kort": "CP3"},
    "CP7 Pallet (1400x1100)": {"lengte": 1400, "breedte": 1100, "kleur": "#2ecc71", "stapelbaar": True, "kort": "CP7"},
    "CP7 Smal (1100x1400)": {"lengte": 1100, "breedte": 1400, "kleur": "#9b59b6", "stapelbaar": True, "kort": "CP7 Smal"},
    "IBC (1000x1200)": {"lengte": 1000, "breedte": 1200, "kleur": "#f1c40f", "stapelbaar": False, "kort": "IBC"}
}

# Formulier om een artikel toe te voegen aan de volgorde
st.subheader("2. Bouw je laadvolgorde op")
col_art, col_aantal = st.columns([2, 1])

with col_art:
    gekozen_artikel = st.selectbox("Kies artikel om NU te laden:", list(product_info.keys()))
with col_aantal:
    gekozen_aantal = st.number_input("Aantal pallets:", min_value=1, value=1, step=1)

col_add, col_clear = st.columns(2)
with col_add:
    if st.button("➕ Voeg toe aan laadplan", use_container_width=True):
        st.session_state.laad_wachtrij.append({
            "type": gekozen_artikel,
            "aantal": gekozen_aantal
        })
with col_clear:
    if st.button("🗑️ Wis hele container (Nieuwe invoer)", use_container_width=True, type="secondary"):
        st.session_state.laad_wachtrij = []
        st.ramps = {} # Reset
        st.rerun()

# Toon de huidige gekozen volgorde aan de lader met individuele verwijderknoppen
if st.session_state.laad_wachtrij:
    st.write("### 📜 Huidige laadvolgorde (van kopschot tot deur):")
    
    # We lopen achteruit door de lijst om veilig items te kunnen verwijderen zonder index-fouten
    for index, item in enumerate(st.session_state.laad_wachtrij):
        col_lijst, col_delete = st.columns([4, 1])
        with col_lijst:
            st.write(f"**{index + 1}.** {item['aantal']}x {item['type']}")
        with col_delete:
            # Unieke knop per rij om te wissen
            if st.button("❌ Verwijder", key=f"del_{index}", use_container_width=True):
                st.session_state.laad_wachtrij.pop(index)
                st.rerun()
else:
    st.info("De container is nog leeg. Voeg hierboven je eerste artikelen toe!")

# 3. Logistieke Logica: Lijst opbouwen exact op volgorde van toevoegen
laad_lijst = []
for item in st.session_state.laad_wachtrij:
    info = product_info[item["type"]]
    
    if info["stapelbaar"]:
        vloerplaatsen = int(math.ceil(item["aantal"] / 2))
    else:
        vloerplaatsen = int(item["aantal"])
        
    overgebleven_pallets = item["aantal"]
    
    for _ in range(vloerplaatsen):
        if info["stapelbaar"]:
            hoogte_label = " (2H)" if overgebleven_pallets >= 2 else " (1H)"
            overgebleven_pallets -= 2
        else:
            hoogte_label = ""
            
        laad_lijst.append({
            "naam": f"{info['kort']}{hoogte_label}",
            "naam_puur": info["kort"],
            "L": info["lengte"],
            "B": info["breedte"],
            "kleur": info["kleur"]
        })

# Breedte-planning: Maak rijen op basis van de ingevoerde volgorde
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

# 4. Teken Layout & Berekening
fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, max_lengte)
ax.set_ylim(0, max_breedte)
ax.set_xlabel("Lengte container (mm)")
ax.set_ylabel("Breedte container (mm)")

container_border = patches.Rectangle((0, 0), max_lengte, max_breedte, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(container_border)

huidige_x = 0
totale_meters = 0

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

if st.session_state.laad_wachtrij:
    if restruimte >= 0:
        st.success(f"Dit past! Je hebt nog {restruimte} mm over in de container.")
    else:
        st.error(f"Dit past NIET! Je komt {abs(restruimte)} mm tekort.")

    st.pyplot(fig)
    st.write(f"**Gebruikte lengte:** {totale_meters} mm van de {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw = CP3 | [X] Groen = CP7 | [X] Paars = CP7 Smal | [X] Geel = IBC")
