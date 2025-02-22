import streamlit as st

# Set page configuration (optional)
st.set_page_config(page_title="Reaction Setup", page_icon="⚗️", layout="wide")

st.title("Reaction Setup")
st.markdown("Choose a reaction and define the phase boundary changes.")

# Define a dictionary of example reactions.
reaction_options = {
    "Haber Process (N₂ + 3H₂ ↔ 2NH₃)": {
        "a": 1, "b": 3, "c": 2, "d": 0,
        "default_reaction_type": "Exothermic"
    },
    "Esterification Reaction (Acid + Alcohol ↔ Ester + Water)": {
        "a": 1, "b": 1, "c": 1, "d": 1,
        "default_reaction_type": "Endothermic"
    },
    "Acid-Base Reaction (Acid + Base ↔ Salt + Water)": {
        "a": 1, "b": 1, "c": 1, "d": 1,
        "default_reaction_type": "Exothermic"
    }
}

# Reaction selection
reaction_choice = st.selectbox("Choose a Reaction", list(reaction_options.keys()))
selected_reaction = reaction_options[reaction_choice]

st.subheader("Phase Boundary Changes")
st.markdown("For each phase boundary (after Phase 1), select the type of change and configure its parameters.")

# For each boundary, let the user select one change type.
phase_change1 = st.selectbox("Boundary 1 Change", ["Temperature", "Volume/Pressure", "Addition"], key="phase1")
phase_change2 = st.selectbox("Boundary 2 Change", ["Temperature", "Volume/Pressure", "Addition"], key="phase2")
phase_change3 = st.selectbox("Boundary 3 Change", ["Temperature", "Volume/Pressure", "Addition"], key="phase3")
phase_changes = [phase_change1, phase_change2, phase_change3]

# If any boundary uses temperature, show a slider for its effect.
if "Temperature" in phase_changes:
    temp_effect = st.slider("Temperature Effect (for Temperature changes)", min_value=-1.0, max_value=1.0, value=0.0, step=0.05)
else:
    temp_effect = 0.0

# If any boundary uses volume/pressure, show its slider.
if "Volume/Pressure" in phase_changes:
    vol_effect = st.slider("Volume/Pressure Effect", min_value=-0.5, max_value=0.5, value=0.0, step=0.05)
else:
    vol_effect = 0.0

# If any boundary uses addition, display perturbation parameters.
if "Addition" in phase_changes:
    st.subheader("Agent Addition Parameters")
    A_perturb = st.slider("A Perturb", min_value=-0.5, max_value=0.5, value=0.0, step=0.05)
    B_perturb = st.slider("B Perturb", min_value=-0.5, max_value=0.5, value=0.0, step=0.05)
    C_perturb = st.slider("C Perturb", min_value=-0.5, max_value=0.5, value=0.0, step=0.05)
    D_perturb = st.slider("D Perturb", min_value=-0.5, max_value=0.5, value=0.0, step=0.05)
else:
    A_perturb = B_perturb = C_perturb = D_perturb = 0.0

# When ready, save the parameters in session state and move to the simulation page.
if st.button("Go to Simulation"):
    st.session_state['reaction_choice'] = reaction_choice
    st.session_state['selected_reaction'] = selected_reaction
    st.session_state['phase_changes'] = phase_changes
    st.session_state['temp_effect'] = temp_effect
    st.session_state['vol_effect'] = vol_effect
    st.session_state['A_perturb'] = A_perturb
    st.session_state['B_perturb'] = B_perturb
    st.session_state['C_perturb'] = C_perturb
    st.session_state['D_perturb'] = D_perturb
    # Use st.query_params to set the query parameters.
    st.query_params(page="Simulation")
    st.rerun()
