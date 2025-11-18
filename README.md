Synthetic User Simulator
AI-powered simulation of user behavior across product flows

Test product flows using synthetic AI users — before launching real experiments.
This project simulates how different user personas (with distinct traits, motivations, and frictions) move through a defined flow like onboarding, checkout, subscription, or creative surfaces.

Built with: Python, Streamlit, OpenAI GPT-4o-mini, and product sense.

🚀 Why I Built This

Product teams spend weeks running A/B tests, waiting for traffic, or gathering meaningful signals from real users.

With this tool, PMs and designers can:

Simulate conversion behavior instantly

Identify high-friction steps

See where users drop off

Understand persona-specific reasoning and emotions

Compare variations of flows

Iterate faster — before committing engineering cycles

This is a step toward the future of autonomous product development:

AI-driven UX testing and continuous product iteration — without needing real traffic.

🎥 Demo (Preview)

[ Live Demo Link ]

✨ Core Features
🧩 1. Flow Definition

Paste or create a step-by-step flow:

1. Landing Page - Hero section with primary CTA
2. Sign Up Form - Email + password
3. Plan Selection - Basic vs Pro
4. Checkout - Payment details


The app parses this into structured steps.

🧬 2. AI-Generated User Personas

The system creates 3–15 synthetic users with:

Name & short bio

Traits (e.g., risk-averse, budget-sensitive, ADHD-like, time-crunched parent)

Behavioral tendencies (e.g., “drops on long forms”, “needs social proof”)

No two runs are the same — personas are dynamic and diverse.

🔍 3. Step-Level Simulation

Each persona moves through each step with AI-determined outputs:

Action → continue / hesitate / drop

Friction score (1–10)

Reasoning (short explanation)

If a persona drops at Step 2, they never reach Step 3.

📊 4. Metrics & Insights

The simulator aggregates:

Synthetic conversion rate

Step-level stats

views

drops

drop rate

average friction

Persona outcomes

Full reasoning logs per persona

Perfect for PMs, UX teams, and growth analysts.

🛠️ Tech Stack

Frontend:

Streamlit (fast prototyping, clean UI, reactive layout)

Backend:

Python

Dataclasses for structured modeling

OpenAI GPT-4o-mini for:

Persona generation

Behavior simulation

Step-level reasoning

Architecture:

simulator.py → logic, persona modeling, step simulation

app.py → Streamlit interface

requirements.txt → reproducibility

The system is modular and designed for easy expansion (multi-agent, images, real-time comparisons).

📷 Screenshots

(Add screenshots after running the app locally)

/screenshots/personas.png
/screenshots/results.png
/screenshots/journey.png

🧑‍💻 Getting Started
1. Clone the repo
git clone https://github.com/<yourusername>/synthetic-user-simulator.git
cd synthetic-user-simulator

2. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set your OpenAI key

Add to your terminal profile (.bash_profile / .zshrc):

export OPENAI_API_KEY="sk-..."


Reload:

source ~/.bash_profile

5. Run the app
streamlit run app.py


It opens automatically at:
http://localhost:8501

🧭 Roadmap (Planned Enhancements)
🔹 V2 – Flow Variants & A/B Comparison

Simulate personas through two versions of the flow and compare:

Conversion delta

Friction delta

Step-level differences

🔹 V3 – Screenshot & UI-based Simulation

Upload a screenshot for each step → personas analyze UI elements.

This becomes AI-driven UX testing.

🔹 V4 – Persona sliders for controlled cohorts

Let the user tune:

Patience

Trust

Tech literacy

Motivation

Risk tolerance

🔹 V5 – Multi-agent markets

Simulate 500–5,000 synthetic users at once.

🔹 V6 – Insights summary generator

AI produces:

UX audit

Redesign recommendations

Prioritization matrix

Mockups suggestions
