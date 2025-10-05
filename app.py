import streamlit as st
from argopy import DataFetcher
import re
import numpy as np
import pandas as pd
import os
import sys
import importlib
import importlib.util

# Prioritize current directory for module imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

viz_path = os.path.join(CURRENT_DIR, 'visualizations.py')
spec = importlib.util.spec_from_file_location('visualizations', viz_path)
viz = importlib.util.module_from_spec(spec)
assert spec and spec.loader, f"visualizations.py not found at {viz_path}"
spec.loader.exec_module(viz)
from nlp import predict_intent
from floats import indian_floats

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'awaiting_float' not in st.session_state:
    st.session_state['awaiting_float'] = False

if 'float_data' not in st.session_state:
    st.session_state['float_data'] = {}

@st.cache_data
def fetch_float_data(float_id):
    ArgoSet = DataFetcher().float([float_id])
    ds = ArgoSet.load().to_xarray()
    return ds

st.set_page_config(page_title="Argo Chatbot", layout="wide")
st.title("Argo Multi-Float Chatbot 🌊")

st.sidebar.header("Manage Floats 🌏")
# indian_floats

selected_float = st.sidebar.selectbox("Add a float:", indian_floats)
debug_intents = st.sidebar.checkbox("Debug intents", value=False)
if st.sidebar.button("Add float"):
    if selected_float not in st.session_state['float_data']:
        try:
            ds = fetch_float_data(selected_float)
            st.session_state['float_data'][selected_float] = ds
            st.sidebar.success(f"Float {selected_float} added!")
        except:
            st.sidebar.error(f"Failed to load float {selected_float}")


loaded_floats = list(st.session_state['float_data'].keys())
compare_selection = st.sidebar.multiselect("Select floats to view or compare", loaded_floats)

if compare_selection:
    if len(compare_selection) == 1:
        fid = compare_selection[0]
        st.subheader(f"Data for Float {fid}")
        for var in ["TEMP", "PSAL", "PRES"]:
            fig = viz.plot_float_profiles({fid: st.session_state['float_data'][fid]}, variable=var)
            st.plotly_chart(fig, use_container_width=True, key=f"profile-{fid}-{var}")
    elif len(compare_selection) > 1:
        st.subheader(f"Comparison for floats: {', '.join(map(str, compare_selection))}")
        figs = viz.compare_floats_plot(st.session_state['float_data'], compare_selection)
        for var, fig in figs.items():
            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"sidebar-compare-{var}-{'-'.join(map(str, compare_selection))}"
            )


if st.session_state['float_data']:
    st.subheader("Latest Float Positions")
    fig_map = viz.plot_map(st.session_state['float_data'])
    st.plotly_chart(fig_map, use_container_width=True, key="map-latest")


for msg in st.session_state['messages']:
    with st.chat_message(msg['role']):
        st.markdown(msg['text'])


