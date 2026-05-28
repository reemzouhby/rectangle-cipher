"""
RECTANGLE Lightweight Block Cipher — Streamlit Interactive App
"""

import streamlit as st
import time

# ─────────────────────────────────────────────
# RECTANGLE CIPHER ENGINE (embedded)
# ─────────────────────────────────────────────

SBOX = [0x6,0x5,0xC,0xA,0x1,0xE,0x7,0x9,0xB,0x0,0x3,0xD,0x8,0xF,0x4,0x2]
SBOX_INV = [0]*16
for _i,_v in enumerate(SBOX): SBOX_INV[_v] = _i

RC = [0x01,0x02,0x04,0x09,0x12,0x05,0x0B,0x16,
      0x0C,0x19,0x13,0x07,0x0F,0x1F,0x1E,0x1C,
      0x18,0x11,0x03,0x06,0x0D,0x1B,0x17,0x0E,0x1D]

def _rot16(x,n):
    n%=16
    return x&0xFFFF if n==0 else ((x<<n)|(x>>(16-n)))&0xFFFF

def _rot32(x,n):
    n%=32
    return x&0xFFFFFFFF if n==0 else ((x<<n)|(x>>(32-n)))&0xFFFFFFFF

def _apply_sbox_cols(rows, num_cols):
    rows=list(rows)
    for j in range(num_cols):
        col=sum(((rows[b]>>j)&1)<<b for b in range(4))
        s=SBOX[col]
        for b in range(4):
            if (s>>b)&1: rows[b]|=(1<<j)
            else:        rows[b]&=~(1<<j)
    return rows

def int_to_state(block):
    # Paper convention: Row0 = MSB (bits 48..63), Row3 = LSB (bits 0..15)
    return [(block >> (16*(3-i))) & 0xFFFF for i in range(4)]

def state_to_int(state):
    return sum(state[i] << (16*(3-i)) for i in range(4))

def sub_column(state):
    ns=[0,0,0,0]
    for j in range(16):
        col=sum(((state[b]>>j)&1)<<b for b in range(4))
        s=SBOX[col]
        for b in range(4):
            if (s>>b)&1: ns[b]|=(1<<j)
    return ns

def sub_column_inv(state):
    ns=[0,0,0,0]
    for j in range(16):
        col=sum(((state[b]>>j)&1)<<b for b in range(4))
        s=SBOX_INV[col]
        for b in range(4):
            if (s>>b)&1: ns[b]|=(1<<j)
    return ns

def shift_row(state):
    return [_rot16(state[0],0),_rot16(state[1],1),_rot16(state[2],12),_rot16(state[3],13)]

def shift_row_inv(state):
    return [_rot16(state[0],0),_rot16(state[1],15),_rot16(state[2],4),_rot16(state[3],3)]

def add_round_key(state,sk):
    return [state[i]^sk[i] for i in range(4)]

def key_schedule_80(key):
    rows=[(key>>(16*i))&0xFFFF for i in range(5)]
    sks=[]
    for r in range(25):
        sks.append(rows[:4])
        rows=_apply_sbox_cols(rows,4)
        R0,R1,R2,R3,R4=rows
        rows=[_rot16(R0,8)^R1,R2,R3,_rot16(R3,12)^R4,R0]
        rows[0]^=RC[r]
    sks.append(rows[:4])
    return sks

def key_schedule_128(key):
    rows=[(key>>(32*i))&0xFFFFFFFF for i in range(4)]
    sks=[]
    for r in range(25):
        sks.append([rows[i]&0xFFFF for i in range(4)])
        rows=_apply_sbox_cols(rows,8)
        R0,R1,R2,R3=rows
        rows=[_rot32(R0,8)^R1,R2,_rot32(R2,16)^R3,R0]
        rows[0]^=RC[r]
    sks.append([rows[i]&0xFFFF for i in range(4)])
    return sks

def encrypt(pt,key,key_bits=80):
    sks=key_schedule_80(key) if key_bits==80 else key_schedule_128(key)
    state=int_to_state(pt)
    for r in range(25):
        state=add_round_key(state,sks[r])
        state=sub_column(state)
        state=shift_row(state)
    state=add_round_key(state,sks[25])
    return state_to_int(state)

