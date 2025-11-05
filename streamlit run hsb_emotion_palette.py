# hsb_emotion_palette.py
# Streamlit app: "HSB (9×9×9) Emotion Palette"
# - Hue: 9 bins (0..320 step 40)
# - Saturation: 9 steps (0..1 step 1/8)
# - Brightness: 9 steps (0..1 step 1/8)
# - Clickable 9×9 grid for S×B at a chosen Hue
# - Exports full 9×9×9 palette as CSV with HEX and emotion labels

import streamlit as st
import colorsys
import pandas as pd
from io import StringIO

st.set_page_config(page_title="HSB Emotion Palette (9×9×9)", layout="wide")

# -----------------------------
# Constants & helpers
# -----------------------------
H_DEGS = [0, 40, 80, 120, 160, 200, 240, 280, 320]  # 9 bins
H_NAMES = ["Red", "Orange", "Yellow", "Green", "Sky", "Blue", "Navy", "Purple", "Pink"]

STEP9 = [i/8 for i in range(9)]  # 0.0 .. 1.0 in 9 steps

def hsv_to_hex(h_deg: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb((h_deg % 360)/360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return "#%02x%02x%02x" % (int(round(r*255)), int(round(g*255)), int(round(b*255)))

def hsv_to_rgb255(h_deg: float, s: float, v: float):
    r, g, b = colorsys.hsv_to_rgb((h_deg % 360)/360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return int(round(r*255)), int(round(g*255)), int(round(b*255))

def emotion_label(h_name: str, s_idx: int, b_idx: int) -> str:
    if s_idx <= 2: s_word = "Soft"
    elif s_idx <= 5: s_word = "Balanced"
    else: s_word = "Vivid"

    if b_idx <= 2: b_word = "Deep"
    elif b_idx <= 5: b_word = "Clear"
    else: b_word = "Bright"

    return f"{b_word} {s_word} {h_name}"

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.title("HSB Emotion Palette (9×9×9)")
st.sidebar.markdown("Select **Hue** family, then pick **Saturation × Brightness** from the grid.")

st.sidebar.subheader("Hue (9)")
h_cols = st.sidebar.columns(9, gap="small")
selected_h_idx = st.session_state.get("selected_h_idx", 0)

for i, c in enumerate(h_cols):
    swatch = hsv_to_hex(H_DEGS[i], 0.9, 0.9)
    if c.button(H_NAMES[i], key=f"hue_btn_{i}", use_container_width=True):
        selected_h_idx = i
        st.session_state["selected_h_idx"] = i
    c.markdown(f"<div style='height:10px;background:{swatch};border-radius:6px;margin-top:4px;'></div>", unsafe_allow_html=True)

st.sidebar.subheader("Brightness (B)")
b_idx = st.sidebar.slider("B (0..8)", min_value=0, max_value=8, value=st.session_state.get("b_idx", 6), step=1)
st.session_state["b_idx"] = b_idx

st.sidebar.subheader("Saturation (S) quick pick")
s_idx_quick = st.sidebar.slider("S (0..8)", min_value=0, max_value=8, value=st.session_state.get("s_idx_quick", 5), step=1)
st.session_state["s_idx_quick"] = s_idx_quick

# -----------------------------
# Main layout
# -----------------------------
st.markdown(f"## 🎨 {H_NAMES[selected_h_idx]} palette — H={H_DEGS[selected_h_idx]}°")
st.caption("Click a cell in the 9×9 grid (Saturation × Brightness).")

left, right = st.columns([2, 1], gap="large")

with left:
    for row_b_idx in reversed(range(9)):
        cols = st.columns(9, gap="small")
        for s_idx in range(9):
            h = H_DEGS[selected_h_idx]
            s = STEP9[s_idx]
            v = STEP9[row_b_idx]
            hex_color = hsv_to_hex(h, s, v)

            key = f"cell_{selected_h_idx}_{s_idx}_{row_b_idx}"
            clicked = cols[s_idx].button(" ", key=key, use_container_width=True)
            cols[s_idx].markdown(
                f"<div style='height:28px;background:{hex_color};border-radius:6px;border:1px solid rgba(0,0,0,0.2);margin-top:-6px;'></div>",
                unsafe_allow_html=True
            )
            if clicked:
                st.session_state["pick"] = {"h_idx": selected_h_idx, "s_idx": s_idx, "b_idx": row_b_idx}

with left:
    st.markdown("#### Quick pick at current Brightness")
    q_cols = st.columns(2)
    s = STEP9[s_idx_quick]
    v = STEP9[b_idx]
    hex_quick = hsv_to_hex(H_DEGS[selected_h_idx], s, v)
    q_cols[0].markdown(f"<div style='height:48px;background:{hex_quick};border-radius:8px;border:1px solid rgba(0,0,0,0.2);'></div>", unsafe_allow_html=True)
    q_cols[1].write(f"H={H_DEGS[selected_h_idx]}°, S={s_idx_quick}/8, B={b_idx}/8")
    if q_cols[1].button("Use Quick Pick", key="use_quick"):
        st.session_state["pick"] = {"h_idx": selected_h_idx, "s_idx": s_idx_quick, "b_idx": b_idx}

with right:
    st.markdown("### 🧾 Selection")
    pick = st.session_state.get("pick", {"h_idx": selected_h_idx, "s_idx": s_idx_quick, "b_idx": b_idx})
    h_idx = pick["h_idx"]; s_idx = pick["s_idx"]; b_idx_sel = pick["b_idx"]
    H_deg = H_DEGS[h_idx]
    S_val = STEP9[s_idx]
    B_val = STEP9[b_idx_sel]

    hex_sel = hsv_to_hex(H_deg, S_val, B_val)
    r, g, b = hsv_to_rgb255(H_deg, S_val, B_val)
    label = emotion_label(H_NAMES[h_idx], s_idx, b_idx_sel)

    st.markdown(f"<div style='height:100px;background:{hex_sel};border-radius:10px;border:1px solid rgba(0,0,0,0.25);'></div>", unsafe_allow_html=True)
    st.write(f"**Emotion**: {label}")
    st.code(f"HSV: ({H_deg}°, {s_idx}/8, {b_idx_sel}/8)\nRGB: ({r}, {g}, {b})\nHEX: {hex_sel}", language="text")

    st.markdown("---")
    st.subheader("Export full 9×9×9 palette")
    rows = []
    for hi, h in enumerate(H_DEGS):
        for si, s in enumerate(STEP9):
            for bi, v in enumerate(STEP9):
                hexv = hsv_to_hex(h, s, v)
                r255, g255, b255 = hsv_to_rgb255(h, s, v)
                rows.append({
                    "H_idx": hi, "S_idx": si, "B_idx": bi,
                    "H_deg": h, "S": round(s, 4), "B": round(v, 4),
                    "R": r255, "G": g255, "B_rgb": b255,
                    "HEX": hexv,
                    "Emotion": emotion_label(H_NAMES[hi], si, bi)
                })
    df = pd.DataFrame(rows)
    csv_buf = StringIO()
    df.to_csv(csv_buf, index=False, encoding="utf-8")
    st.download_button("Download CSV (729 colors)", data=csv_buf.getvalue(),
                       file_name="hsb_emotion_palette_9x9x9.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("Export selected color")
    one_df = pd.DataFrame([{
        "H_idx": h_idx, "S_idx": s_idx, "B_idx": b_idx_sel,
        "H_deg": H_deg, "S": round(S_val, 4), "B": round(B_val, 4),
        "R": r, "G": g, "B_rgb": b, "HEX": hex_sel, "Emotion": label
    }])
    csv_one = StringIO()
    one_df.to_csv(csv_one, index=False, encoding="utf-8")
    st.download_button("Download selected color CSV", data=csv_one.getvalue(),
                       file_name="selected_color.csv", mime="text/csv")

st.caption("Tip: In this palette, S≈intensity, B≈openness/energy. Labels are illustrative and can be customized to your taxonomy.")
