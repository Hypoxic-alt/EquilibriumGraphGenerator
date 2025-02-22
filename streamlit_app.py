import streamlit as st

st.set_page_config(page_title="Reaction Setup", page_icon="⚗️", layout="wide")

st.title("Reaction Setup")
st.markdown(
    "Choose a reaction from the list below and define the phase boundary changes. "
    "Your configuration will be saved and used on the Simulation page."
)

# Define a dictionary of example reactions with approximate ΔH values.
reaction_options = {
    "Haber Process (N₂ + 3H₂ ↔ 2NH₃)": {"a": 1, "b": 3, "c": 2, "d": 0, "delta_H": -92},
    "Contact Reaction (2SO₂ + O₂ ↔ 2SO₃)": {"a": 2, "b": 1, "c": 2, "d": 0, "delta_H": -197},
    "Ethanol Production (C₆H₁₂O₆ ↔ 2C₂H₅OH + 2CO₂)": {"a": 1, "b": 0, "c": 2, "d": 2, "delta_H": -218},
    "Calcium Carbonate Decomposition (CaCO₃ ↔ CaO + CO₂)": {"a": 1, "b": 0, "c": 1, "d": 1, "delta_H": +178},
    "Dissolution of Ammonium Chloride (NH₄Cl ↔ NH₄⁺ + Cl⁻)": {"a": 1, "b": 0, "c": 1, "d": 1, "delta_H": +15},
    "Dissolution of Ammonium Nitrate (NH₄NO₃ ↔ NH₄⁺ + NO₃⁻)": {"a": 1, "b": 0, "c": 1, "d": 1, "delta_H": +25},
}

# -------------------------------
# Initialize session state defaults for widget keys
# -------------------------------
if "reaction_choice" not in st.session_state:
    st.session_state["reaction_choice"] = list(reaction_options.keys())[0]

for i in range(1, 4):
    if f"phase_change_{i}" not in st.session_state:
        st.session_state[f"phase_change_{i}"] = "Temperature"
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
# Reaction Selection Widget (state maintained automatically)
# -------------------------------
reaction_choice = st.selectbox(
    "Choose a Reaction",
    list(reaction_options.keys()),
    index=list(reaction_options.keys()).index(st.session_state["reaction_choice"]),
    key="reaction_choice"
)
selected_reaction = reaction_options[reaction_choice]

st.subheader("Phase Boundary Changes")

# Prepare lists to store boundary settings.
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
# Save Configuration Button
# -------------------------------
if st.button("Save Configuration"):
    config = {
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
    st.session_state["config"] = config
    st.success("Configuration saved!")

# -------------------------------
# Update Sliders Button
# -------------------------------
if st.button("Update Sliders to Saved Config"):
    if "config" in st.session_state:
        config = st.session_state["config"]
        # Delete widget keys so that we can update them.
        keys_to_reset = ["reaction_choice"]
        for i in range(1, 4):
            keys_to_reset.extend([
                f"phase_change_{i}", f"temp_effect{i}", f"vol_effect{i}",
                f"A_perturb{i}", f"B_perturb{i}", f"C_perturb{i}", f"D_perturb{i}"
            ])
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        # Now update the keys with saved configuration.
        st.session_state["reaction_choice"] = config["reaction_choice"]
        for i in range(1, 4):
            st.session_state[f"phase_change_{i}"] = config["phase_changes"][i-1]
            st.session_state[f"temp_effect{i}"] = config["temp_effects"][i-1]
            st.session_state[f"vol_effect{i}"] = config["vol_effects"][i-1]
            st.session_state[f"A_perturb{i}"] = config["A_perturb_list"][i-1]
            st.session_state[f"B_perturb{i}"] = config["B_perturb_list"][i-1]
            st.session_state[f"C_perturb{i}"] = config["C_perturb_list"][i-1]
            st.session_state[f"D_perturb{i}"] = config["D_perturb_list"][i-1]
        st.success("Sliders updated to saved configuration!")
        st.rerun()  # Using st.rerun() as requested.
    else:
        st.error("No configuration saved to load.")

st.info("Configuration saved in session state. You can now switch to the Simulation page.")