def decrypt(ct,key,key_bits=80):
    sks=key_schedule_80(key) if key_bits==80 else key_schedule_128(key)
    state=int_to_state(ct)
    state=add_round_key(state,sks[25])
    for r in range(24,-1,-1):
        state=shift_row_inv(state)
        state=sub_column_inv(state)
        state=add_round_key(state,sks[r])
    return state_to_int(state)

def bits_diff(a,b):
    return bin(a^b).count('1')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="RECTANGLE Cipher",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0a0e1a;
    --surface:   #111827;
    --card:      #1a2235;
    --border:    #2a3550;
    --accent:    #00e5ff;
    --accent2:   #7c3aed;
    --success:   #10b981;
    --danger:    #ef4444;
    --warning:   #f59e0b;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --mono:      'Space Mono', monospace;
    --sans:      'DM Sans', sans-serif;
}

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: var(--sans);
}

[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Headings ── */
h1,h2,h3 { font-family: var(--mono) !important; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-accent { border-left: 3px solid var(--accent); }
.card-success { border-left: 3px solid var(--success); }
.card-danger  { border-left: 3px solid var(--danger);  }
.card-purple  { border-left: 3px solid var(--accent2); }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(0,229,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero h1 {
    font-size: 2.4rem;
    background: linear-gradient(90deg, #00e5ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem;
    letter-spacing: -1px;
}
.hero p { color: var(--muted); font-size: 1rem; margin: 0; }

/* ── Badge chips ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin: 2px;
}
.badge-cyan   { background: rgba(0,229,255,0.12); color: var(--accent); border: 1px solid rgba(0,229,255,0.3); }
.badge-purple { background: rgba(124,58,237,0.15); color: #a78bfa; border: 1px solid rgba(124,58,237,0.3); }
.badge-green  { background: rgba(16,185,129,0.12); color: var(--success); border: 1px solid rgba(16,185,129,0.3); }
.badge-red    { background: rgba(239,68,68,0.12); color: var(--danger); border: 1px solid rgba(239,68,68,0.3); }

/* ── Hex output box ── */
.hex-box {
    background: #050810;
    border: 1px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-family: var(--mono);
    font-size: 1.3rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-align: center;
    box-shadow: 0 0 20px rgba(0,229,255,0.08);
    word-break: break-all;
}
.hex-box-green {
    border-color: var(--success);
    color: var(--success);
    box-shadow: 0 0 20px rgba(16,185,129,0.08);
}
.hex-box-red {
    border-color: var(--danger);
    color: var(--danger);
    box-shadow: 0 0 20px rgba(239,68,68,0.08);
}

/* ── Step pill ── */
.step {
    display: inline-flex; align-items: center; justify-content: center;
    width: 28px; height: 28px;
    background: var(--accent2); border-radius: 50%;
    font-family: var(--mono); font-size: 0.8rem; font-weight: 700;
    color: #fff; margin-right: 0.5rem; flex-shrink: 0;
}

/* ── Info rows in sidebar ── */
.info-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--muted); }
.info-val   { font-family: var(--mono); color: var(--accent); font-size: 0.8rem; }

/* ── Streamlit overrides ── */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,255,0.15) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #00e5ff22, #7c3aed33) !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.05em !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00e5ff44, #7c3aed55) !important;
    box-shadow: 0 0 16px rgba(0,229,255,0.25) !important;
}
div[data-baseweb="radio"] { gap: 0.5rem; }
div[data-baseweb="radio"] label { font-family: var(--sans) !important; }