user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state['messages'].append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = "Sorry, I didn't understand. You can ask about float data."

    float_numbers = [int(f) for f in re.findall(r'\b\d{6,8}\b', user_input)]
    intent = predict_intent(user_input)
    # Heuristic fallback: route common map/location phrases to trajectory
    if intent == "unknown":
        tl = user_input.lower()
        if any(k in tl for k in ["map", "where is", "position", "location", "track", "path", "route"]):
            intent = "trajectory"

    if debug_intents:
        st.sidebar.write({
            "intent": intent,
            "numbers": float_numbers,
            "visualizations_module": getattr(viz, "__file__", "unknown"),
        })

   
    if st.session_state['awaiting_float']:
        try:
            float_id = int(user_input)
            if float_id not in st.session_state['float_data']:
                ds = fetch_float_data(float_id)
                st.session_state['float_data'][float_id] = ds
            response = f"Float {float_id} loaded. You can now ask: temperature, salinity, pressure, trajectory, info, or add float."
            st.session_state['awaiting_float'] = False
        except:
            response = "Please enter a valid float number (integer)."
    else:
        if intent == "importance_temperature":
            response = ("🌡️ **Temperature** is critical for understanding the ocean's heat content, "
                        "which influences currents, weather patterns, and climate change.")
        elif intent == "importance_salinity":
            response = ("🧂 **Salinity** affects the density of seawater, driving ocean circulation "
                        "and influencing marine ecosystems.")
        elif intent == "importance_pressure":
            response = ("⏱️ **Pressure** increases with depth and helps determine the density and "
                        "stability of ocean layers, critical for understanding deep-sea processes.")
        elif intent == "importance_argo":
            response = ("🌊 **Argo data** is essential for monitoring global ocean conditions. "
                        "It provides free, high-quality temperature, salinity, and pressure profiles "
                        "from thousands of floats worldwide to support climate and weather research.")
        
        
        elif intent == "compare_floats":
            loaded_floats_local = list(st.session_state['float_data'].keys())
            compare_ids = float_numbers if len(float_numbers) >= 2 else loaded_floats_local
            if compare_ids and len(compare_ids) >= 2:
                # Ensure data is loaded for all compare IDs
                for f in compare_ids:
                    if f not in st.session_state['float_data']:
                        ds = fetch_float_data(f)
                        st.session_state['float_data'][f] = ds
                figs = viz.compare_floats_plot(st.session_state['float_data'], compare_ids)
                response = f"Comparing floats: {', '.join(map(str, compare_ids))}. See graphs below."
                for var, fig in figs.items():
                    st.plotly_chart(fig, use_container_width=True, key=f"compare-{var}-{'-'.join(map(str, compare_ids))}")
            else:
                response = "Please specify at least two float numbers to compare or add multiple floats from the sidebar."

        
        elif intent == "float_info":
            loaded_floats_local = list(st.session_state['float_data'].keys())
            fid = float_numbers[0] if float_numbers else (loaded_floats_local[0] if len(loaded_floats_local) == 1 else None)
            if fid is None:
                response = "Please specify which float you want info for (e.g., 'info float 2903893'), or load exactly one float."
            elif fid in st.session_state['float_data']:
                ds = st.session_state['float_data'][fid]
                lat = float(ds['LATITUDE'].values[-1]) if 'LATITUDE' in ds else np.nan
                lon = float(ds['LONGITUDE'].values[-1]) if 'LONGITUDE' in ds else np.nan
                cycle = int(ds['CYCLE_NUMBER'].values[-1]) if 'CYCLE_NUMBER' in ds else "Unknown"
                date = pd.to_datetime(ds['JULD'].values[-1]).strftime('%Y-%m-%d') if 'JULD' in ds else "Unknown"
                response = f"Float {fid}: Latest cycle {cycle}, at {lat:.2f}°N, {lon:.2f}°E on {date}."
            else:
                response = f"Float {fid} not loaded yet. Please add it first."

      
        elif intent in ["temperature", "salinity", "pressure"]:
            loaded_floats_local = list(st.session_state['float_data'].keys())
            fid = float_numbers[0] if float_numbers else (loaded_floats_local[0] if len(loaded_floats_local) == 1 else None)
            if fid is None:
                response = "Please specify the float number (e.g., 'temperature 2903893') or load exactly one float."
            else:
                # Auto-load if explicit float provided but not yet loaded
                if fid not in st.session_state['float_data']:
                    try:
                        ds = fetch_float_data(fid)
                        st.session_state['float_data'][fid] = ds
                    except Exception:
                        response = f"Failed to load float {fid}. Please try another ID."
                        st.session_state['messages'].append({"role": "assistant", "text": response})
                        with st.chat_message("assistant"):
                            st.markdown(response)
                        raise
                var_map = {"temperature": "TEMP", "salinity": "PSAL", "pressure": "PRES"}
                var = var_map[intent]
                fig = viz.plot_float_profiles({fid: st.session_state['float_data'][fid]}, variable=var)
                st.plotly_chart(fig, use_container_width=True, key=f"profile-{fid}-{var}")
                response = f"{intent.capitalize()} profile for float {fid} displayed."

        elif intent == "trajectory":
            loaded_floats_local = list(st.session_state['float_data'].keys())
            fid = float_numbers[0] if float_numbers else (loaded_floats_local[0] if len(loaded_floats_local) == 1 else None)
            if fid is None:
                response = "Please specify the float number (e.g., 'trajectory 2903893') or load exactly one float."
            else:
                # Auto-load if explicit float provided but not yet loaded
                if fid not in st.session_state['float_data']:
                    try:
                        ds = fetch_float_data(fid)
                        st.session_state['float_data'][fid] = ds
                    except Exception:
                        response = f"Failed to load float {fid}. Please try another ID."
                        st.session_state['messages'].append({"role": "assistant", "text": response})
                        with st.chat_message("assistant"):
                            st.markdown(response)
                        raise
                # Full trajectory
                fig_traj = viz.plot_trajectories({fid: st.session_state['float_data'][fid]})
                st.plotly_chart(fig_traj, use_container_width=True, key=f"traj-{fid}")
                response = f"Full trajectory for float {fid} displayed."

        elif intent == "ask_float":
            response = "Please type the float number you want to add."
            st.session_state['awaiting_float'] = True

        elif intent == "greeting":
            response = "Hello! You can ask about Argo floats or type a float number to get started."

        elif intent == "thanks":
            response = "You're welcome! 🌊"

        elif intent == "help":
            response = (
                "Here’s what I can do:\n"
                "- Ask about variables: 'temperature', 'salinity', 'pressure'\n"
                "- Show a float's 'trajectory' or 'info'\n"
                "- 'compare' two or more floats (e.g., 'compare 2903893 vs 2903892')\n"
                "- 'add float' to load new data\n"
                "- 'list floats' to see what's loaded\n"
                "Tip: Include a float number like 2903893, or load exactly one float to avoid ambiguity."
            )

        elif intent == "list_floats":
            loaded = list(st.session_state['float_data'].keys())
            if loaded:
                response = "Loaded floats: " + ", ".join(map(str, loaded))
            else:
                response = "No floats loaded yet. Use the sidebar or type 'add float' to load one."

        elif intent == "goodbye":
            response = "Goodbye! If you need me again, just send a message. 👋"

        elif intent == "unknown":
            response = (
                "I didn't quite get that. You can say things like:\n"
                "'temperature 2903893', 'trajectory', 'compare 2903893 2903892', 'info float 2903893', or 'help'."
            )

    st.session_state['messages'].append({"role": "assistant", "text": response})
    with st.chat_message("assistant"):
        st.markdown(response)

