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

totale_meters = max(x_onder, x_boven)
restruimte = max_lengte - totale_meters

st.write("### 3. Plan:")
if pallets_cp3+pallets_cp7+pallets_cp7_smal+pallets_ibc > 0:
    if restruimte >= 0:
        st.success(f"✅ Past! Nog {restruimte} mm over.")
    else:
        st.error(f"❌ Past NIET! {abs(restruimte)} mm tekort.")
    st.pyplot(fig)
    st.write(f"**Geladen:** {totale_meters} mm van {max_lengte} mm.")
    st.write("💡 **Legenda:** [X] Blauw=CP3 | [X] Groen=CP7 | [X] Paars=CP7 Smal | [X] Geel=IBC")
else:
    st.info("Container is leeg. Gebruik de + en - knoppen om te beginnen.")
