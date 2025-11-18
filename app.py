import streamlit as st
from typing import List
from simulator import Step, generate_personas, simulate_persona_through_flow, summarize_runs

st.set_page_config(page_title="Synthetic User Simulator", page_icon="🧪", layout="wide")

st.title("🧪 Synthetic User Simulator")
st.write(
    "Simulate how different synthetic users move through a product flow. "
    "Define a flow, generate personas, and see where they drop off."
)

# ----------- Sample flow -----------
DEFAULT_FLOW_TEXT = """1. Landing Page - Hero section with value prop and primary CTA: 'Get Started'
2. Sign Up Form - Email, password, and marketing opt-in checkbox
3. Plan Selection - Choose between Basic, Pro, and Premium plans
4. Checkout - Enter payment details and confirm subscription
"""

st.subheader("1️⃣ Define your flow")

flow_text = st.text_area(
    "Describe your flow steps (one per line, numbered):",
    value=DEFAULT_FLOW_TEXT,
    height=200,
)

num_personas = st.slider("How many personas to simulate?", min_value=3, max_value=15, value=5, step=1)

if "steps" not in st.session_state:
    st.session_state.steps: List[Step] = []


def parse_flow(text: str) -> List[Step]:
    steps: List[Step] = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        # Very simple parse: split on " - " into name + description
        if " - " in line:
            name_part, desc_part = line.split(" - ", 1)
        else:
            name_part, desc_part = f"Step {i+1}", line

        name = name_part.strip("0123456789. ").strip()
        desc = desc_part.strip()
        steps.append(
            Step(
                id=i,
                name=name or f"Step {i+1}",
                description=desc,
                type="decision",  # For V1, treat all as "decision" steps
            )
        )
    return steps


if st.button("Parse flow"):
    st.session_state.steps = parse_flow(flow_text)
    st.success(f"Parsed {len(st.session_state.steps)} steps.")

steps = st.session_state.get("steps", [])
if steps:
    st.markdown("**Parsed flow steps:**")
    for s in steps:
        st.markdown(f"- **{s.name}**: {s.description}")

st.markdown("---")
st.subheader("2️⃣ Generate personas & run simulation")

if st.button("Generate personas and simulate"):
    if not steps:
        st.error("Please parse a flow first.")
    else:
        with st.spinner("Generating personas..."):
            flow_description = "\n".join(f"{s.name}: {s.description}" for s in steps)
            personas = generate_personas(flow_description, num_personas=num_personas)

        st.success(f"Generated {len(personas)} personas.")

        with st.spinner("Simulating personas through the flow..."):
            runs = []
            for p in personas:
                run = simulate_persona_through_flow(p, steps)
                runs.append(run)

        summary = summarize_runs(runs, steps)

        # --------- High-level results ---------
        st.markdown("### 3️⃣ Results overview")

        conv_rate = summary["conversion_rate"]
        st.metric("Conversion rate (synthetic)", f"{conv_rate*100:.1f}%")

        # Step-level table
        st.markdown("#### Step-level stats")
        step_rows = []
        for sid, s in summary["step_stats"].items():
            step_rows.append(
                {
                    "Step": s["name"],
                    "Views": s["views"],
                    "Drops": s["drops"],
                    "Drop rate": f"{s['drop_rate']*100:.1f}%",
                    "Avg friction": s["avg_friction"],
                }
            )
        st.table(step_rows)

        # Persona summaries
        st.markdown("#### Persona outcomes")
        persona_rows = summary["persona_summaries"]
        st.table(persona_rows)

        # Optional: detailed logs
        with st.expander("See detailed persona journeys"):
            for run in runs:
                st.markdown(f"**{run.persona.name}**")
                st.write(run.persona.bio)
                for e in run.events:
                    step_name = next(s.name for s in steps if s.id == e.step_id)
                    st.markdown(f"- **{step_name}** → `{e.action}` (friction {e.friction})")
                    st.caption(e.reasoning)
                st.markdown("---")
else:
    st.info("Parse your flow and then click 'Generate personas and simulate' to run the simulation.")
