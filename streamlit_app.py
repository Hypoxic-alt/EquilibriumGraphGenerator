import streamlit as st

st.set_page_config(page_title="Reaction Setup", page_icon="⚗️", layout="wide")

# -------------------------------
# Initialize session state defaults
# -------------------------------
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

if "reaction_choice" not in st.session_state:
    st.session_state["reaction_choice"] = list(reaction_options.keys())[0]

for i in range(1, 4):
    if f"phase_change_{i}" not in st.session_state:
        st.session_state[f"phase_change_{i}"] = "Temperature"  # default change type
    if f"temp_effect{i}" not in st.session_state:
        st.session_state[f"temp_effect{i}"] = 0.0
    if f"vol_effect{i}" not in st.session_state:
        st.session_state[f"vol_effect{i}"] = 0.0
    if f"A_perturb{i}" not in st.session_state:
        st.session_state[f"A_perturb{i}"] = 0.0
    if f"B_perturb{i}" not in st.session_state:
        st.session_state[f"B_perturb{i}"] = 0.0
    if f"C_perturb{i}" not in st.session_state:
        st.session_state[f"C_perturb{i}"] = 0.0
    if f"D_perturb{i}" not in st.session_state:
        st.session_state[f"D_perturb{i}"] = 0.0

# -------------------------------
# Layout: Title and Description
# -------------------------------
st.title("Reaction Setup")
st.markdown(
    "Choose a reaction from the list below and define the phase boundary changes. "
    "Your configuration will be saved and used on the Simulation page (via the sidebar)."
)

# -------------------------------
# Reaction Selection: Uses widget keys to persist state
# -------------------------------
reaction_choice = st.selectbox(
    "Choose a Reaction",
    list(reaction_options.keys()),
    index=list(reaction_options.keys()).index(st.session_state["reaction_choice"]),
    key="reaction_choice"
)
selected_reaction = reaction_options[reaction_choice]

# -------------------------------
# Phase Boundary Changes Setup
# -------------------------------
st.subheader("Phase Boundary Changes")

phase_changes = []
temp_effects = []
vol_effects = []
A_perturb_list = []
B_perturb_list = []
C_perturb_list = []
D_perturb_list = []

for i in range(1, 4):
    st.markdown(f"### Boundary {i} Change")
    change_types = ["Temperature", "Volume/Pressure", "Addition"]
    change_type = st.selectbox(
        f"Select Change Type for Boundary {i}",
        change_types,
        index=change_types.index(st.session_state[f"phase_change_{i}"]),
        key=f"phase_change_{i}"
    )
    phase_changes.append(change_type)
    
    if change_type == "Temperature":
        effect = st.slider(
            f"Temperature Effect for Boundary {i}",
            min_value=-1.0, max_value=1.0,
            value=st.session_state[f"temp_effect{i}"],
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
            value=st.session_state[f"vol_effect{i}"],
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
        if selected_reaction['a'] != 0:
            A_eff = st.slider(
                f"A Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state[f"A_perturb{i}"],
                step=0.05,
                key=f"A_perturb_{i}"
            )
        else:
            A_eff = 0.0
        if selected_reaction['b'] != 0:
            B_eff = st.slider(
                f"B Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state[f"B_perturb{i}"],
                step=0.05,
                key=f"B_perturb_{i}"
            )
        else:
            B_eff = 0.0
        if selected_reaction['c'] != 0:
            C_eff = st.slider(
                f"C Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state[f"C_perturb{i}"],
                step=0.05,
                key=f"C_perturb_{i}"
            )
        else:
            C_eff = 0.0
        if selected_reaction['d'] != 0:
            D_eff = st.slider(
                f"D Perturb for Boundary {i}",
                min_value=-0.5, max_value=0.5,
                value=st.session_state[f"D_perturb{i}"],
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

# -------------------------------
# Save Configuration Button (using a separate key for configuration)
# -------------------------------
if st.button("Save Configuration"):
    st.session_state["config"] = {
        "reaction_choice": reaction_choice,
        "selected_reaction": selected_reaction,
        "phase_changes": phase_changes,
        "temp_effects": temp_effects,
        "vol_effects": vol_effects,
        "A_perturb_list": A_perturb_list,
        "B_perturb_list": B_perturb_list,
        "C_perturb_list": C_perturb_list,
        "D_perturb_list": D_perturb_list,
    }
    st.success("Configuration saved!")

st.info("Your configuration will persist between sessions. Now navigate to the Simulation page via the sidebar.")
