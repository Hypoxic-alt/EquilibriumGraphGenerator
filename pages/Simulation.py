import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Set page configuration (optional)
st.set_page_config(page_title="Simulation", page_icon="⚗️", layout="wide")

def generic_reaction(concentrations, t, k1, k2, a, b, c, d):
    A, B, C, D = concentrations
    # Calculate forward and reverse reaction rates.
    r_forward = k1 * (A ** a) * (B ** b)
    r_reverse = k2 * (C ** c) * (D ** d)
    r = r_forward - r_reverse
    dA_dt = -a * r
    dB_dt = -b * r
    dC_dt =  c * r
    dD_dt =  d * r
    return [dA_dt, dB_dt, dC_dt, dD_dt]

def simulate_reaction(a, b, c, d, reaction_type,
                      temp_effect, vol_effect,
                      A_perturb, B_perturb, C_perturb, D_perturb,
                      A_phase1, A_phase2, A_phase3, A_phase4,
                      B_phase1, B_phase2, B_phase3, B_phase4,
                      C_phase1, C_phase2, C_phase3, C_phase4,
                      D_phase1, D_phase2, D_phase3, D_phase4,
                      phase_changes, show_title):
    # Base rate constants.
    k1_base = 0.02
    k2_base = 0.01

    # Initialize current rate constants and initial state.
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]

    # The first phase is always "Base". Then three phase changes follow.
    phases = ["Base"] + phase_changes
    sols = []      # To store the solution arrays.
    t_phases = []  # To store time arrays for each phase.

    # Simulate each phase (each phase lasts 200 time units).
    for i, phase in enumerate(phases):
        t_phase = np.linspace(i * 200, (i + 1) * 200, 1000)
        sol = odeint(generic_reaction, init_state, t_phase, args=(k1_current, k2_current, a, b, c, d))
        sols.append(sol)
        t_phases.append(t_phase)
        
        # If not the last phase, apply the specified change.
        if i < len(phases) - 1:
            init_state = sol[-1].copy()
            next_change = phases[i + 1]
            if next_change == "Temperature":
                # For Temperature, adjust the rate constant based on the reaction type.
                if reaction_type == "Exothermic":
                    k2_current = k2_base * (1 + temp_effect)
                else:
                    k1_current = k1_base * (1 + temp_effect)
            elif next_change == "Volume/Pressure":
                # Adjust concentrations for a volume change.
                init_state = init_state / (1 + vol_effect)
            elif next_change == "Addition":
                # Apply the addition (agent perturbation) to each species.
                init_state[0] *= (1 + A_perturb)
                init_state[1] *= (1 + B_perturb)
                init_state[2] *= (1 + C_perturb)
                init_state[3] *= (1 + D_perturb)

    # Create the plot.
    fig = plt.figure(figsize=(10, 6))
    phases_labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]

    # Plot each species in each phase if enabled.
    for i, sol in enumerate(sols):
        if a != 0:
            if (i == 0 and A_phase1) or (i == 1 and A_phase2) or (i == 2 and A_phase3) or (i == 3 and A_phase4):
                plt.plot(t_phases[i], sol[:, 0], label='A ' + phases_labels[i], color='blue', linewidth=2)
    for i, sol in enumerate(sols):
        if b != 0:
            if (i == 0 and B_phase1) or (i == 1 and B_phase2) or (i == 2 and B_phase3) or (i == 3 and B_phase4):
                plt.plot(t_phases[i], sol[:, 1], label='B ' + phases_labels[i], color='red', linewidth=2)
    for i, sol in enumerate(sols):
        if c != 0:
            if (i == 0 and C_phase1) or (i == 1 and C_phase2) or (i == 2 and C_phase3) or (i == 3 and C_phase4):
                plt.plot(t_phases[i], sol[:, 2], label='C ' + phases_labels[i], color='green', linewidth=2)
    for i, sol in enumerate(sols):
        if d != 0:
            if (i == 0 and D_phase1) or (i == 1 and D_phase2) or (i == 2 and D_phase3) or (i == 3 and D_phase4):
                plt.plot(t_phases[i], sol[:, 3], label='D ' + phases_labels[i], color='purple', linewidth=2)

    # Draw vertical dotted lines at phase boundaries.
    for boundary in [200, 400, 600]:
        plt.axvline(x=boundary, color='grey', linestyle=':', linewidth=1)

    # (Optional) Connect the phases with vertical lines.
    def draw_connection(sol_prev, sol_next, t_prev, t_next, color):
        plt.plot([t_prev[-1], t_prev[-1]], [sol_prev[-1], sol_next[0]], color=color, linewidth=2)

    if a != 0:
        if A_phase1 and A_phase2:
            draw_connection(sols[0][:, 0], sols[1][:, 0], t_phases[0], t_phases[1], 'blue')
        if A_phase2 and A_phase3:
            draw_connection(sols[1][:, 0], sols[2][:, 0], t_phases[1], t_phases[2], 'blue')
        if A_phase3 and A_phase4:
            draw_connection(sols[2][:, 0], sols[3][:, 0], t_phases[2], t_phases[3], 'blue')
    if b != 0:
        if B_phase1 and B_phase2:
            draw_connection(sols[0][:, 1], sols[1][:, 1], t_phases[0], t_phases[1], 'red')
        if B_phase2 and B_phase3:
            draw_connection(sols[1][:, 1], sols[2][:, 1], t_phases[1], t_phases[2], 'red')
        if B_phase3 and B_phase4:
            draw_connection(sols[2][:, 1], sols[3][:, 1], t_phases[2], t_phases[3], 'red')
    if c != 0:
        if C_phase1 and C_phase2:
            draw_connection(sols[0][:, 2], sols[1][:, 2], t_phases[0], t_phases[1], 'green')
        if C_phase2 and C_phase3:
            draw_connection(sols[1][:, 2], sols[2][:, 2], t_phases[1], t_phases[2], 'green')
        if C_phase3 and C_phase4:
            draw_connection(sols[2][:, 2], sols[3][:, 2], t_phases[2], t_phases[3], 'green')
    if d != 0:
        if D_phase1 and D_phase2:
            draw_connection(sols[0][:, 3], sols[1][:, 3], t_phases[0], t_phases[1], 'purple')
        if D_phase2 and D_phase3:
            draw_connection(sols[1][:, 3], sols[2][:, 3], t_phases[1], t_phases[2], 'purple')
        if D_phase3 and D_phase4:
            draw_connection(sols[2][:, 3], sols[3][:, 3], t_phases[2], t_phases[3], 'purple')

    plt.xlabel("Time")
    plt.ylabel("Concentration")
    if show_title:
        title_str = ("{}: {}A + {}B ↔ {}C + {}D  |  Reaction: {}  |  Boundaries: {}, {}, {}"
                     .format(st.session_state['reaction_choice'],
                             a, b, c, d, reaction_type,
                             phase_changes[0], phase_changes[1], phase_changes[2]))
        plt.title(title_str)
    plt.tight_layout()
    return fig

