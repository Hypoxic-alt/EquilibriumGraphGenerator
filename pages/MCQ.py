import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import random

st.set_page_config(page_title="MCQ Quiz", page_icon="❓", layout="wide")

st.title("Reaction Quiz")
st.markdown(
    "Below is a simulation plot based on your saved configuration—with one section hidden. "
    "Then answer the two-part quiz below to test your understanding of what occurred at a randomly selected boundary."
)

# --- Check that configuration exists ---
if "config" not in st.session_state:
    st.error("No reaction configuration found. Please go to the Reaction Setup page and save a configuration.")
    st.stop()

# Retrieve saved configuration.
config = st.session_state["config"]
reaction_choice = config["reaction_choice"]
selected_reaction = config["selected_reaction"]
a = selected_reaction["a"]
b = selected_reaction["b"]
c = selected_reaction["c"]
d = selected_reaction["d"]
delta_H = selected_reaction["delta_H"]
phase_changes = config["phase_changes"]   # List of 3 boundary changes.
temp_effects = config["temp_effects"]
vol_effects = config["vol_effects"]
A_perturb_list = config["A_perturb_list"]
B_perturb_list = config["B_perturb_list"]
C_perturb_list = config["C_perturb_list"]
D_perturb_list = config["D_perturb_list"]

st.write("Reaction Selected:", reaction_choice)

# --- Choose a Random Boundary for the Quiz ---
# We want to quiz on one of the three boundaries (index 0, 1, or 2).
if "quiz_boundary_index" not in st.session_state:
    st.session_state.quiz_boundary_index = random.randint(0, len(phase_changes)-1)
quiz_boundary = st.session_state.quiz_boundary_index  # This boundary index (0-based)

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
                           phase_changes, hidden_boundary_index):
    # Base rate constants.
    k1_base = 0.02
    k2_base = 0.01
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]
    
    # There are 4 phases: Base + 3 boundaries → Phase 1, Phase 2, Phase 3, Phase 4.
    phases = ["Phase 1"] + ["Phase 2", "Phase 3", "Phase 4"]
    sols = []
    t_phases = []
    
    # For each phase, integrate the ODE.
    for i in range(len(phases)):
        t_phase = np.linspace(i * 200, (i + 1) * 200, 1000)
        sol = odeint(generic_reaction, init_state, t_phase, args=(k1_current, k2_current, a, b, c, d))
        sols.append(sol)
        t_phases.append(t_phase)
        # Update state only if there is a boundary change (i < last phase).
        if i < len(phases) - 1:
            init_state = sol[-1].copy()
            # The boundary change applied is from phase i to phase i+1.
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
                
    # Create a plot.
    fig = plt.figure(figsize=(10, 6))
    # We'll use these labels for clarity.
    for i, sol in enumerate(sols):
        # Always plot species A, C, D.
        if a != 0:
            plt.plot(t_phases[i], sol[:, 0], label=f'A {phases[i]}', color='blue', linewidth=2)
        if c != 0:
            plt.plot(t_phases[i], sol[:, 2], label=f'C {phases[i]}', color='green', linewidth=2)
        if d != 0:
            plt.plot(t_phases[i], sol[:, 3], label=f'D {phases[i]}', color='purple', linewidth=2)
        # For species B, hide the phase corresponding to the selected boundary change.
        # The boundary change at index X affects the transition from phase (X+1) to phase (X+2).
        # Here, we choose to hide species B in phase (hidden_boundary_index+1).
        if b != 0:
            if i == hidden_boundary_index + 1:
                # Do not plot species B for this phase.
                pass
            else:
                plt.plot(t_phases[i], sol[:, 1], label=f'B {phases[i]}', color='red', linewidth=2)
                
    # Draw connection lines between phases.
    for i in range(len(phases)-1):
        t_boundary = t_phases[i][-1]
        if a != 0:
            draw_connection(t_boundary, sols[i][-1, 0], sols[i+1][0, 0], 'blue')
        if b != 0:
            # Only draw connection for species B if it is not part of the hidden phase.
            if i != hidden_boundary_index:
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

