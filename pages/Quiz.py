import streamlit as st
import random
from scipy.integrate import odeint
import numpy as np

st.set_page_config(page_title="Quiz", page_icon="❓", layout="wide")

# Define our reaction dictionary with ΔH values and reagent names.
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

# Function to generate a new quiz.
def generate_quiz():
    # Randomly select a reaction.
    reaction_key = random.choice(list(reaction_options.keys()))
    reaction = reaction_options[reaction_key]
    reagents = reaction["reagents"]
    # For simplicity, we only ask questions about the 4 boundaries (yielding 5 phases).
    # For each boundary, randomly choose a change type.
    quiz = []
    for boundary in range(1, 5):
        change_type = random.choice(["Temperature", "Volume/Pressure", "Addition"])
        # For Temperature and Volume, randomly choose effect sign.
        if change_type == "Temperature":
            effect = random.choice([0.2, -0.2])
            correct = "Increase in Temperature" if effect > 0 else "Decrease in Temperature"
            # For distractors, include the opposite and one each from the other types.
            distractors = ["Decrease in Temperature" if effect > 0 else "Increase in Temperature",
                           "Increase in Volume", "Addition of " + (reagents.get("reactant1") or "R1")]
        elif change_type == "Volume/Pressure":
            effect = random.choice([0.2, -0.2])
            correct = "Increase in Volume" if effect > 0 else "Decrease in Volume"
            distractors = ["Decrease in Volume" if effect > 0 else "Increase in Volume",
                           "Increase in Temperature", "Addition of " + (reagents.get("reactant1") or "R1")]
        elif change_type == "Addition":
            # From available reagents, choose one at random.
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
            correct = "Addition of " + random.choice(available)
            # For distractors, choose another reagent if available and include two non-addition options.
            other = [x for x in available if x != correct.split()[-1]]
            if other:
                distractor1 = "Addition of " + random.choice(other)
            else:
                distractor1 = "Addition of " + correct.split()[-1]  # fallback; won't match correct
            distractors = [distractor1, "Increase in Temperature", "Decrease in Temperature"]
        # Shuffle options.
        options = [correct] + distractors
        random.shuffle(options)
        quiz.append({
            "boundary": boundary,
            "change_type": change_type,
            "correct_answer": correct,
            "options": options
        })
    return reaction_key, reaction, quiz

# If no quiz exists, generate one.
if "quiz" not in st.session_state:
    reaction_key, reaction, quiz = generate_quiz()
    st.session_state.quiz_reaction_key = reaction_key
    st.session_state.quiz_reaction = reaction
    st.session_state.quiz = quiz
    st.session_state.quiz_answers = {}

reaction_key = st.session_state.quiz_reaction_key
reaction = st.session_state.quiz_reaction
quiz = st.session_state.quiz
reagents = reaction["reagents"]

st.title("Quiz")
st.write("A random reaction has been chosen. Answer the following questions based on the boundary changes that occurred.")

st.write("**Reaction:**", reaction_key, f"(ΔH = {reaction['delta_H']} kJ/mol)")
st.write("**Reagents:**", reagents)

# Display each quiz question.
for q in quiz:
    ans = st.radio(f"Boundary {q['boundary']} - What change occurred?", q["options"], key=f"q_{q['boundary']}")
    st.session_state.quiz_answers[q["boundary"]] = ans

# Check answers button.
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

# Next Question button.
if "checked" in st.session_state and st.session_state.checked:
    if st.button("Next Question"):
        # Clear the quiz from session state.
        for key in ["quiz", "quiz_reaction", "quiz_reaction_key", "quiz_answers", "checked"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()
