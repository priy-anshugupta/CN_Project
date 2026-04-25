import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ipaddress
from io import BytesIO

from utils.subnet_calc import calculate_subnet, generate_subnets
from utils.vlsm import calculate_vlsm, summarize_routes
from utils.ip_converter import ip_to_binary, binary_to_ip, ip_to_hex, hex_to_ip, cidr_to_mask, mask_to_cidr
from utils.ipv6 import calculate_ipv6

# Page Config
st.set_page_config(page_title="Subnet Calculator Pro", page_icon="⚡", layout="centered", initial_sidebar_state="expanded")

# Load Custom CSS
try:
    with open("styles/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception:
    st.warning("Custom CSS not found, proceeding with default theme.")

# Initialize Session State
if 'vlsm_hosts' not in st.session_state:
    st.session_state.vlsm_hosts = [50, 20, 10]

def update_vlsm_hosts():
    val = st.session_state.new_host_val
    if val > 0:
        st.session_state.vlsm_hosts.append(val)
        st.session_state.new_host_val = 0

def remove_vlsm_host(index):
    st.session_state.vlsm_hosts.pop(index)

# --- Compact Sidebar Navigation ---
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="brand-icon">⚡</div>
    <div class="brand-title">Routing Engine</div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    [
        "Basic Subnet Calculator",
        "Subnet Divider / VLSM",
        "Supernet / Summarization",
        "IP Converter",
        "Subnet Table Generator",
        "Visual Subnet Map",
        "IPv6 Support",
        "Cheat Sheet",
        "Quiz Mode"
    ],
    label_visibility="collapsed"
)

