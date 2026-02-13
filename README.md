# Hedging CUI Study

This project is a Streamlit-based research application designed to study user decision-making and interactions with AI-based advisors. It investigates how different communication styles (specifically hedging) affect user trust and decision outcomes in a financial scenario.

## Overview

The application guides participants through a structured experiment flow:
1.  **Consent**: Participants reviewed study information and provide consent.
2.  **Pre-Questionnaire (GAAIS)**: General Attitudes towards Artificial Intelligence Scale.
3.  **Decision Task**: Participants read a financial scenario and interact with an AI chatbot (with assigned communication styles) to reach a decision.
4.  **Post-Questionnaire**: Feedback on the interaction and trust metrics.

## Prerequisites

-   Python 3.8+
-   Streamlit

## Installation

1.  Clone the repository or download the project files.
2.  Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Configuration

1.  Create a `.env` file in the root directory.
2.  Add your API key to the `.env` file:

```env
API_KEY=your_api_key_here
```

## Running the Application

To start the user study interface, run the main script using Streamlit:

```bash
streamlit run Consent.py
```

This will launch the application in your default web browser.

## Project Structure

-   `Consent.py`: The entry point for the application. Handles user consent and session initialization.
-   `pages/`: Contains the sequential stages of the study.
    -   `1_GAAIS.py`: Pre-experiment questionnaire.
    -   `2_Chat.py`: The main chat interface and decision task.
    -   `3_Questionnaire.py`: Post-experiment questionnaire.
-   `utils/`: Helper modules for database management, authentication, and UI elements.
-   `components/`: Reusable UI components (e.g., chat message rendering).
-   `data/`: Contains static data such as survey questions and scenarios.