# Generate the simulation plot, hiding species B in the phase corresponding to our chosen boundary.
# Note: For a boundary at index X, we hide species B in phase (X+1).
fig = simulate_reaction_quiz(a, b, c, d, delta_H,
                             temp_effects, vol_effects,
                             A_perturb_list, B_perturb_list, C_perturb_list, D_perturb_list,
                             phase_changes, hidden_boundary_index=quiz_boundary)
st.pyplot(fig)

# --- Quiz State Initialization ---
if "quiz_stage" not in st.session_state:
    st.session_state.quiz_stage = 0
if "quiz1_answer" not in st.session_state:
    st.session_state.quiz1_answer = None
if "quiz2_answer" not in st.session_state:
    st.session_state.quiz2_answer = None

# --- New Quiz Button ---
if st.button("New Quiz"):
    # Remove quiz-related keys to reset.
    for key in ["quiz_stage", "quiz1_answer", "quiz2_answer", "quiz_boundary_index"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# --- Determine the boundary label (1-indexed) for display ---
quiz_boundary_label = quiz_boundary + 1

# --- Stage 1: Ask Type of Change ---
if st.session_state.quiz_stage == 0:
    st.markdown("### Quiz Question - Stage 1")
    q1 = f"What type of boundary change was applied at Boundary {quiz_boundary_label}?"
    options1 = ["Temperature", "Volume/Pressure", "Addition"]
    answer1 = st.radio(q1, options1, key="q1")
    if st.button("Submit Answer for Stage 1"):
        st.session_state.quiz1_answer = answer1
        st.session_state.quiz_stage = 1

# Once Stage 1 is submitted, show feedback and Stage 2.
if st.session_state.quiz_stage >= 1:
    correct_q1 = phase_changes[quiz_boundary]  # The saved change type for this boundary.
    if st.session_state.quiz1_answer == correct_q1:
        st.success(f"Stage 1 Correct! The boundary change was '{correct_q1}'.")
    else:
        st.error(f"Stage 1 Incorrect. You answered '{st.session_state.quiz1_answer}', but the correct answer is '{correct_q1}'.")
    
    # --- Stage 2: Ask Direction of Change ---
    st.markdown("### Quiz Question - Stage 2")
    # Use the slider value for the chosen boundary.
    if correct_q1 == "Temperature":
        slider_val = temp_effects[quiz_boundary]
        direction_question = f"At Boundary {quiz_boundary_label}, was the temperature increased or decreased?"
    elif correct_q1 == "Volume/Pressure":
        slider_val = vol_effects[quiz_boundary]
        direction_question = f"At Boundary {quiz_boundary_label}, was the volume/pressure increased or decreased?"
    elif correct_q1 == "Addition":
        # For addition, check the perturbation for reagent A if available.
        if selected_reaction["a"] != 0:
            slider_val = A_perturb_list[quiz_boundary]
        else:
            slider_val = 0.0
        direction_question = f"At Boundary {quiz_boundary_label}, did the addition indicate an increase or decrease for reagent A?"
    else:
        slider_val = 0.0
        direction_question = f"What was the direction of the change at Boundary {quiz_boundary_label}?"
    
    options2 = ["Increase", "Decrease"]
    answer2 = st.radio(direction_question, options2, key="q2")
    if st.button("Submit Answer for Stage 2"):
        st.session_state.quiz2_answer = answer2
        # Determine correct direction based on the slider value.
        if slider_val > 0:
            correct_direction = "Increase"
        elif slider_val < 0:
            correct_direction = "Decrease"
        else:
            correct_direction = "No change"
        if st.session_state.quiz2_answer == correct_direction:
            st.success(f"Stage 2 Correct! The slider value was {slider_val:.2f}, indicating '{correct_direction}'.")
        else:
            st.error(f"Stage 2 Incorrect. You answered '{st.session_state.quiz2_answer}', but the correct answer is '{correct_direction}'.")
