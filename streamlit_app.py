import streamlit as st

st.set_page_config(page_title="Reaction Setup", page_icon="⚗️", layout="wide")

st.title("Reaction Setup")
st.markdown(
    "Choose a reaction from the list below and define the phase boundary changes. "
    "Your configuration will be saved automatically and used in the Simulation page (via the sidebar)."
)

# Define a dictionary of example reactions.
reaction_options = {
    # Exothermic reactions:
    "Haber Process (N₂ + 3H₂ ↔ 2NH₃)": {
        "a": 1, "b": 3, "c": 2, "d": 0,
        "default_reaction_type": "Exothermic"
    },
    "Contact Reaction (2SO₂ + O₂ ↔ 2SO₃)": {
        "a": 2, "b": 1, "c": 2, "d": 0,
        "default_reaction_type": "Exothermic"
    },
    "Ethanol Production (C₆H₁₂O₆ ↔ 2C₂H₅OH + 2CO₂)": {
        "a": 1, "b": 0, "c": 2, "d": 2,
        "default_reaction_type": "Exothermic"
    },
    # Endothermic reactions:
    "Calcium Carbonate Decomposition (CaCO₃ ↔ CaO + CO₂)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "default_reaction_type": "Endothermic"
    },
    "Dissolution of Ammonium Chloride (NH₄Cl ↔ NH₄⁺ + Cl⁻)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "default_reaction_type": "Endothermic"
    },
    "Dissolution of Ammonium Nitrate (NH₄NO₃ ↔ NH₄⁺ + NO₃⁻)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "default_reaction_type": "Endothermic"
    }
}

default_reaction_choice = st.session_state.get("reaction_choice", list(reaction_options.keys())[0])
reaction_choice = st.selectbox(
    "Choose a Reaction", list(reaction_options.keys()),
    index=list(reaction_options.keys()).index(default_reaction_choice)
)
selected_reaction = reaction_options[reaction_choice]

st.subheader("Phase Boundary Changes")
st.markdown("For each boundary (after Phase 1), choose the type of change and specify its effect. "
            "For example, you can choose a temperature change and set it as an increase (positive value) or decrease (negative value).")

# For each boundary, let the user select the type and then its effect.
# We have three boundaries.

phase_change1 = st.selectbox("Boundary 1 Change", ["Temperature", "Volume/Pressure", "Addition"], key="phase1")
phase_change2 = st.selectbox("Boundary 2 Change", ["Temperature", "Volume/Pressure", "Addition"], key="phase2")
phase_change3 = st.selectbox("Boundary 3 Change", ["Temperature", "Volume/Pressure", "Addition"], key="phase3")
phase_changes = [phase_change1, phase_change2, phase_change3]

# Prepare dictionaries to hold the effect values for each boundary.
temp_effects = [0.0, 0.0, 0.0]
vol_effects = [0.0, 0.0, 0.0]
A_perturb_list = [0.0, 0.0, 0.0]
B_perturb_list = [0.0, 0.0, 0.0]
C_perturb_list = [0.0, 0.0, 0.0]
D_perturb_list = [0.0, 0.0, 0.0]

for i, change_type in enumerate(phase_changes, start=1):
    st.markdown(f"**Boundary {i} ({change_type})**")
    if change_type == "Temperature":
        temp_effects[i-1] = st.slider(
            f"Temperature Effect for Boundary {i}",
            min_value=-1.0, max_value=1.0,
            value=st.session_state.get(f"temp_effect{i}", 0.0),
            step=0.05,
            key=f"temp_effect{i}"
        )
    elif change_type == "Volume/Pressure":
        vol_effects[i-1] = st.slider(
            f"Volume/Pressure Effect for Boundary {i}",
            min_value=-0.5, max_value=0.5,
            value=st.session_state.get(f"vol_effect{i}", 0.0),
            step=0.05,
            key=f"vol_effect{i}"
        )
    elif change_type == "Addition":
        A_perturb_list[i-1] = st.slider(
            f"A Perturb for Boundary {i}",
            min_value=-0.5, max_value=0.5,
            value=st.session_state.get(f"A_perturb{i}", 0.0),
            step=0.05,
            key=f"A_perturb{i}"
        )
        B_perturb_list[i-1] = st.slider(
            f"B Perturb for Boundary {i}",
            min_value=-0.5, max_value=0.5,
            value=st.session_state.get(f"B_perturb{i}", 0.0),
            step=0.05,
            key=f"B_perturb{i}"
        )
        C_perturb_list[i-1] = st.slider(
            f"C Perturb for Boundary {i}",
            min_value=-0.5, max_value=0.5,
            value=st.session_state.get(f"C_perturb{i}", 0.0),
            step=0.05,
            key=f"C_perturb{i}"
        )
        D_perturb_list[i-1] = st.slider(
            f"D Perturb for Boundary {i}",
            min_value=-0.5, max_value=0.5,
            value=st.session_state.get(f"D_perturb{i}", 0.0),
            step=0.05,
            key=f"D_perturb{i}"
        )

# Save all parameters into session state.
st.session_state['reaction_choice'] = reaction_choice
st.session_state['selected_reaction'] = selected_reaction
st.session_state['phase_changes'] = phase_changes
st.session_state['temp_effects'] = temp_effects
st.session_state['vol_effects'] = vol_effects
st.session_state['A_perturb_list'] = A_perturb_list
st.session_state['B_perturb_list'] = B_perturb_list
st.session_state['C_perturb_list'] = C_perturb_list
st.session_state['D_perturb_list'] = D_perturb_list

st.info("Configuration saved! Now navigate to the Simulation page via the sidebar.")
