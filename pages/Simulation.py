import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Simulation", page_icon="⚗️", layout="wide")

def generic_reaction(concentrations, t, k1, k2, a, b, c, d):
    A, B, C, D = concentrations
    r_forward = k1 * (A ** a) * (B ** b)
    r_reverse = k2 * (C ** c) * (D ** d)
    r = r_forward - r_reverse
    return [-a * r, -b * r, c * r, d * r]

def draw_connection(t_value, prev_value, next_value, color):
    plt.vlines(t_value, prev_value, next_value, colors=color, linestyles='solid', linewidth=2)

def simulate_reaction(a, b, c, d, delta_H,
                      temp_effects, vol_effects,
                      A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
                      phase_changes, show_title,
                      # Phase display toggles for each reagent:
                      r1_phase1, r1_phase2, r1_phase3, r1_phase4, r1_phase5,
                      r2_phase1, r2_phase2, r2_phase3, r2_phase4, r2_phase5,
                      p1_phase1, p1_phase2, p1_phase3, p1_phase4, p1_phase5,
                      p2_phase1, p2_phase2, p2_phase3, p2_phase4, p2_phase5):
    k1_base = 0.02
    k2_base = 0.01
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]
    
    # 5 phases (4 boundaries)
    phases = ["Base"] + phase_changes  # length = 5
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
    phases_labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
    
    # Plot curves for each reagent if enabled.
    # Reactant 1 (A)
    if a != 0:
        for i, sol in enumerate(sols):
            if (i == 0 and r1_phase1) or (i == 1 and r1_phase2) or (i == 2 and r1_phase3) or (i == 3 and r1_phase4) or (i == 4 and r1_phase5):
                plt.plot(t_phases[i], sol[:, 0], label=f"{reagents.get('reactant1','R1')} {phases_labels[i]}", color='blue', linewidth=2)
    # Reactant 2 (B)
    if b != 0:
        for i, sol in enumerate(sols):
            if (i == 0 and r2_phase1) or (i == 1 and r2_phase2) or (i == 2 and r2_phase3) or (i == 3 and r2_phase4) or (i == 4 and r2_phase5):
                plt.plot(t_phases[i], sol[:, 1], label=f"{reagents.get('reactant2','R2')} {phases_labels[i]}", color='red', linewidth=2)
    # Product 1 (C)
    if c != 0:
        for i, sol in enumerate(sols):
            if (i == 0 and p1_phase1) or (i == 1 and p1_phase2) or (i == 2 and p1_phase3) or (i == 3 and p1_phase4) or (i == 4 and p1_phase5):
                plt.plot(t_phases[i], sol[:, 2], label=f"{reagents.get('product1','P1')} {phases_labels[i]}", color='green', linewidth=2)
    # Product 2 (D)
    if d != 0:
        for i, sol in enumerate(sols):
            if (i == 0 and p2_phase1) or (i == 1 and p2_phase2) or (i == 2 and p2_phase3) or (i == 3 and p2_phase4) or (i == 4 and p2_phase5):
                plt.plot(t_phases[i], sol[:, 3], label=f"{reagents.get('product2','P2')} {phases_labels[i]}", color='purple', linewidth=2)
    
    # Draw vertical connections between phases.
    for i in range(len(phases)-1):
        t_boundary = t_phases[i][-1]
        if a != 0 and ((i == 0 and r1_phase1 and r1_phase2) or (i == 1 and r1_phase2 and r1_phase3) or (i == 2 and r1_phase3 and r1_phase4) or (i == 3 and r1_phase4 and r1_phase5)):
            draw_connection(t_boundary, sols[i][-1, 0], sols[i+1][0, 0], 'blue')
        if b != 0 and ((i == 0 and r2_phase1 and r2_phase2) or (i == 1 and r2_phase2 and r2_phase3) or (i == 2 and r2_phase3 and r2_phase4) or (i == 3 and r2_phase4 and r2_phase5)):
            draw_connection(t_boundary, sols[i][-1, 1], sols[i+1][0, 1], 'red')
        if c != 0 and ((i == 0 and p1_phase1 and p1_phase2) or (i == 1 and p1_phase2 and p1_phase3) or (i == 2 and p1_phase3 and p1_phase4) or (i == 3 and p1_phase4 and p1_phase5)):
            draw_connection(t_boundary, sols[i][-1, 2], sols[i+1][0, 2], 'green')
        if d != 0 and ((i == 0 and p2_phase1 and p2_phase2) or (i == 1 and p2_phase2 and p2_phase3) or (i == 2 and p2_phase3 and p2_phase4) or (i == 3 and p2_phase4 and p2_phase5)):
            draw_connection(t_boundary, sols[i][-1, 3], sols[i+1][0, 3], 'purple')
    
    plt.xlabel("Time")
    plt.ylabel("Concentration")
    if show_title:
        title_str = "{}  |  ΔH = {} kJ/mol".format(st.session_state['reaction_choice'], delta_H)
        plt.title(title_str)
    plt.tight_layout()
    return fig

