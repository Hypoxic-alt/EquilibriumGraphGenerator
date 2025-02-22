import streamlit as st

st.set_page_config(page_title="Reaction Setup", page_icon="⚗️", layout="wide")

st.title("Reaction Setup")
st.markdown(
    "Choose a reaction from the list below and define the phase boundary changes. "
    "Your configuration will be saved automatically and used in the Simulation page (via the sidebar)."
)

# Define a dictionary of example reactions with approximate ΔH values.
reaction_options = {
    # Exothermic reactions:
    "Haber Process (N₂ + 3H₂ ↔ 2NH₃)": {
        "a": 1, "b": 3, "c": 2, "d": 0,
        "delta_H": -92  # kJ/mol
    },
    "Contact Reaction (2SO₂ + O₂ ↔ 2SO₃)": {
        "a": 2, "b": 1, "c": 2, "d": 0,
        "delta_H": -197  # kJ/mol
    },
    "Ethanol Production (C₆H₁₂O₆ ↔ 2C₂H₅OH + 2CO₂)": {
        "a": 1, "b": 0, "c": 2, "d": 2,
        "delta_H": -218  # kJ/mol
    },
    # Endothermic reactions:
    "Calcium Carbonate Decomposition (CaCO₃ ↔ CaO + CO₂)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "delta_H": +178  # kJ/mol
    },
    "Dissolution of Ammonium Chloride (NH₄Cl ↔ NH₄⁺ + Cl⁻)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "delta_H": +15   # kJ/mol
    },
    "Dissolution of Ammonium Nitrate (NH₄NO₃ ↔ NH₄⁺ + NO₃⁻)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "delta_H": +25   # kJ/mol
    }
}

default_reaction_choice = st.session_state.get("reaction_choice", list(reaction_options.keys())[0])
reaction_choice = st.selectbox(
    "Choose a Reaction", list(reaction_options.keys()),
    index=list(reaction_options.keys()).index(default_reaction_choice)
)
selected_reaction = reaction_options[reaction_choice]

st.subheader("Phase Boundary Changes")

# Prepare lists to store boundary change choices and their effects.
phase_changes = []
temp_effects = []
vol_effects = []
A_perturb_list = []
B_perturb_list = []
C_perturb_list = []
D_perturb_list = []

# Loop over the three boundaries.
for i in range(1, 4):
    st.markdown(f"### Boundary {i} Change")
    # Select the change type for Boundary i.
    change_type = st.selectbox(
        f"Select Change Type for Boundary {i}",
        ["Temperature", "Volume/Pressure", "Addition"],
        key=f"phase_change_{i}"
    )
    phase_changes.append(change_type)
    
    # Display sliders immediately below the selectbox.
    if change_type == "Temperature":
        effect = st.slider(
            f"Temperature Effect for Boundary {i}",
            min_value=-1.0, max_value=1.0,
            value=st.session_state.get(f"temp_effect{i}", 0.0),
            step=0.05,
            key=f"temp_effect_{i}"
        )
        temp_effects.append(effect)
        vol_effects.append(0.0)
        A_perturb_list.append(0.0)
        B_perturb_list.append(0.0)
        C_perturb_list.append(0.0)
        D_perturb_list.append(0.0)
    elif change_type == "Volume/Pressure":
        effect = st.slider(
            f"Volume/Pressure Effect for Boundary {i}",
            min_value=-0.5, max_value=0.5,
            value=st.session_state.get(f"vol_effect{i}", 0.0),
            step=0.05,
            key=f"vol_effect_{i}"
        )
        vol_effects.append(effect)
        temp_effects.append(0.0)
        A_perturb_list.append(0.0)
        B_perturb_list.append(0.0)
        C_perturb_list.append(0.0)
        D_perturb_list.append(0.0)
    elif change_type == "Addition":
        st.markdown(f"**Agent Addition for Boundary {i}:**")
        # Only display sliders for species that are present (nonzero coefficient).
        if selected_reaction['a'] != 0:
            A_eff = st.slider(
                f"A Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state.get(f"A_perturb{i}", 0.0),
                step=0.05,
                key=f"A_perturb_{i}"
            )
        else:
            A_eff = 0.0
        if selected_reaction['b'] != 0:
            B_eff = st.slider(
                f"B Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state.get(f"B_perturb{i}", 0.0),
                step=0.05,
                key=f"B_perturb_{i}"
            )
        else:
            B_eff = 0.0
        if selected_reaction['c'] != 0:
            C_eff = st.slider(
                f"C Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state.get(f"C_perturb{i}", 0.0),
                step=0.05,
                key=f"C_perturb_{i}"
            )
        else:
            C_eff = 0.0
        if selected_reaction['d'] != 0:
            D_eff = st.slider(
                f"D Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state.get(f"D_perturb{i}", 0.0),
                step=0.05,
                key=f"D_perturb_{i}"
            )
        else:
            D_eff = 0.0
        A_perturb_list.append(A_eff)
        B_perturb_list.append(B_eff)
        C_perturb_list.append(C_eff)
        D_perturb_list.append(D_eff)
        temp_effects.append(0.0)
        vol_effects.append(0.0)

# Save the configuration to session state.
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
