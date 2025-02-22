import streamlit as st
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

st.set_page_config(page_title="Quiz", page_icon="❓", layout="wide")

# --- Reaction definitions (same as before) ---
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
    # We will have 4 boundaries (thus 5 phases).
    quiz = []
    sim_effects = []      # store simulation effect for each boundary
    addition_choices = [] # for boundaries of type "Addition", record which reagent is chosen
    for boundary in range(1, 5):
        change_type = random.choice(["Temperature", "Volume/Pressure", "Addition"])
        # For Temperature and Volume, choose a random effect value from ±0.2.
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
            # For addition, choose a reagent from those present.
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
            # Create distinct options: include the correct addition and two non-addition options.
            options = [correct, 
                       "Addition of " + (random.choice([x for x in available if x != chosen_reagent]) if len(available)>1 else chosen_reagent),
                       "Increase in Temperature", "Decrease in Temperature"]
            sim_effects.append(random.choice([0.2, -0.2]))  # use a random effect for addition
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
reagents = reaction["reagents"]

st.title("Quiz")
st.write("A random reaction has been chosen. Answer the following questions based on the boundary changes that occurred.")

st.write("**Reaction:**", reaction_key, f"(ΔH = {reaction['delta_H']} kJ/mol)")
st.write("**Reagents:**", reagents)

# Display quiz questions.
for q in quiz:
    ans = st.radio(f"Boundary {q['boundary']} - What change occurred?", q["options"], key=f"q_{q['boundary']}")
    st.session_state.quiz_answers[q["boundary"]] = ans

# Check Answers
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