# --- Compact Main Header ---
st.markdown(f"""
<div class="page-header">
    <h1 class="page-title">{menu}</h1>
    <div class="page-subtitle">Premium routing suite & IP Toolkit</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. Basic Subnet Calculator
# ----------------------------------------------------
if menu == "Basic Subnet Calculator":
    
    col_input, col_space = st.columns([2, 1])
    with col_input:
        ip_input = st.text_input("Network IP or CIDR", value="192.168.1.0/24", help="e.g. 192.168.1.0/24", key="basic_calc")
        
    if ip_input:
        res = calculate_subnet(ip_input)
        if res["Valid"]:
            st.markdown("<div class='pill-success'>✓ Configuration Valid</div><br>", unsafe_allow_html=True)
            
            # Stat grid - Fixed to render in a single markdown block
            st.markdown(f"""
            <div class='stat-grid'>
                <div class='stat-box'><div class='stat-label'>Network</div><div class='stat-val'>{res['Network Address'].split('/')[0]}</div></div>
                <div class='stat-box'><div class='stat-label'>Usable Hosts</div><div class='stat-val'>{res['Usable Hosts']:,}</div></div>
                <div class='stat-box'><div class='stat-label'>Total Hosts</div><div class='stat-val'>{res['Total Hosts']:,}</div></div>
                <div class='stat-box'><div class='stat-label'>IP Class</div><div class='stat-val'>{res['IP Class']}</div></div>
            </div>
            <br>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='card-panel'>
                    <div class='info-row'><span class='info-key'>Broadcast Address</span><span class='info-val'>{res['Broadcast Address']}</span></div>
                    <div class='info-row'><span class='info-key'>Subnet Mask</span><span class='info-val'>{res['Subnet Mask']}</span></div>
                    <div class='info-row'><span class='info-key'>Wildcard Mask</span><span class='info-val'>{res['Wildcard Mask']}</span></div>
                    <div class='info-row'><span class='info-key'>Host Range</span><span class='info-val'>{res['First Usable Host']} - {res['Last Usable Host']}</span></div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class='card-panel'>
                    <div class='info-row'><span class='info-key'>Is Private?</span><span class='info-val'>{'Yes (Internal)' if res['Is Private'] else 'No (Public)'}</span></div>
                    <div class='info-row'><span class='info-key'>Binary Mask</span><span class='info-val mono'>{res['Subnet Mask (Binary)']}</span></div>
                    <div class='info-row'><span class='info-key'>Binary IP</span><span class='info-val mono'>{res['IP Address (Binary)']}</span></div>
                    <div class='info-row'><span class='info-key'>Hex Mask</span><span class='info-val mono'>{res['Subnet Mask (Hex)']}</span></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### Calculation Steps")
            with st.expander("View Step-by-Step Calculation", expanded=True):
                for step in res.get("Steps", []):
                    st.markdown(step)

        else:
            st.markdown(f"<div class='pill-error'>✕ {res['Error']}</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. Variable Length Subnet Mask (VLSM)
# ----------------------------------------------------
elif menu == "Subnet Divider / VLSM":
    
    c1, c2 = st.columns([1, 1])
    with c1:
        base_ip = st.text_input("Base Network CIDR", value="192.168.0.0/24")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.markdown("<div class='section-label'>Add Needed Subnets</div>", unsafe_allow_html=True)
        row1, row2 = st.columns([2, 1])
        with row1:
             st.number_input("Hosts req.", min_value=0, step=1, key="new_host_val", label_visibility="collapsed")
        with row2:
             st.button("Add", on_click=update_vlsm_hosts, type="primary", use_container_width=True)
        
        st.markdown("**Request List:**")
        # Combine list items
        list_html = "<div class='card-panel' style='padding: 8px;'><div style='max-height: 200px; overflow-y: auto;'>"
        for i, val in enumerate(st.session_state.vlsm_hosts):
            list_html += f"<div class='list-item'>Subnet {i+1} <span>{val} hosts</span></div>"
        list_html += "</div></div>"
        st.markdown(list_html, unsafe_allow_html=True)
            
        if st.button("Clear List", use_container_width=True):
            st.session_state.vlsm_hosts = []
            st.rerun()
            
    with col2:
        if st.session_state.vlsm_hosts and base_ip:
            res = calculate_vlsm(base_ip, st.session_state.vlsm_hosts)
            if res["Valid"]:
                df = pd.DataFrame(res["Subnets"])
                st.dataframe(df, use_container_width=True, hide_index=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", data=csv, file_name="vlsm.csv", mime="text/csv", type="primary")
            else:
                st.markdown(f"<div class='pill-error'>✕ {res['Error']}</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 3. Supernet / Route Summarization
# ----------------------------------------------------
elif menu == "Supernet / Summarization":
    
    c1, c2 = st.columns([2, 1])
    with c1:
        nets_input = st.text_area("Networks (one per line)", "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24\n192.168.3.0/24", height=120)
    
    if st.button("Summarize Routes", type="primary"):
        nets = [n for n in nets_input.split('\n') if n.strip()]
        res = summarize_routes(nets)
        if res["Valid"]:
            st.markdown("<div class='pill-success' style='margin-bottom:12px;'>✓ Summary Complete</div>", unsafe_allow_html=True)
            res_html = "<div class='card-panel'>"
            for r in res["Summarized"]:
                res_html += f"<div class='info-row'><span class='info-val mono' style='font-size: 1.1rem; color: #F26B2D;'>{r}</span></div>"
            res_html += "</div>"
            st.markdown(res_html, unsafe_allow_html=True)
        else:
             st.markdown(f"<div class='pill-error'>✕ {res['Error']}</div>", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. IP Converter
# ----------------------------------------------------
elif menu == "IP Converter":
    
    tab1, tab2, tab3 = st.tabs(["IP ↔ Binary", "IP ↔ Hex", "CIDR ↔ Mask"])
    
    with tab1:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            ip1 = st.text_input("Decimal IP", value="192.168.1.1", key="ipbin")
            st.markdown(f"<div class='mono-box'>{ip_to_binary(ip1)}</div>", unsafe_allow_html=True)
        with c2:
            bin1 = st.text_input("Binary IP", value="11000000.10101000.00000001.00000001", key="binip")
            st.markdown(f"<div class='mono-box'>{binary_to_ip(bin1)}</div>", unsafe_allow_html=True)
            
    with tab2:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            ip2 = st.text_input("Decimal IP", value="10.0.0.1", key="iphex")
            st.markdown(f"<div class='mono-box'>{ip_to_hex(ip2)}</div>", unsafe_allow_html=True)
        with c2:
            hex1 = st.text_input("Hexadecimal IP", value="0A.00.00.01", key="hexip")
            st.markdown(f"<div class='mono-box'>{hex_to_ip(hex1)}</div>", unsafe_allow_html=True)
            
    with tab3:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            cidr1 = st.text_input("CIDR Prefix", value="/24", key="cidr")
            st.markdown(f"<div class='mono-box'>{cidr_to_mask(cidr1)}</div>", unsafe_allow_html=True)
        with c2:
            mask1 = st.text_input("Subnet Mask", value="255.255.255.0", key="mask")
            st.markdown(f"<div class='mono-box'>{mask_to_cidr(mask1)}</div>", unsafe_allow_html=True)
            
# ----------------------------------------------------
# 5. Subnet Table Generator
# ----------------------------------------------------
elif menu == "Subnet Table Generator":
    
    c1, c2 = st.columns([1, 1])
    with c1:
        ip_str = st.text_input("Network block", "192.168.1.0/26")
        
    if st.button("Generate Table", type="primary"):
        res = generate_subnets(ip_str)
        if res["Valid"]:
            df = pd.DataFrame(res["Subnets"])
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name="subnet_table.csv", mime="text/csv")
        else:
            st.error(res["Error"])

# ----------------------------------------------------
# 6. Visual Subnet Map
# ----------------------------------------------------
elif menu == "Visual Subnet Map":
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        base_net = st.text_input("Parent Network", value="192.168.1.0/24")
        hosts_str = st.text_area("Hosts (Comma sep.)", "50, 25, 10, 5")
        draw_btn = st.button("Draw Map", type="primary", use_container_width=True)
    
    with col2:
        if draw_btn:
            try:
                reqs = [int(h.strip()) for h in hosts_str.split(',') if h.strip().isdigit()]
                if not reqs:
                    st.warning("Please provide valid integer requirements.")
                else:
                    res = calculate_vlsm(base_net, reqs)
                    if not res["Valid"]:
                        st.markdown(f"<div class='pill-error'>✕ {res['Error']}</div>", unsafe_allow_html=True)
                    else:
                        parent = ipaddress.IPv4Network(base_net, strict=False)
                        parent_start, parent_end = int(parent.network_address), int(parent.broadcast_address)
                        df_list = []
                        current_start = parent_start
                        
                        for sub in res["Subnets"]:
                            s_net = ipaddress.IPv4Network(sub["Network Address"] + sub["CIDR"])
                            start_ip, end_ip = int(s_net.network_address), int(s_net.broadcast_address)
                            df_list.append({"Subnet": f"{sub['CIDR']}", "Size": sub["Allocated Size"], "StartStr": sub["Network Address"], "Color": "Allocated"})
                            current_start = end_ip + 1
                            
                        if current_start <= parent_end:
                             df_list.append({"Subnet": "Unallocated", "Size": (parent_end - current_start) + 1, "StartStr": "-", "Color": "Unallocated"})
                             
                        df_viz = pd.DataFrame(df_list)
                        fig = go.Figure()
                        
                        for i, row in df_viz.iterrows():
                            c = "#1F2937" if row["Color"] == "Allocated" else "#E7E5E4"
                            fig.add_trace(go.Bar(
                                y=["Segment"], x=[row["Size"]], name=row["Subnet"], orientation='h',
                                text=f"{row['Subnet']}<br>{row['StartStr']}", textposition='inside',
                                marker=dict(color=c, line=dict(color="#FCFAF7", width=2))
                            ))
                            
                        fig.update_layout(
                            barmode='stack', template="plotly_white", margin=dict(l=0, r=0, t=10, b=0),
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(showgrid=False, visible=False), yaxis=dict(showticklabels=False), height=150
                        )
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error visualizing: {str(e)}")

# ----------------------------------------------------
# 7. IPv6 Support
# ----------------------------------------------------
elif menu == "IPv6 Support":
    
    c1, c2 = st.columns([2, 1])
    with c1:
        ipv6_input = st.text_input("IPv6 Address & Prefix", "2001:0db8:85a3::8a2e:0370:7334/64")
    
    if ipv6_input:
        res = calculate_ipv6(ipv6_input)
        if res["Valid"]:
            st.markdown(f"""
            <div class='card-panel'>
                <div class='info-row'><span class='info-key'>Expanded</span><span class='info-val mono'>{res['IP Address (Expanded)']}</span></div>
                <div class='info-row'><span class='info-key'>Compressed</span><span class='info-val mono'>{res['IP Address (Compressed)']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='stat-grid'>
                <div class='stat-box'><div class='stat-label'>Prefix</div><div class='stat-val'>/{res['Prefix Length']}</div></div>
                <div class='stat-box'><div class='stat-label'>LAN Subnets</div><div class='stat-val'>{res['Total Subnets (/64)']}</div></div>
                <div class='stat-box'><div class='stat-label'>Site Local</div><div class='stat-val'>{res['Site Local']}</div></div>
                <div class='stat-box'><div class='stat-label'>Private</div><div class='stat-val'>{res['Is Private']}</div></div>
            </div>
            """, unsafe_allow_html=True)
        else:
             st.markdown(f"<div class='pill-error'>✕ {res['Error']}</div>", unsafe_allow_html=True)

elif menu == "Cheat Sheet":
    
    cheat_data = []
    for i in range(8, 33):
        net = ipaddress.IPv4Network(f"0.0.0.0/{i}")
        wild = str(ipaddress.IPv4Address((~int(net.netmask)) & 0xFFFFFFFF))
        cheat_data.append({"CIDR": f"/{i}", "Subnet Mask": str(net.netmask), "Wildcard": wild, "Usable Hosts": net.num_addresses - 2 if net.num_addresses > 2 else net.num_addresses})
    st.dataframe(pd.DataFrame(cheat_data), use_container_width=True, hide_index=True)

elif menu == "Quiz Mode":
    
    import random
    if "quiz_q" not in st.session_state:
        st.session_state.quiz_q = None
    def generate_question():
        prefix = random.randint(16, 29)
        net_str = f"{random.randint(10, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.0/{prefix}"
        network = ipaddress.IPv4Network(net_str, strict=False)
        st.session_state.quiz_q = {"network": f"{network.network_address}/{prefix}", "hosts": network.num_addresses - 2, "mask": str(network.netmask), "broadcast": str(network.broadcast_address)}
        st.session_state.quiz_checked = False
        
    if not st.session_state.quiz_q:
        generate_question()
        
    if st.button("New Question", type="primary"):
        generate_question()
        st.rerun()
        
    q = st.session_state.quiz_q
    st.markdown(f"**Target Network:** `<span class='mono'>{q['network']}</span>`", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: h_ans = st.text_input("Usable Hosts", key="q1")
    with col2: m_ans = st.text_input("Subnet Mask", key="q2")
    with col3: b_ans = st.text_input("Broadcast Address", key="q3")
    
    if st.button("Submit Answers"):
        h_correct = h_ans.strip() == str(q['hosts'])
        m_correct = m_ans.strip() == q['mask']
        b_correct = b_ans.strip() == q['broadcast']
        if h_correct and m_correct and b_correct:
            st.balloons()
            st.markdown("<div class='pill-success'>🎉 Correct!</div>", unsafe_allow_html=True)
        else:
            if not h_correct: st.error(f"Hosts should be {q['hosts']}")
            if not m_correct: st.error(f"Mask should be {q['mask']}")
            if not b_correct: st.error(f"Broadcast should be {q['broadcast']}")
