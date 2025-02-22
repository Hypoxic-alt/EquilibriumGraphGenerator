import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Quiz", page_icon="❓", layout="wide")

# --- Reaction definitions ---
reaction_options = {
    "Haber Process (N₂ + 3H₂ ↔ 2NH₃)": {
        "a": 1, "b": 3, "c": 2, "d": 0,
        "delta_H": -92,  # kJ/mol
        "reagents": {
            "reactant1": "N₂",
            "reactant2": "H₂",
            "product1": "NH₃",
            "product2": ""
        }
    },
    "Contact Reaction (2SO₂ + O₂ ↔ 2SO₃)": {
        "a": 2, "b": 1, "c": 2, "d": 0,
        "delta_H": -197,
        "reagents": {
            "reactant1": "SO₂",
            "reactant2": "O₂",
            "product1": "SO₃",
            "product2": ""
        }
    },
    "Ethanol Production (C₆H₁₂O₆ ↔ 2C₂H₅OH + 2CO₂)": {
        "a": 1, "b": 0, "c": 2, "d": 2,
        "delta_H": -218,
        "reagents": {
            "reactant1": "C₆H₁₂O₆",
            "reactant2": "",
            "product1": "C₂H₅OH",
            "product2": "CO₂"
        }
    },
    "Calcium Carbonate Decomposition (CaCO₃ ↔ CaO + CO₂)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "delta_H": +178,
        "reagents": {
            "reactant1": "CaCO₃",
            "reactant2": "",
            "product1": "CaO",
            "product2": "CO₂"
        }
    },
    "Dissolution of Ammonium Chloride (NH₄Cl ↔ NH₄⁺ + Cl⁻)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "delta_H": +15,
        "reagents": {
            "reactant1": "NH₄Cl",
            "reactant2": "",
            "product1": "NH₄⁺",
            "product2": "Cl⁻"
        }
    },
    "Dissolution of Ammonium Nitrate (NH₄NO₃ ↔ NH₄⁺ + NO₃⁻)": {
        "a": 1, "b": 0, "c": 1, "d": 1,
        "delta_H": +25,
        "reagents": {
            "reactant1": "NH₄NO₃",
            "reactant2": "",
            "product1": "NH₄⁺",
            "product2": "NO₃⁻"
        }
    }
}

# --- Quiz Generation ---
def generate_quiz():
    # Randomly select a reaction.
    reaction_key = random.choice(list(reaction_options.keys()))
    reaction = reaction_options[reaction_key]
    reagents = reaction["reagents"]
    quiz = []
    sim_effects = []      # store simulation effect for each boundary
    addition_choices = [] # for boundaries with Addition, record chosen reagent
    for boundary in range(1, 5):
        change_type = random.choice(["Temperature", "Volume/Pressure", "Addition"])
        if change_type == "Temperature":
            effect = random.choice([0.2, -0.2])
            correct = "Increase in Temperature" if effect > 0 else "Decrease in Temperature"
            options = [correct,
                       "Decrease in Temperature" if effect > 0 else "Increase in Temperature",
                       "Increase in Volume", "Addition of " + (reagents.get("reactant1") or "R1")]
            sim_effects.append(effect)
            addition_choices.append(None)
        elif change_type == "Volume/Pressure":
            effect = random.choice([0.2, -0.2])
            correct = "Increase in Volume" if effect > 0 else "Decrease in Volume"
            options = [correct,
                       "Decrease in Volume" if effect > 0 else "Increase in Volume",
                       "Increase in Temperature", "Addition of " + (reagents.get("reactant1") or "R1")]
            sim_effects.append(effect)
            addition_choices.append(None)
        elif change_type == "Addition":
            available = []
            if reaction["a"] != 0:
                available.append(reagents.get("reactant1", "R1"))
            if reaction["b"] != 0:
                available.append(reagents.get("reactant2", "R2"))
            if reaction["c"] != 0:
                available.append(reagents.get("product1", "P1"))
            if reaction["d"] != 0:
                available.append(reagents.get("product2", "P2"))
            if not available:
                available = ["R1"]
            chosen_reagent = random.choice(available)
            correct = "Addition of " + chosen_reagent
            options = [correct,
                       "Addition of " + (random.choice([x for x in available if x != chosen_reagent]) if len(available)>1 else chosen_reagent),
                       "Increase in Temperature", "Decrease in Temperature"]
            sim_effects.append(random.choice([0.2, -0.2]))
            addition_choices.append(chosen_reagent)
        random.shuffle(options)
        quiz.append({
            "boundary": boundary,
            "change_type": change_type,
            "correct_answer": correct,
            "options": options
        })
    return reaction_key, reaction, quiz, sim_effects, addition_choices

if "quiz" not in st.session_state:
    (r_key, r_data, quiz, sim_effects, addition_choices) = generate_quiz()
    st.session_state.quiz_reaction_key = r_key
    st.session_state.quiz_reaction = r_data
    st.session_state.quiz = quiz
    st.session_state.quiz_sim_effects = sim_effects
    st.session_state.quiz_addition_choices = addition_choices
    st.session_state.quiz_answers = {}

reaction_key = st.session_state.quiz_reaction_key
reaction = st.session_state.quiz_reaction
quiz = st.session_state.quiz
sim_effects = st.session_state.quiz_sim_effects
addition_choices = st.session_state.quiz_addition_choices

