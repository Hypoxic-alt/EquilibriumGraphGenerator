import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="MCQ Quiz", page_icon="❓", layout="wide")

st.title("Reaction Quiz")
st.markdown(
    "Below is a simulation plot based on your saved configuration—with one section hidden. "
    "Answer the quiz question below to test your understanding of what occurred at that boundary."
)

# Check if configuration exists.
if "config" not in st.session_state:
    st.error("No reaction configuration found. Please go to the Reaction Setup page and save a configuration.")
    st.stop()

# Retrieve configuration.
config = st.session_state["config"]
reaction_choice = config["reaction_choice"]
selected_reaction = config["selected_reaction"]
a = selected_reaction["a"]
b = selected_reaction["b"]
c = selected_reaction["c"]
d = selected_reaction["d"]
delta_H = selected_reaction["delta_H"]
phase_changes = config["phase_changes"]
temp_effects = config["temp_effects"]
vol_effects = config["vol_effects"]
A_perturb_list = config["A_perturb_list"]
B_perturb_list = config["B_perturb_list"]
C_perturb_list = config["C_perturb_list"]
D_perturb_list = config["D_perturb_list"]

st.write("Reaction Selected:", reaction_choice)

# --- Simulation Function for Quiz Page ---
def generic_reaction(concentrations, t, k1, k2, a, b, c, d):
    A, B, C, D = concentrations
    r_forward = k1 * (A ** a) * (B ** b)
    r_reverse = k2 * (C ** c) * (D ** d)
    r = r_forward - r_reverse
    return [-a * r, -b * r, c * r, d * r]

def draw_connection(t_value, prev_value, next_value, color):
    plt.vlines(t_value, prev_value, next_value, colors=color, linestyles='solid', linewidth=2)

def simulate_reaction_quiz(a, b, c, d, delta_H,
                           temp_effects, vol_effects,
                           A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
                           phase_changes):
    # Base rate constants.
    k1_base = 0.02
    k2_base = 0.01
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]
    
    # There are 4 phases: Base and 3 subsequent phases.
    phases = ["Base"] + phase_changes  # phase_changes list length should be 3.
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
                
    # Create a plot
    fig = plt.figure(figsize=(10, 6))
    phases_labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    
    # For each phase, plot species curves.
    for i, sol in enumerate(sols):
        # For species A, C, D, plot all phases.
        if a != 0:
            plt.plot(t_phases[i], sol[:, 0], label=f'A {phases_labels[i]}', color='blue', linewidth=2)
        if c != 0:
            plt.plot(t_phases[i], sol[:, 2], label=f'C {phases_labels[i]}', color='green', linewidth=2)
        if d != 0:
            plt.plot(t_phases[i], sol[:, 3], label=f'D {phases_labels[i]}', color='purple', linewidth=2)
        # For species B, hide one section. In this example, we do not plot B in Phase 3.
        if b != 0:
            if i == 2:
                # Hide the Phase 3 section for species B.
                pass  # Do not plot species B in Phase 3.
            else:
                plt.plot(t_phases[i], sol[:, 1], label=f'B {phases_labels[i]}', color='red', linewidth=2)
                
    # Optionally, draw connection lines between phases.
    for i in range(len(phases)-1):
        t_boundary = t_phases[i][-1]
        if a != 0:
            draw_connection(t_boundary, sols[i][-1, 0], sols[i+1][0, 0], 'blue')
        if b != 0:
            # For species B, draw connection only if not hidden.
            if i != 1:  # If the hidden section is after Phase 2, skip drawing for that boundary.
                draw_connection(t_boundary, sols[i][-1, 1], sols[i+1][0, 1], 'red')
        if c != 0:
            draw_connection(t_boundary, sols[i][-1, 2], sols[i+1][0, 2], 'green')
        if d != 0:
            draw_connection(t_boundary, sols[i][-1, 3], sols[i+1][0, 3], 'purple')
                
    plt.xlabel("Time")
    plt.ylabel("Concentration")
    title_str = "{}  |  ΔH = {} kJ/mol".format(reaction_choice, delta_H)
    plt.title(title_str)
    plt.tight_layout()
    return fig

# Generate the simulation plot for the quiz.
fig = simulate_reaction_quiz(a, b, c, d, delta_H,
                             temp_effects, vol_effects,
                             A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
                             phase_changes)
st.pyplot(fig)

# --- Quiz Section ---
st.markdown("### Quiz Question")
# For this example, we ask about Boundary 2 (i.e. the change between Phase 2 and Phase 3).
# In our configuration, this is stored in config["phase_changes"][1].
quiz_question = "What type of boundary change was applied at Boundary 2 (between Phase 2 and Phase 3)?"
options = ["Temperature", "Volume/Pressure", "Addition"]
user_answer = st.radio(quiz_question, options)

if st.button("Submit Answer"):
    correct_answer = config["phase_changes"][1]
    if user_answer == correct_answer:
        st.success("Correct!")
    else:
        st.error(f"Incorrect. The correct answer was: {correct_answer}.")