# Retrieve stored settings from session state.
if 'selected_reaction' not in st.session_state:
    st.error("No reaction selected. Please go back to the Reaction Setup page.")
else:
    reaction_choice = st.session_state['reaction_choice']
    selected_reaction = st.session_state['selected_reaction']
    a = selected_reaction['a']
    b = selected_reaction['b']
    c = selected_reaction['c']
    d = selected_reaction['d']
    reaction_type = selected_reaction['default_reaction_type']
    phase_changes = st.session_state['phase_changes']
    temp_effect = st.session_state['temp_effect']
    vol_effect = st.session_state['vol_effect']
    A_perturb = st.session_state['A_perturb']
    B_perturb = st.session_state['B_perturb']
    C_perturb = st.session_state['C_perturb']
    D_perturb = st.session_state['D_perturb']

    st.title("Simulation")
    st.write("Reaction Selected:", reaction_choice)

    # Sidebar options to choose which phases to display for each species.
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

    # Run the simulation and display the plot.
    fig = simulate_reaction(a, b, c, d, reaction_type,
                            temp_effect, vol_effect,
                            A_perturb, B_perturb, C_perturb, D_perturb,
                            A_phase1, A_phase2, A_phase3, A_phase4,
                            B_phase1, B_phase2, B_phase3, B_phase4,
                            C_phase1, C_phase2, C_phase3, C_phase4,
                            D_phase1, D_phase2, D_phase3, D_phase4,
                            phase_changes, show_title)
    st.pyplot(fig)