# Retrieve saved configuration.
if 'selected_reaction' not in st.session_state:
    st.error("No reaction selected. Please go back to the Reaction Setup page.")
else:
    reaction_choice = st.session_state['reaction_choice']
    selected_reaction = st.session_state['selected_reaction']
    reagents = selected_reaction["reagents"]
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

    st.title("Simulation")
    st.write("Reaction Selected:", reaction_choice)
    
    # Place the Show Plot Title tick box at the top of the sidebar.
    show_title = st.sidebar.checkbox("Show Plot Title", value=True)
    
    st.sidebar.header("Show/Hide Phase Sections")
    # Only show checkboxes for reagents that are present.
    if a != 0:
        r1_phase1 = st.sidebar.checkbox(f"{reagents.get('reactant1', 'R1')} Phase 1", value=True)
        r1_phase2 = st.sidebar.checkbox(f"{reagents.get('reactant1', 'R1')} Phase 2", value=True)
        r1_phase3 = st.sidebar.checkbox(f"{reagents.get('reactant1', 'R1')} Phase 3", value=True)
        r1_phase4 = st.sidebar.checkbox(f"{reagents.get('reactant1', 'R1')} Phase 4", value=True)
        r1_phase5 = st.sidebar.checkbox(f"{reagents.get('reactant1', 'R1')} Phase 5", value=True)
    else:
        r1_phase1 = r1_phase2 = r1_phase3 = r1_phase4 = r1_phase5 = False

    if b != 0:
        r2_phase1 = st.sidebar.checkbox(f"{reagents.get('reactant2', 'R2')} Phase 1", value=True)
        r2_phase2 = st.sidebar.checkbox(f"{reagents.get('reactant2', 'R2')} Phase 2", value=True)
        r2_phase3 = st.sidebar.checkbox(f"{reagents.get('reactant2', 'R2')} Phase 3", value=True)
        r2_phase4 = st.sidebar.checkbox(f"{reagents.get('reactant2', 'R2')} Phase 4", value=True)
        r2_phase5 = st.sidebar.checkbox(f"{reagents.get('reactant2', 'R2')} Phase 5", value=True)
    else:
        r2_phase1 = r2_phase2 = r2_phase3 = r2_phase4 = r2_phase5 = False

    if c != 0:
        p1_phase1 = st.sidebar.checkbox(f"{reagents.get('product1', 'P1')} Phase 1", value=True)
        p1_phase2 = st.sidebar.checkbox(f"{reagents.get('product1', 'P1')} Phase 2", value=True)
        p1_phase3 = st.sidebar.checkbox(f"{reagents.get('product1', 'P1')} Phase 3", value=True)
        p1_phase4 = st.sidebar.checkbox(f"{reagents.get('product1', 'P1')} Phase 4", value=True)
        p1_phase5 = st.sidebar.checkbox(f"{reagents.get('product1', 'P1')} Phase 5", value=True)
    else:
        p1_phase1 = p1_phase2 = p1_phase3 = p1_phase4 = p1_phase5 = False

    if d != 0:
        p2_phase1 = st.sidebar.checkbox(f"{reagents.get('product2', 'P2')} Phase 1", value=True)
        p2_phase2 = st.sidebar.checkbox(f"{reagents.get('product2', 'P2')} Phase 2", value=True)
        p2_phase3 = st.sidebar.checkbox(f"{reagents.get('product2', 'P2')} Phase 3", value=True)
        p2_phase4 = st.sidebar.checkbox(f"{reagents.get('product2', 'P2')} Phase 4", value=True)
        p2_phase5 = st.sidebar.checkbox(f"{reagents.get('product2', 'P2')} Phase 5", value=True)
    else:
        p2_phase1 = p2_phase2 = p2_phase3 = p2_phase4 = p2_phase5 = False

    fig = simulate_reaction(
        a, b, c, d, delta_H,
        temp_effects, vol_effects,
        A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
        phase_changes, show_title,
        r1_phase1, r1_phase2, r1_phase3, r1_phase4, r1_phase5,
        r2_phase1, r2_phase2, r2_phase3, r2_phase4, r2_phase5,
        p1_phase1, p1_phase2, p1_phase3, p1_phase4, p1_phase5,
        p2_phase1, p2_phase2, p2_phase3, p2_phase4, p2_phase5
    )
    st.pyplot(fig)
