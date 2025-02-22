import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# =========================
# Helper Functions
# =========================

def generic_reaction(concentrations, t, k1, k2, a, b, c, d):
    A, B, C, D = concentrations
    r_forward = k1 * (A ** a) * (B ** b)
    r_reverse = k2 * (C ** c) * (D ** d)
    r = r_forward - r_reverse
    return [-a * r, -b * r, c * r, d * r]

def draw_connection(t_value, prev_value, next_value, color):
    # Draw a vertical line at t_value connecting the previous and next phase values.
    plt.vlines(t_value, prev_value, next_value, colors=color, linestyles='solid', linewidth=2)

# =========================
# Reaction Setup Page
# =========================

def reaction_setup():
    st.title("Reaction Setup")
    st.markdown(
        "Choose a reaction from the list below and define the phase boundary changes. "
        "Your configuration will be saved and used on the Simulation page (via the sidebar)."
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

    # -------------------------------
    # Initialize session state defaults
    # -------------------------------
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
    # Reaction Selection (widget state persists automatically)
    # -------------------------------
    reaction_choice = st.selectbox(
        "Choose a Reaction",
        list(reaction_options.keys()),
        index=list(reaction_options.keys()).index(st.session_state["reaction_choice"]),
        key="reaction_choice"
    )
    selected_reaction = reaction_options[reaction_choice]

    st.subheader("Phase Boundary Changes")

    # Prepare lists to store phase boundary settings.
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
        # Save the configuration under custom keys so as not to conflict with widget keys.
        st.session_state["reaction_choice"] = reaction_choice
        st.session_state["selected_reaction"] = selected_reaction
        st.session_state["phase_changes"] = phase_changes
        st.session_state["temp_effects"] = temp_effects
        st.session_state["vol_effects"] = vol_effects
        st.session_state["A_perturb_list"] = A_perturb_list
        st.session_state["B_perturb_list"] = B_perturb_list
        st.session_state["C_perturb_list"] = C_perturb_list
        st.session_state["D_perturb_list"] = D_perturb_list
        st.success("Configuration saved!")

    st.info("Configuration saved in session state. You can now go to the Simulation page via the sidebar.")

# =========================
# Simulation Page
# =========================

def simulate_reaction(a, b, c, d, delta_H,
                      temp_effects, vol_effects,
                      A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
                      phase_changes, show_title,
                      # Phase display toggles:
                      A_phase1, A_phase2, A_phase3, A_phase4,
                      B_phase1, B_phase2, B_phase3, B_phase4,
                      C_phase1, C_phase2, C_phase3, C_phase4,
                      D_phase1, D_phase2, D_phase3, D_phase4):
    # Base rate constants.
    k1_base = 0.02
    k2_base = 0.01
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]
    
    # There are 4 phases: Base and three subsequent phases.
    phases = ["Base"] + phase_changes
    sols = []
    t_phases = []
    
    for i, phase in enumerate(phases):
        t_phase = np.linspace(i * 200, (i + 1) * 200, 1000)
        sol = odeint(generic_reaction, init_state, t_phase, args=(k1_current, k2_current, a, b, c, d))
        sols.append(sol)
        t_phases.append(t_phase)
        if i < len(phases) - 1:
            init_state = sol[-1].copy()
            current_boundary = phase_changes[i]
            if current_boundary == "Temperature":
                effect = temp_effects[i]
                # Adjust rate constants based on ΔH.
                if delta_H < 0:
                    k2_current = k2_base * (1 + effect)
                else:
                    k1_current = k1_base * (1 + effect)
            elif current_boundary == "Volume/Pressure":
                effect = vol_effects[i]
                init_state = init_state / (1 + effect)
            elif current_boundary == "Addition":
                init_state[0] *= (1 + A_perturb_list[i])
                init_state[1] *= (1 + B_perturb_list[i])
                init_state[2] *= (1 + C_perturb_list[i])
                init_state[3] *= (1 + D_perturb_list[i])
    
    fig = plt.figure(figsize=(10, 6))
    phases_labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    
    # Plot each species for each phase if enabled.
    for i, sol in enumerate(sols):
        if a != 0 and ((i == 0 and A_phase1) or (i == 1 and A_phase2) or (i == 2 and A_phase3) or (i == 3 and A_phase4)):
            plt.plot(t_phases[i], sol[:, 0], label=f'A {phases_labels[i]}', color='blue', linewidth=2)
        if b != 0 and ((i == 0 and B_phase1) or (i == 1 and B_phase2) or (i == 2 and B_phase3) or (i == 3 and B_phase4)):
            plt.plot(t_phases[i], sol[:, 1], label=f'B {phases_labels[i]}', color='red', linewidth=2)
        if c != 0 and ((i == 0 and C_phase1) or (i == 1 and C_phase2) or (i == 2 and C_phase3) or (i == 3 and C_phase4)):
            plt.plot(t_phases[i], sol[:, 2], label=f'C {phases_labels[i]}', color='green', linewidth=2)
        if d != 0 and ((i == 0 and D_phase1) or (i == 1 and D_phase2) or (i == 2 and D_phase3) or (i == 3 and D_phase4)):
            plt.plot(t_phases[i], sol[:, 3], label=f'D {phases_labels[i]}', color='purple', linewidth=2)
    
    # Draw vertical connecting lines at phase boundaries.
    for i in range(len(phases)-1):
        t_boundary = t_phases[i][-1]
        if a != 0 and ((i == 0 and A_phase1 and A_phase2) or (i == 1 and A_phase2 and A_phase3) or (i == 2 and A_phase3 and A_phase4)):
            draw_connection(t_boundary, sols[i][-1, 0], sols[i+1][0, 0], 'blue')
        if b != 0 and ((i == 0 and B_phase1 and B_phase2) or (i == 1 and B_phase2 and B_phase3) or (i == 2 and B_phase3 and B_phase4)):
            draw_connection(t_boundary, sols[i][-1, 1], sols[i+1][0, 1], 'red')
        if c != 0 and ((i == 0 and C_phase1 and C_phase2) or (i == 1 and C_phase2 and C_phase3) or (i == 2 and C_phase3 and C_phase4)):
            draw_connection(t_boundary, sols[i][-1, 2], sols[i+1][0, 2], 'green')
        if d != 0 and ((i == 0 and D_phase1 and D_phase2) or (i == 1 and D_phase2 and D_phase3) or (i == 2 and D_phase3 and D_phase4)):
            draw_connection(t_boundary, sols[i][-1, 3], sols[i+1][0, 3], 'purple')
    
    plt.xlabel("Time")
    plt.ylabel("Concentration")
    if show_title:
        title_str = "{}  |  ΔH = {} kJ/mol".format(st.session_state.get('reaction_choice', 'Unknown Reaction'), delta_H)
        plt.title(title_str)
    plt.tight_layout()
    return fig

