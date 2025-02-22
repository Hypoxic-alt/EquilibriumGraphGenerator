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
    return [-a * r, -b * r, c *
