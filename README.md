# SolarDoc: Solar Home System Fault Expert

SolarDoc is a rule-based expert system that diagnoses faults in off-grid and hybrid solar home systems. The user ticks observable symptoms (what they see, hear, smell, and measure), and the system concludes the likely fault, its urgency, and the recommended action.

It is built with Python and Streamlit and uses forward chaining with certainty factors (MYCIN combination) for reasoning.

## Live application

**Link:** https://your-app-name.streamlit.app

Replace the link above with your deployed Streamlit address.

## Features

- 55 observable conditions grouped into 7 categories
- 74 IF-THEN rules with certainty factors
- 30 fault conclusions, each with an urgency level and recommended action
- Forward-chaining inference engine
- Certainty combination using the MYCIN formula: CF = CF₁ + CF₂ × (1 − CF₁)
- Explanation of every conclusion, showing the rules that fired
- Emergency safety alert for fire and burning hazards
- Adjustable minimum-certainty threshold
- Knowledge base viewer for transparency

## Project structure