/* ── Tab styling ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
    border-radius: 7px !important;
    color: var(--muted) !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0; }

/* ── Metric ── */
[data-testid="stMetricValue"] {
    font-family: var(--mono) !important;
    color: var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — How to Use + Examples
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <span style="font-size:2.5rem;">🔐</span>
        <h2 style="font-family:'Space Mono',monospace; font-size:1.1rem;
                   margin:0.3rem 0 0; color:#00e5ff; letter-spacing:0.1em;">
            RECTANGLE
        </h2>
        <p style="color:#64748b; font-size:0.75rem; margin:0;">
            Lightweight Block Cipher
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Algorithm specs ──
    st.markdown("#### 📐 Algorithm Specs")
    specs = [
        ("Block size",   "64 bits"),
        ("Key options",  "80 or 128 bits"),
        ("Rounds",       "25"),
        ("Structure",    "SP-network"),
        ("S-box",        "4-bit × 4-bit"),
        ("P-layer",      "3 rotations"),
        ("Standard",     "ISO/IEC (basis)"),
    ]
    rows_html = "".join(
        f'<div class="info-row"><span class="info-label">{k}</span><span class="info-val">{v}</span></div>'
        for k, v in specs
    )
    st.markdown(f'<div class="card">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── How to use ──
    st.markdown("#### 📖 How to Use")

    steps = [
        ("Choose mode", "Select **Encrypt** or **Decrypt** on the main page."),
        ("Enter block",
         "Type your **64-bit plaintext** (or ciphertext) as 16 hex characters, "
         "e.g. `DEADBEEFCAFEBABE`."),
        ("Pick key size", "Choose **80-bit** (20 hex chars) or **128-bit** (32 hex chars)."),
        ("Enter key", "Type your secret key in hex, e.g. `0123456789ABCDEF0123`."),
        ("Run", "Click **Encrypt / Decrypt** and read the result."),
        ("Avalanche tab", "Use the **Avalanche Analysis** tab to explore how 1 bit change affects the output."),
    ]
    for idx, (title, desc) in enumerate(steps, 1):
        st.markdown(
            f'<div style="display:flex;align-items:flex-start;gap:0.6rem;margin-bottom:0.9rem;">'
            f'<span class="step">{idx}</span>'
            f'<div><strong style="color:#e2e8f0;font-size:0.88rem;">{title}</strong>'
            f'<br><span style="color:#94a3b8;font-size:0.8rem;">{desc}</span></div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Test vectors from paper ──
    st.markdown("#### 🧪 Official Test Vectors")
    st.markdown('<p style="color:#64748b;font-size:0.78rem;">From Table 10 of the RECTANGLE paper. '
                'Copy these into the main page to verify correctness.</p>', unsafe_allow_html=True)

    examples = [
        {
            "label": "REC-80 · All Zeros",
            "key_bits": 80,
            "pt": "0000000000000000",
            "key": "00000000000000000000",
            "ct": "2D96E354E8B10874",
        },
        {
            "label": "REC-80 · All Ones",
            "key_bits": 80,
            "pt": "FFFFFFFFFFFFFFFF",
            "key": "FFFFFFFFFFFFFFFFFFFF",
            "ct": "9945AA34AE3D0112",
        },
        {
            "label": "REC-128 · All Zeros",
            "key_bits": 128,
            "pt": "0000000000000000",
            "key": "00000000000000000000000000000000",
            "ct": "AEE6361344A499EE",
        },
        {
            "label": "REC-128 · All Ones",
            "key_bits": 128,
            "pt": "FFFFFFFFFFFFFFFF",
            "key": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF",
            "ct": "E83EEFEE4A157A46",
        },
    ]

    for ex in examples:
        with st.expander(ex["label"]):
            st.markdown(
                f'<div style="font-family:Space Mono,monospace;font-size:0.72rem;line-height:1.8;">'
                f'<span style="color:#64748b;">Key bits:</span> '
                f'<span style="color:#00e5ff;">{ex["key_bits"]}</span><br>'
                f'<span style="color:#64748b;">Plaintext:</span><br>'
                f'<span style="color:#e2e8f0;">{ex["pt"]}</span><br>'
                f'<span style="color:#64748b;">Key:</span><br>'
                f'<span style="color:#e2e8f0;">{ex["key"]}</span><br>'
                f'<span style="color:#64748b;">Ciphertext:</span><br>'
                f'<span style="color:#10b981;">{ex["ct"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )







# ─────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────

# Hero banner
st.markdown("""
<div class="hero">
    <h1>RECTANGLE CIPHER</h1>
    <p>Lightweight block cipher for IoT & embedded systems</p>
    <div style="margin-top:1rem;">
        <span class="badge badge-cyan">64-bit Block</span>
        <span class="badge badge-purple">SP-Network</span>
        <span class="badge badge-green">25 Rounds</span>
        <span class="badge badge-cyan">Bit-slice Design</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──
tab_enc, tab_aval, tab_compare = st.tabs(["🔒  Encrypt / Decrypt", "🌊  Avalanche Analysis", "🔑  Key Size Comparison"])


# ═══════════════════════════════════════════
# TAB 1 — ENCRYPT / DECRYPT
# ═══════════════════════════════════════════

with tab_enc:
    col_left, col_right = st.columns([1.1, 1], gap="large")

    with col_left:
        st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Configuration")

        # Mode
        st.markdown("**Operation Mode**")
        mode = st.radio("mode", ["🔒 Encrypt", "🔓 Decrypt"],
                        horizontal=True, label_visibility="collapsed")
        is_encrypt = "Encrypt" in mode

        st.markdown("---")

        # Input block
        block_label = "Plaintext (hex)" if is_encrypt else "Ciphertext (hex)"
        block_hint  = "16 hex characters — e.g. DEADBEEFCAFEBABE"
        block_input = st.text_input(
            block_label,
            value="0000000000000000",
            max_chars=16,
            help=block_hint,
            placeholder="0000000000000000"
        ).strip().upper()

        # Key size
        st.markdown("**Key Size**")
        key_bits = st.radio("keybits", [80, 128], horizontal=True,
                            label_visibility="collapsed", format_func=lambda x: f"{x}-bit")

        # Key input
        key_chars = 20 if key_bits == 80 else 32
        key_input = st.text_input(
            f"Key (hex, {key_chars} chars)",
            value="0" * key_chars,
            max_chars=key_chars,
            placeholder="0" * key_chars
        ).strip().upper()

        st.markdown("</div>", unsafe_allow_html=True)

        # Run button
        run = st.button(
            f"{'🔒 ENCRYPT' if is_encrypt else '🔓 DECRYPT'}",
            use_container_width=True
        )

    with col_right:
        st.markdown('<div class="card card-purple">', unsafe_allow_html=True)
        st.markdown("### 📤 Result")

        # Validate inputs
        errors = []
        if len(block_input) != 16:
            errors.append(f"Block must be exactly **16** hex chars (got {len(block_input)})")
        else:
            try: int(block_input, 16)
            except ValueError: errors.append("Block contains invalid hex characters")

        if len(key_input) != key_chars:
            errors.append(f"Key must be exactly **{key_chars}** hex chars (got {len(key_input)})")
        else:
            try: int(key_input, 16)
            except ValueError: errors.append("Key contains invalid hex characters")

        if errors:
            for e in errors:
                st.error(e)
        elif run:
            with st.spinner("Running 25 rounds..."):
                t0 = time.perf_counter()
                pt_val  = int(block_input, 16)
                key_val = int(key_input, 16)
                result  = encrypt(pt_val, key_val, key_bits) if is_encrypt \
                          else decrypt(pt_val, key_val, key_bits)
                elapsed = (time.perf_counter() - t0) * 1_000_000  # µs

            result_hex = f"{result:016X}"
            label_out  = "Ciphertext" if is_encrypt else "Plaintext"

            st.markdown(f"**{label_out}:**")
            cls = "hex-box-green" if is_encrypt else "hex-box"
            st.markdown(f'<div class="hex-box {cls}">{result_hex}</div>',
                        unsafe_allow_html=True)

            st.markdown("---")

            # Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Rounds", "25")
            m2.metric("Key", f"{key_bits}-bit")
            m3.metric("Time", f"{elapsed:.1f} µs")

            st.markdown("---")

            # Summary table
            rows_summary = [
                ("Mode",      "Encrypt 🔒" if is_encrypt else "Decrypt 🔓"),
                ("Input",     block_input),
                ("Key",       key_input),
                ("Output",    result_hex),
            ]
            tbl = "".join(
                f'<div class="info-row">'
                f'<span class="info-label">{k}</span>'
                f'<span class="info-val" style="font-size:0.72rem;max-width:200px;'
                f'overflow:hidden;text-overflow:ellipsis;">{v}</span></div>'
                for k, v in rows_summary
            )
            st.markdown(f'<div style="margin-top:0.5rem;">{tbl}</div>',
                        unsafe_allow_html=True)

            # Verify round-trip
            if is_encrypt:
                rt = decrypt(result, key_val, key_bits)
                ok = (rt == pt_val)
                icon = "✅" if ok else "❌"
                st.markdown(
                    f'<div style="margin-top:1rem;padding:0.6rem 1rem;border-radius:8px;'
                    f'background:{"rgba(16,185,129,0.1)" if ok else "rgba(239,68,68,0.1)"};'
                    f'border:1px solid {"#10b981" if ok else "#ef4444"};'
                    f'font-size:0.82rem;color:{"#10b981" if ok else "#ef4444"};">'
                    f'{icon} Round-trip verified: decrypt(encrypt(PT)) = PT</div>',
                    unsafe_allow_html=True
                )
        elif not run:
            st.markdown(
                '<div style="height:200px;display:flex;align-items:center;justify-content:center;'
                'color:#334155;font-family:Space Mono,monospace;font-size:0.9rem;">'
                '⬅ Configure inputs and click Run</div>',
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 2 — AVALANCHE ANALYSIS
# ═══════════════════════════════════════════

with tab_aval:
    st.markdown("""
    <div class="card card-accent">
    <p style="color:#94a3b8;font-size:0.88rem;margin:0;">
    The <strong style="color:#00e5ff;">Avalanche Effect</strong> is a key property of good ciphers:
    flipping a <em>single bit</em> in the plaintext or key should change approximately
    <strong>50%</strong> of the ciphertext bits.  RECTANGLE achieves this fully after just 4 rounds.
    </p>
    </div>
    """, unsafe_allow_html=True)

    av_col1, av_col2 = st.columns(2, gap="large")

    with av_col1:
        st.markdown("**Base Plaintext (16 hex chars)**")
        av_pt  = st.text_input("Base PT", value="0123456789ABCDEF",
                               max_chars=16, label_visibility="collapsed").strip().upper()
        st.markdown("**Key (80-bit, 20 hex chars)**")
        av_key = st.text_input("Aval Key", value="0123456789ABCDEF0123",
                               max_chars=20, label_visibility="collapsed").strip().upper()

        av_mode = st.radio("Flip in:", ["Plaintext", "Key"], horizontal=True)
        flip_bit = st.slider("Bit to flip (0 = LSB)", 0, 63, 0)
        run_aval = st.button("⚡ Analyse Avalanche", use_container_width=True)

    with av_col2:
        valid_aval = len(av_pt)==16 and len(av_key)==20
        if run_aval and valid_aval:
            pt_base  = int(av_pt, 16)
            key_base = int(av_key, 16)

            if av_mode == "Plaintext":
                pt_flipped  = pt_base ^ (1 << flip_bit)
                key_flipped = key_base
                ct1 = encrypt(pt_base,  key_base,  80)
                ct2 = encrypt(pt_flipped, key_flipped, 80)
                lbl1, lbl2 = f"PT = {pt_base:016X}", f"PT' = {pt_flipped:016X}"
            else:
                pt_flipped  = pt_base
                key_flipped = key_base ^ (1 << flip_bit)
                ct1 = encrypt(pt_base, key_base,   80)
                ct2 = encrypt(pt_base, key_flipped, 80)
                lbl1, lbl2 = f"K = {key_base:016X}", f"K' = {key_flipped:016X}"

            diff_bits = bits_diff(ct1, ct2)
            pct = diff_bits / 64 * 100
            diff_hex = ct1 ^ ct2

            # Visual bit difference display
            ct1_bin = f"{ct1:064b}"
            ct2_bin = f"{ct2:064b}"

            st.markdown(f"**{diff_bits}/64 bits changed ({pct:.1f}%)**")

            # Coloured bar
            bar_html = '<div style="display:flex;gap:1px;flex-wrap:wrap;margin:0.5rem 0;">'
            for i in range(64):
                b1 = ct1_bin[i]
                b2 = ct2_bin[i]
                color = "#ef4444" if b1 != b2 else "#1e3a5f"
                bar_html += f'<div title="bit {63-i}" style="width:8px;height:20px;background:{color};border-radius:2px;"></div>'
            bar_html += "</div>"
            bar_html += '<p style="color:#64748b;font-size:0.75rem;">🟥 changed bits &nbsp; 🟦 unchanged bits</p>'
            st.markdown(bar_html, unsafe_allow_html=True)

            st.markdown("**Ciphertext 1:**")
            st.markdown(f'<div class="hex-box">{ct1:016X}</div>', unsafe_allow_html=True)
            st.markdown("**Ciphertext 2:**")
            st.markdown(f'<div class="hex-box hex-box-red">{ct2:016X}</div>', unsafe_allow_html=True)
            st.markdown("**XOR Difference:**")
            st.markdown(f'<div class="hex-box" style="color:#f59e0b;border-color:#f59e0b;">{diff_hex:016X}</div>',
                        unsafe_allow_html=True)

            quality = "🟢 Excellent" if pct >= 40 else ("🟡 Moderate" if pct >= 25 else "🔴 Weak")
            st.markdown(
                f'<div style="margin-top:1rem;padding:0.8rem 1rem;border-radius:8px;'
                f'background:rgba(16,185,129,0.08);border:1px solid #10b981;'
                f'font-size:0.85rem;color:#10b981;">'
                f'{quality} avalanche &nbsp;|&nbsp; {diff_bits}/64 bits differ</div>',
                unsafe_allow_html=True
            )

        elif run_aval:
            st.error("Check: plaintext must be 16 hex chars, key must be 20 hex chars.")
        else:
            st.markdown(
                '<div style="height:220px;display:flex;align-items:center;justify-content:center;'
                'color:#334155;font-family:Space Mono,monospace;font-size:0.85rem;">'
                '⬅ Set inputs and click Analyse</div>',
                unsafe_allow_html=True
            )


# ═══════════════════════════════════════════
# TAB 3 — KEY SIZE COMPARISON
# ═══════════════════════════════════════════

with tab_compare:
    st.markdown("""
    <div class="card card-purple">
    <p style="color:#94a3b8;font-size:0.88rem;margin:0;">
    Encrypt the same plaintext with both <strong style="color:#a78bfa;">80-bit</strong>
    and <strong style="color:#00e5ff;">128-bit</strong> keys side by side.
    Both use exactly <strong>25 rounds</strong> — only the key schedule differs.
    </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1], gap="medium")

    with c1:
        st.markdown("**Plaintext (16 hex chars)**")
        cmp_pt = st.text_input("CMP PT", value="DEADBEEFCAFEBABE",
                               max_chars=16, label_visibility="collapsed").strip().upper()

    with c2:
        st.markdown("**80-bit Key (20 hex chars)**")
        cmp_k80 = st.text_input("CMP K80", value="0123456789ABCDEF0123",
                                max_chars=20, label_visibility="collapsed").strip().upper()

    with c3:
        st.markdown("**128-bit Key (32 hex chars)**")
        cmp_k128 = st.text_input("CMP K128",
                                 value="0123456789ABCDEF0123456789ABCDEF",
                                 max_chars=32, label_visibility="collapsed").strip().upper()

    run_cmp = st.button("⚡ Compare Both Key Sizes", use_container_width=True)

    if run_cmp:
        errs = []
        if len(cmp_pt)  != 16: errs.append("Plaintext must be 16 hex chars")
        if len(cmp_k80) != 20: errs.append("80-bit key must be 20 hex chars")
        if len(cmp_k128)!= 32: errs.append("128-bit key must be 32 hex chars")
        for e in errs: st.error(e)

        if not errs:
            pt_val = int(cmp_pt, 16)

            t0 = time.perf_counter()
            ct80 = encrypt(pt_val, int(cmp_k80, 16), 80)
            d80  = (time.perf_counter() - t0) * 1e6

            t0 = time.perf_counter()
            ct128 = encrypt(pt_val, int(cmp_k128, 16), 128)
            d128  = (time.perf_counter() - t0) * 1e6

            diff = bits_diff(ct80, ct128)

            left, right = st.columns(2, gap="large")
            with left:
                st.markdown('<div class="card" style="border-left:3px solid #a78bfa;">', unsafe_allow_html=True)
                st.markdown("#### 🔑 80-bit Key Result")
                st.markdown(f'<div class="hex-box" style="color:#a78bfa;border-color:#a78bfa;">{ct80:016X}</div>',
                            unsafe_allow_html=True)
                st.metric("Time", f"{d80:.1f} µs")
                st.metric("Key length", "80 bits")
                st.metric("Security level", "~80-bit")
                st.markdown("</div>", unsafe_allow_html=True)

            with right:
                st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
                st.markdown("#### 🔑 128-bit Key Result")
                st.markdown(f'<div class="hex-box">{ct128:016X}</div>', unsafe_allow_html=True)
                st.metric("Time", f"{d128:.1f} µs")
                st.metric("Key length", "128 bits")
                st.metric("Security level", "~128-bit")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown(
                f'<div class="card" style="text-align:center;">'
                f'<p style="color:#64748b;font-size:0.85rem;margin:0 0 0.5rem;">Ciphertext difference</p>'
                f'<p style="font-family:Space Mono,monospace;font-size:1.8rem;color:#f59e0b;margin:0;">'
                f'{diff}/64 bits differ</p>'
                f'<p style="color:#64748b;font-size:0.8rem;margin:0.3rem 0 0;">'
                f'Different keys always produce completely different outputs</p>'
                f'</div>',
                unsafe_allow_html=True
            )