def simulation_page():
    st.title("Simulation")
    if 'selected_reaction' not in st.session_state:
        st.error("No reaction selected. Please go back to the Reaction Setup page.")
        return

    reaction_choice = st.session_state['reaction_choice']
    selected_reaction = st.session_state['selected_reaction']
    a = selected_reaction['a']
    b = selected_reaction['b']
    c = selected_reaction['c']
    d = selected_reaction['d']
    delta_H = selected_reaction['delta_H']
    phase_changes = st.session_state['phase_changes']
    temp_effects = st.session_state['temp_effects']
    vol_effects = st.session_state['vol_effects']
    A_perturb_list = st.session_state['A_perturb_list']
    B_perturb_list = st.session_state['B_perturb_list']
    C_perturb_list = st.session_state['C_perturb_list']
    D_perturb_list = st.session_state['D_perturb_list']

    st.write("Reaction Selected:", reaction_choice)
    
    st.sidebar.header("Show/Hide Phase Sections")
    A_phase1 = st.sidebar.checkbox("A Phase 1", value=True)
    A_phase2 = st.sidebar.checkbox("A Phase 2", value=True)
    A_phase3 = st.sidebar.checkbox("A Phase 3", value=True)
    A_phase4 = st.sidebar.checkbox("A Phase 4", value=True)
    B_phase1 = st.sidebar.checkbox("B Phase 1", value=True)
    B_phase2 = st.sidebar.checkbox("B Phase 2", value=True)
    B_phase3 = st.sidebar.checkbox("B Phase 3", value=True)
    B_phase4 = st.sidebar.checkbox("B Phase 4", value=True)
    C_phase1 = st.sidebar.checkbox("C Phase 1", value=True)
    C_phase2 = st.sidebar.checkbox("C Phase 2", value=True)
    C_phase3 = st.sidebar.checkbox("C Phase 3", value=True)
    C_phase4 = st.sidebar.checkbox("C Phase 4", value=True)
    D_phase1 = st.sidebar.checkbox("D Phase 1", value=True)
    D_phase2 = st.sidebar.checkbox("D Phase 2", value=True)
    D_phase3 = st.sidebar.checkbox("D Phase 3", value=True)
    D_phase4 = st.sidebar.checkbox("D Phase 4", value=True)
    show_title = st.sidebar.checkbox("Show Plot Title", value=True)
    
    fig = simulate_reaction(
        a, b, c, d, delta_H,
        temp_effects, vol_effects,
        A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
        phase_changes, show_title,
        A_phase1, A_phase2, A_phase3, A_phase4,
        B_phase1, B_phase2, B_phase3, B_phase4,
        C_phase1, C_phase2, C_phase3, C_phase4,
        D_phase1, D_phase2, D_phase3, D_phase4
    )
    st.pyplot(fig)

# =========================
# Main App Layout
# =========================

st.set_page_config(page_title="Reaction & Simulation App", layout="wide")
page = st.sidebar.radio("Navigate", ["Reaction Setup", "Simulation"])
if page == "Reaction Setup":
    reaction_setup()
elif page == "Simulation":
    simulation_page()