# For plotting, extract phase changes from quiz.
phase_changes = [q["change_type"] for q in quiz]

st.title("Quiz")
st.write("**Reaction:**", reaction_key, f"(ΔH = {reaction['delta_H']} kJ/mol)")

# --- Plot the Reaction Simulation ---
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
                      phase_changes, show_title):
    k1_base = 0.02
    k2_base = 0.01
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]
    phases = ["Base"] + phase_changes  # 5 phases
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
                chosen = addition_choices[i]
                if chosen == reaction["reagents"].get("reactant1", "R1"):
                    init_state[0] *= (1 + sim_effects[i])
                elif chosen == reaction["reagents"].get("reactant2", "R2"):
                    init_state[1] *= (1 + sim_effects[i])
                elif chosen == reaction["reagents"].get("product1", "P1"):
                    init_state[2] *= (1 + sim_effects[i])
                elif chosen == reaction["reagents"].get("product2", "P2"):
                    init_state[3] *= (1 + sim_effects[i])
    fig = plt.figure(figsize=(10,6))
    phases_labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
    colors = {'reactant1':'blue','reactant2':'red','product1':'green','product2':'purple'}
    # Plot each phase for each reagent if present.
    if a != 0:
        plt.plot(t_phases[0], sols[0][:,0], label=f"{reaction['reagents'].get('reactant1','R1')} {phases_labels[0]}", color=colors['reactant1'], linewidth=2)
    if b != 0:
        plt.plot(t_phases[0], sols[0][:,1], label=f"{reaction['reagents'].get('reactant2','R2')} {phases_labels[0]}", color=colors['reactant2'], linewidth=2)
    if c != 0:
        plt.plot(t_phases[0], sols[0][:,2], label=f"{reaction['reagents'].get('product1','P1')} {phases_labels[0]}", color=colors['product1'], linewidth=2)
    if d != 0:
        plt.plot(t_phases[0], sols[0][:,3], label=f"{reaction['reagents'].get('product2','P2')} {phases_labels[0]}", color=colors['product2'], linewidth=2)
    for i in range(1, len(phases)):
        if a != 0:
            plt.plot(t_phases[i], sols[i][:,0], label=f"{reaction['reagents'].get('reactant1','R1')} {phases_labels[i]}", color=colors['reactant1'], linewidth=2)
        if b != 0:
            plt.plot(t_phases[i], sols[i][:,1], label=f"{reaction['reagents'].get('reactant2','R2')} {phases_labels[i]}", color=colors['reactant2'], linewidth=2)
        if c != 0:
            plt.plot(t_phases[i], sols[i][:,2], label=f"{reaction['reagents'].get('product1','P1')} {phases_labels[i]}", color=colors['product1'], linewidth=2)
        if d != 0:
            plt.plot(t_phases[i], sols[i][:,3], label=f"{reaction['reagents'].get('product2','P2')} {phases_labels[i]}", color=colors['product2'], linewidth=2)
        t_boundary = t_phases[i-1][-1]
        if a != 0:
            draw_connection(t_boundary, sols[i-1][-1,0], sols[i][0,0], colors['reactant1'])
        if b != 0:
            draw_connection(t_boundary, sols[i-1][-1,1], sols[i][0,1], colors['reactant2'])
        if c != 0:
            draw_connection(t_boundary, sols[i-1][-1,2], sols[i][0,2], colors['product1'])
        if d != 0:
            draw_connection(t_boundary, sols[i-1][-1,3], sols[i][0,3], colors['product2'])
    plt.xlabel("Time")
    plt.ylabel("Concentration")
    plt.title(f"{reaction_key}  |  ΔH = {reaction['delta_H']} kJ/mol")
    plt.tight_layout()
    return fig

# Display the simulation plot before quiz questions.
fig = simulate_reaction(
    reaction["a"], reaction["b"], reaction["c"], reaction["d"], reaction["delta_H"],
    st.session_state.quiz_sim_effects,
    [0.0]*4,  # For simplicity, no separate vol_effects used in the quiz simulation plot.
    [0.0]*4, [0.0]*4, [0.0]*4, [0.0]*4,  # For additions, we rely on quiz_sim_effects inside simulate_reaction.
    phase_changes, True
)
st.pyplot(fig)

# --- Quiz Questions ---
st.write("### Quiz Questions")
for q in quiz:
    ans = st.radio(f"Boundary {q['boundary']} - What change occurred?", q["options"], key=f"q_{q['boundary']}")
    st.session_state.quiz_answers[q["boundary"]] = ans

if st.button("Check Answers"):
    correct_count = 0
    results = []
    for q in quiz:
        user_ans = st.session_state.quiz_answers[q["boundary"]]
        if user_ans == q["correct_answer"]:
            results.append(f"Boundary {q['boundary']}: Correct!")
            correct_count += 1
        else:
            results.append(f"Boundary {q['boundary']}: Incorrect. The correct answer is '{q['correct_answer']}'.")
    st.success(f"You got {correct_count} out of {len(quiz)} correct.")
    for r in results:
        st.write(r)
    st.session_state.checked = True

if "checked" in st.session_state and st.session_state.checked:
    if st.button("Next Question"):
        for key in ["quiz", "quiz_reaction", "quiz_reaction_key", "quiz_sim_effects", "quiz_addition_choices", "quiz_answers", "checked"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
