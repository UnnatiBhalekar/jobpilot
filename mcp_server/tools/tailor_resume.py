"""
tailor_resume MCP tool.

Takes a structured resume (from parse_resume) plus a job description,
and returns a SELECTION: which bullet IDs are most relevant to this JD,
ranked, with brief reasoning. It does NOT rewrite bullet text and does
NOT invent new content — the actual resume text always comes from the
stored structured data, never from this tool's output.
"""

import json
import anthropic

client = anthropic.Anthropic()

TAILOR_PROMPT = """You are a resume-tailoring assistant. You will be given a candidate's full structured resume (as JSON) and a job description. Your job is to SELECT and RANK the existing bullets that are most relevant to this job — you do not write new bullets or alter their wording.

STRICT RULES:
1. You may only reference bullet IDs that already exist in the provided resume JSON. Never invent an ID.
2. Do not alter, rephrase, or summarize any bullet's text. Your output is IDs and reasoning only, never the bullet text itself.
3. For each experience/project section, rank its bullets by relevance to the JD — most relevant first. Do not silently drop a section entirely unless it has zero relevance.
4. Also return a short list of skills from the resume's "skills" section that best match the JD, again referencing existing category/skill_name pairs only.
5. Output ONLY valid JSON in this exact shape, no preamble, no markdown fences:

{{
  "match_summary": "2-3 sentence honest assessment of fit, including any real gaps",
  "ranked_bullet_ids": ["bullet-id-1", "bullet-id-2", ...],
  "relevant_skills": ["skill name 1", "skill name 2", ...]
}}

RESUME JSON:
{resume_json}

JOB DESCRIPTION:
{job_description}

Output the JSON now."""


def tailor_resume(resume_data: dict, job_description: str) -> dict:
    prompt = TAILOR_PROMPT.format(
        resume_json=json.dumps(resume_data, indent=2),
        job_description=job_description
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)

    # Defensive check: confirm every returned ID actually exists in the
    # source resume. If the model ever invents an ID despite the prompt,
    # we catch it here rather than silently rendering a broken resume.
    valid_ids = _collect_all_bullet_ids(resume_data)
    invalid = [bid for bid in result["ranked_bullet_ids"] if bid not in valid_ids]
    if invalid:
        raise ValueError(f"Model returned bullet IDs not present in source resume: {invalid}")

    return result


def _collect_all_bullet_ids(resume_data: dict) -> set:
    ids = set()
    for exp in resume_data.get("experience", []):
        for bullet in exp.get("bullets", []):
            ids.add(bullet["id"])
    for proj in resume_data.get("projects", []):
        for bullet in proj.get("bullets", []):
            ids.add(bullet["id"])
    return ids


TOOL_DEFINITION = {
    "name": "tailor_resume",
    "description": "Given a structured resume and a job description, select and rank the most relevant existing bullets and skills. Never invents content.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "resume_data": {"type": "object", "description": "Structured resume JSON from parse_resume"},
            "job_description": {"type": "string"}
        },
        "required": ["resume_data", "job_description"]
    }
}

if __name__ == "__main__":
    with open("../../data/parsed_resume_reviewed.json") as f:
        resume = json.load(f)

    with open("../../data/sample_jd.txt") as f:
        jd = f.read()

    result = tailor_resume(resume, jd)
    print(json.dumps(result, indent=2))