# Next Question button uses st.rerun()
if "checked" in st.session_state and st.session_state.checked:
    if st.button("Next Question"):
        for key in ["quiz", "quiz_reaction", "quiz_reaction_key", "quiz_sim_effects", "quiz_addition_choices", "quiz_answers", "checked"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Plot the Reaction ---
st.write("### Reaction Simulation")
# Here we plot the reaction based on the quiz parameters.
# We reuse a simulation function similar to the Simulation page, but using our quiz simulation effect values.
def generic_reaction(concentrations, t, k1, k2, a, b, c, d):
    A, B, C, D = concentrations
    r_forward = k1 * (A ** a) * (B ** b)
    r_reverse = k2 * (C ** c) * (D ** d)
    r = r_forward - r_reverse
    return [-a*r, -b*r, c*r, d*r]

def draw_connection(t_value, prev_value, next_value, color):
    plt.vlines(t_value, prev_value, next_value, colors=color, linestyles='solid', linewidth=2)

def simulate_reaction(a, b, c, d, delta_H,
                      sim_effects, phase_types, addition_choices,
                      # We'll assume 5 phases (4 boundaries) with fixed time intervals of 200 units.
                      ):
    k1_base = 0.02
    k2_base = 0.01
    k1_current = k1_base
    k2_current = k2_base
    init_state = [1.0, 1.0, 0.0, 0.0]
    phases = ["Base"] + phase_types  # phase_types is a list of 4 change types
    sols = []
    t_phases = []
    for i, phase in enumerate(phases):
        t_phase = np.linspace(i * 200, (i + 1) * 200, 1000)
        sol = odeint(generic_reaction, init_state, t_phase, args=(k1_current, k2_current, a, b, c, d))
        sols.append(sol)
        t_phases.append(t_phase)
        if i < len(phases)-1:
            init_state = sol[-1].copy()
            current_boundary = phase_types[i]
            if current_boundary == "Temperature":
                effect = sim_effects[i]
                if delta_H < 0:
                    k2_current = k2_base * (1 + effect)
                else:
                    k1_current = k1_base * (1 + effect)
            elif current_boundary == "Volume/Pressure":
                effect = sim_effects[i]
                init_state = init_state / (1 + effect)
            elif current_boundary == "Addition":
                # For addition, apply effect to the chosen reagent.
                chosen = addition_choices[i]
                # For each species, if its reagent matches chosen, apply the effect.
                # We assume for simplicity that addition effect increases concentration by (1 + effect).
                if chosen == reagents.get("reactant1", "R1"):
                    init_state[0] *= (1 + sim_effects[i])
                if chosen == reagents.get("reactant2", "R2"):
                    init_state[1] *= (1 + sim_effects[i])
                if chosen == reagents.get("product1", "P1"):
                    init_state[2] *= (1 + sim_effects[i])
                if chosen == reagents.get("product2", "P2"):
                    init_state[3] *= (1 + sim_effects[i])
    fig = plt.figure(figsize=(10,6))
    phases_labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
    colors = ['blue','red','green','purple']
    # Plot all curves.
    if a != 0:
        plt.plot(t_phases[0], sols[0][:,0], label=f"{reagents.get('reactant1','R1')} Phase 1", color='blue', linewidth=2)
    if b != 0:
        plt.plot(t_phases[0], sols[0][:,1], label=f"{reagents.get('reactant2','R2')} Phase 1", color='red', linewidth=2)
    if c != 0:
        plt.plot(t_phases[0], sols[0][:,2], label=f"{reagents.get('product1','P1')} Phase 1", color='green', linewidth=2)
    if d != 0:
        plt.plot(t_phases[0], sols[0][:,3], label=f"{reagents.get('product2','P2')} Phase 1", color='purple', linewidth=2)
    # Plot subsequent phases (for simplicity, we plot each phase's curves).
    for i in range(1, len(phases)):
        if a != 0:
            plt.plot(t_phases[i], sols[i][:,0], label=f"{reagents.get('reactant1','R1')} Phase {i+1}", color='blue', linewidth=2)
        if b != 0:
            plt.plot(t_phases[i], sols[i][:,1], label=f"{reagents.get('reactant2','R2')} Phase {i+1}", color='red', linewidth=2)
        if c != 0:
            plt.plot(t_phases[i], sols[i][:,2], label=f"{reagents.get('product1','P1')} Phase {i+1}", color='green', linewidth=2)
        if d != 0:
            plt.plot(t_phases[i], sols[i][:,3], label=f"{reagents.get('product2','P2')} Phase {i+1}", color='purple', linewidth=2)
        # Draw vertical connection between phases.
        t_boundary = t_phases[i-1][-1]
        if a != 0:
            draw_connection(t_boundary, sols[i-1][-1,0], sols[i][0,0], 'blue')
        if b != 0:
            draw_connection(t_boundary, sols[i-1][-1,1], sols[i][0,1], 'red')
        if c != 0:
            draw_connection(t_boundary, sols[i-1][-1,2], sols[i][0,2], 'green')
        if d != 0:
            draw_connection(t_boundary, sols[i-1][-1,3], sols[i][0,3], 'purple')
    plt.xlabel("Time")
    plt.ylabel("Concentration")
    plt.title(f"{reaction_key}  |  ΔH = {delta_H} kJ/mol")
    plt.tight_layout()
    return fig

# Now, generate and display the plot using the quiz simulation parameters.
fig = simulate_reaction(
    reaction["a"], reaction["b"], reaction["c"], reaction["d"], reaction["delta_H"],
    st.session_state.quiz_sim_effects,
    st.session_state.quiz,  # phase_changes list from quiz; we use the same quiz questions list to extract change types
    st.session_state.quiz_sim_effects,  # not used for addition here; see below
    # For additions, we need to provide perturbation lists:
    # For each boundary, if the change type is Addition, then apply the simulation effect to the chosen reagent.
    # We'll build these lists: for each boundary, for reagent A, if chosen matches reagent1, then effect else 0.
    [st.session_state.quiz_sim_effects[i] if st.session_state.quiz[i]["change_type"]=="Addition" and addition_choices[i]==reaction["a"] or False else 0.0 for i in range(4)],
    [st.session_state.quiz_sim_effects[i] if st.session_state.quiz[i]["change_type"]=="Addition" and addition_choices[i]==reaction["b"] or False else 0.0 for i in range(4)],
    [st.session_state.quiz_sim_effects[i] if st.session_state.quiz[i]["change_type"]=="Addition" and addition_choices[i]==reaction["c"] or False else 0.0 for i in range(4)],
    [st.session_state.quiz_sim_effects[i] if st.session_state.quiz[i]["change_type"]=="Addition" and addition_choices[i]==reaction["d"] or False else 0.0 for i in range(4)],
    st.session_state.quiz,  # using quiz as phase_changes list (should be a list of 4 strings)
    True  # show_title
)
st.pyplot(fig)
