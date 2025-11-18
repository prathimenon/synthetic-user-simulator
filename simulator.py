from dataclasses import dataclass
from typing import List, Literal, Dict, Any, Optional
from openai import OpenAI
import os
import json

StepType = Literal["info", "decision", "form", "paywall", "cta"]
ActionType = Literal["continue", "hesitate", "drop"]

@dataclass
class Step:
    id: int
    name: str
    description: str
    type: StepType

@dataclass
class Persona:
    id: int
    name: str
    bio: str
    traits: List[str]
    tendencies: List[str]

@dataclass
class StepEvent:
    step_id: int
    action: ActionType
    friction: int  # 1-10
    reasoning: str

@dataclass
class SimulationRun:
    persona: Persona
    events: List[StepEvent]
    converted: bool
    drop_step_id: Optional[int]


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def generate_personas(flow_description: str, num_personas: int = 5) -> List[Persona]:
    client = get_client()
    system_msg = (
        "You are helping design synthetic user personas for UX testing. "
        "You create realistic but fictional users with varied motivations, "
        "attention spans, risk tolerance, tech savviness, and constraints."
    )
    user_prompt = f"""
Create {num_personas} distinct user personas for the following product flow.

Flow description:
{flow_description}

Return STRICT JSON in this format:

{{
  "personas": [
    {{
      "name": "string",
      "bio": "short paragraph",
      "traits": ["trait1", "trait2"],
      "tendencies": ["behavior1", "behavior2"]
    }},
    ...
  ]
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""

    start = content.find("{")
    end = content.rfind("}") + 1
    data = json.loads(content[start:end])

    personas = []
    for i, p in enumerate(data.get("personas", [])):
        personas.append(
            Persona(
                id=i,
                name=p.get("name", f"Persona {i+1}"),
                bio=p.get("bio", ""),
                traits=p.get("traits", []),
                tendencies=p.get("tendencies", []),
            )
        )
    return personas


def simulate_step(persona: Persona, step: Step) -> StepEvent:
    client = get_client()
    system_msg = (
        "You are simulating how a specific user behaves in a product flow. "
        "You must decide if they CONTINUE, HESITATE, or DROP at each step."
    )
    user_prompt = f"""
Persona:
Name: {persona.name}
Bio: {persona.bio}
Traits: {", ".join(persona.traits)}
Tendencies: {", ".join(persona.tendencies)}

Step:
Name: {step.name}
Type: {step.type}
Description: {step.description}

Answer with STRICT JSON in this format:

{{
  "action": "continue" | "hesitate" | "drop",
  "friction": 1-10,
  "reasoning": "one or two short sentences"
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    start = content.find("{")
    end = content.rfind("}") + 1
    data = json.loads(content[start:end])

    action = data.get("action", "continue")
    friction = int(data.get("friction", 5))
    friction = max(1, min(10, friction))
    reasoning = data.get("reasoning", "")

    return StepEvent(
        step_id=step.id,
        action=action,  # type: ignore
        friction=friction,
        reasoning=reasoning,
    )


def simulate_persona_through_flow(persona: Persona, steps: List[Step]) -> SimulationRun:
    events: List[StepEvent] = []
    drop_step_id: Optional[int] = None

    for step in steps:
        event = simulate_step(persona, step)
        events.append(event)
        if event.action == "drop":
            drop_step_id = step.id
            break

    converted = drop_step_id is None and len(steps) > 0
    return SimulationRun(
        persona=persona,
        events=events,
        converted=converted,
        drop_step_id=drop_step_id,
    )


def summarize_runs(runs: List[SimulationRun], steps: List[Step]) -> Dict[str, Any]:
    if not runs:
        return {"conversion_rate": 0.0, "step_stats": {}, "persona_summaries": []}

    n = len(runs)
    conversions = sum(1 for r in runs if r.converted)
    conversion_rate = conversions / n

    # step-level stats
    step_stats: Dict[int, Dict[str, Any]] = {}
    for step in steps:
        step_stats[step.id] = {
            "name": step.name,
            "views": 0,
            "drops": 0,
            "friction_scores": [],
        }

    for r in runs:
        for e in r.events:
            s = step_stats[e.step_id]
            s["views"] += 1
            s["friction_scores"].append(e.friction)
            if e.action == "drop":
                s["drops"] += 1

    for sid, s in step_stats.items():
        views = s["views"] or 1
        s["avg_friction"] = round(sum(s["friction_scores"]) / views, 2) if s["friction_scores"] else 0.0
        s["drop_rate"] = s["drops"] / views if views else 0.0

    persona_summaries = []
    for r in runs:
        persona_summaries.append(
            {
                "name": r.persona.name,
                "converted": r.converted,
                "drop_step": next(
                    (st.name for st in steps if st.id == r.drop_step_id),
                    None,
                ),
            }
        )

    return {
        "conversion_rate": conversion_rate,
        "step_stats": step_stats,
        "persona_summaries": persona_summaries,
    }
from dataclasses import dataclass
from typing import List, Literal, Dict, Any, Optional
from openai import OpenAI
import os
import json

StepType = Literal["info", "decision", "form", "paywall", "cta"]
ActionType = Literal["continue", "hesitate", "drop"]

@dataclass
class Step:
    id: int
    name: str
    description: str
    type: StepType

@dataclass
class Persona:
    id: int
    name: str
    bio: str
    traits: List[str]
    tendencies: List[str]

@dataclass
class StepEvent:
    step_id: int
    action: ActionType
    friction: int  # 1-10
    reasoning: str

@dataclass
class SimulationRun:
    persona: Persona
    events: List[StepEvent]
    converted: bool
    drop_step_id: Optional[int]


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def generate_personas(flow_description: str, num_personas: int = 5) -> List[Persona]:
    client = get_client()
    system_msg = (
        "You are helping design synthetic user personas for UX testing. "
        "You create realistic but fictional users with varied motivations, "
        "attention spans, risk tolerance, tech savviness, and constraints."
    )
    user_prompt = f"""
Create {num_personas} distinct user personas for the following product flow.

Flow description:
{flow_description}

Return STRICT JSON in this format:

{{
  "personas": [
    {{
      "name": "string",
      "bio": "short paragraph",
      "traits": ["trait1", "trait2"],
      "tendencies": ["behavior1", "behavior2"]
    }},
    ...
  ]
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""

    start = content.find("{")
    end = content.rfind("}") + 1
    data = json.loads(content[start:end])

    personas = []
    for i, p in enumerate(data.get("personas", [])):
        personas.append(
            Persona(
                id=i,
                name=p.get("name", f"Persona {i+1}"),
                bio=p.get("bio", ""),
                traits=p.get("traits", []),
                tendencies=p.get("tendencies", []),
            )
        )
    return personas


def simulate_step(persona: Persona, step: Step) -> StepEvent:
    client = get_client()
    system_msg = (
        "You are simulating how a specific user behaves in a product flow. "
        "You must decide if they CONTINUE, HESITATE, or DROP at each step."
    )
    user_prompt = f"""
Persona:
Name: {persona.name}
Bio: {persona.bio}
Traits: {", ".join(persona.traits)}
Tendencies: {", ".join(persona.tendencies)}

Step:
Name: {step.name}
Type: {step.type}
Description: {step.description}

Answer with STRICT JSON in this format:

{{
  "action": "continue" | "hesitate" | "drop",
  "friction": 1-10,
  "reasoning": "one or two short sentences"
}}
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    start = content.find("{")
    end = content.rfind("}") + 1
    data = json.loads(content[start:end])

    action = data.get("action", "continue")
    friction = int(data.get("friction", 5))
    friction = max(1, min(10, friction))
    reasoning = data.get("reasoning", "")

    return StepEvent(
        step_id=step.id,
        action=action,  # type: ignore
        friction=friction,
        reasoning=reasoning,
    )


def simulate_persona_through_flow(persona: Persona, steps: List[Step]) -> SimulationRun:
    events: List[StepEvent] = []
    drop_step_id: Optional[int] = None

    for step in steps:
        event = simulate_step(persona, step)
        events.append(event)
        if event.action == "drop":
            drop_step_id = step.id
            break

    converted = drop_step_id is None and len(steps) > 0
    return SimulationRun(
        persona=persona,
        events=events,
        converted=converted,
        drop_step_id=drop_step_id,
    )


def summarize_runs(runs: List[SimulationRun], steps: List[Step]) -> Dict[str, Any]:
    if not runs:
        return {"conversion_rate": 0.0, "step_stats": {}, "persona_summaries": []}

    n = len(runs)
    conversions = sum(1 for r in runs if r.converted)
    conversion_rate = conversions / n

    # step-level stats
    step_stats: Dict[int, Dict[str, Any]] = {}
    for step in steps:
        step_stats[step.id] = {
            "name": step.name,
            "views": 0,
            "drops": 0,
            "friction_scores": [],
        }

    for r in runs:
        for e in r.events:
            s = step_stats[e.step_id]
            s["views"] += 1
            s["friction_scores"].append(e.friction)
            if e.action == "drop":
                s["drops"] += 1

    for sid, s in step_stats.items():
        views = s["views"] or 1
        s["avg_friction"] = round(sum(s["friction_scores"]) / views, 2) if s["friction_scores"] else 0.0
        s["drop_rate"] = s["drops"] / views if views else 0.0

    persona_summaries = []
    for r in runs:
        persona_summaries.append(
            {
                "name": r.persona.name,
                "converted": r.converted,
                "drop_step": next(
                    (st.name for st in steps if st.id == r.drop_step_id),
                    None,
                ),
            }
        )

    return {
        "conversion_rate": conversion_rate,
        "step_stats": step_stats,
        "persona_summaries": persona_summaries,
    }
