# app.py
# Streamlit: "What's your color today?"
# Step 1) 9 pure hues (S=1, B=1) 중 하나 선택
# Step 2) "Wanna tell me some more?" → Saturation / Brightness 슬라이더로 미세조정
# (필요시 Reset 버튼으로 처음 단계로 돌아가기)

import streamlit as st
import colorsys

st.set_page_config(page_title="What's your color today?", layout="centered")

# -----------------------------
# Constants
# -----------------------------
H_DEGS = [0, 40, 80, 120, 160, 200, 240, 280, 320]  # 9 hues
H_NAMES = ["Red", "Orange", "Yellow", "Green", "Sky", "Blue", "Navy", "Purple", "Pink"]

def hsv_to_hex(h_deg: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb((h_deg % 360)/360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return "#%02x%02x%02x" % (int(round(r*255)), int(round(g*255)), int(round(b*255)))

def hsv_to_rgb255(h_deg: float, s: float, v: float):
    r, g, b = colorsys.hsv_to_rgb((h_deg % 360)/360.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return int(round(r*255)), int(round(g*255)), int(round(b*255))

def emotion_label(h_name: str, s: float, b: float) -> str:
    # 간단 라벨: S=강도, B=개방감/에너지
    if s < 0.33: s_word = "Soft"
    elif s < 0.75: s_word = "Balanced"
    else: s_word = "Vivid"

    if b < 0.33: b_word = "Deep"
    elif b < 0.75: b_word = "Clear"
    else: b_word = "Bright"

    return f"{b_word} {s_word} {h_name}"

# -----------------------------
# State init
# -----------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "pick_hue"  # or "refine"
if "h_idx" not in st.session_state:
    st.session_state.h_idx = 0
if "s" not in st.session_state:
    st.session_state.s = 1.0
if "b" not in st.session_state:
    st.session_state.b = 1.0

# -----------------------------
# Header
# -----------------------------
st.markdown("<h1 style='text-align:center;'>What's your color today?</h1>", unsafe_allow_html=True)

# -----------------------------
# Stage 1: pick hue (pure color)
# -----------------------------
if st.session_state.stage == "pick_hue":
    st.caption("순도 1의 9개 색 중에서 골라줘. (S=1, B=1)")

    cols = st.columns(3, gap="large")
    for i, h in enumerate(H_DEGS):
        hex_color = hsv_to_hex(h, 1.0, 1.0)
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="height:110px;border-radius:16px;border:1px solid rgba(0,0,0,0.15);
                background:{hex_color};"></div>
                """, unsafe_allow_html=True
            )
            if st.button(H_NAMES[i], key=f"hue_btn_{i}", use_container_width=True):
                st.session_state.h_idx = i
                st.session_state.s = 1.0
                st.session_state.b = 1.0
                st.session_state.stage = "refine"
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.caption("Tip: 한 번 클릭하면 다음 단계에서 채도·밝기를 더 말해줄 수 있어.")

# -----------------------------
# Stage 2: refine S/B
# -----------------------------
elif st.session_state.stage == "refine":
    h_idx = st.session_state.h_idx
    h_deg = H_DEGS[h_idx]
    s = st.session_state.s
    b = st.session_state.b

    st.markdown(
        f"<h3 style='text-align:center;'>Wanna tell me some more?</h3>",
        unsafe_allow_html=True
    )
    st.caption("채도(Saturation)와 밝기(Brightness)를 움직여서 네 오늘의 색을 더 정확히 말해줘.")

    # Preview
    left, right = st.columns([1,1], gap="large")
    with left:
        hex_now = hsv_to_hex(h_deg, s, b)
        r, g, bl = hsv_to_rgb255(h_deg, s, b)
        st.markdown(
            f"""
            <div style="height:150px;border-radius:18px;border:1px solid rgba(0,0,0,0.2);
            background:{hex_now};"></div>
            """,
            unsafe_allow_html=True
        )
        st.write(f"**{emotion_label(H_NAMES[h_idx], s, b)}**")
        st.code(f"H: {h_deg}°  S: {s:.3f}  B: {b:.3f}\nRGB: ({r}, {g}, {bl})  HEX: {hex_now}", language="text")

    with right:
        s_new = st.slider("Saturation (S)", 0.0, 1.0, s, step=0.01)
        b_new = st.slider("Brightness (B)", 0.0, 1.0, b, step=0.01)
        st.session_state.s = s_new
        st.session_state.b = b_new

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("✅ Confirm", use_container_width=True):
            st.toast("Saved your color today.", icon="✅")
        if c2.button("↩️ Reset", use_container_width=True):
            st.session_state.stage = "pick_hue"
            st.session_state.s = 1.0
            st.session_state.b = 1.0

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.caption("원하면 Confirm으로 확정하거나, Reset으로 처음부터 다시 고를 수 있어.")

# Footer
st.markdown("<hr style='opacity:.2;'>", unsafe_allow_html=True)
st.caption("Design: 9 pure hues → refine with Saturation & Brightness. (HSV/HSB)")
