"""
draft_cover_letter MCP tool.

Takes the candidate's structured resume, the tailor_resume output
(ranked bullets + match summary), and a job description, and drafts
a cover letter grounded strictly in the tailored facts.

Unlike parse_resume and tailor_resume, this tool genuinely generates
prose — there's no fixed ID list to validate against. Groundedness is
enforced through prompt constraints instead: the model is only given
the SELECTED bullets (not the full resume) and told explicitly not to
invent achievements, metrics, or claims beyond what's provided.
"""

import json
import anthropic

from text_utils import fix_missing_spaces

client = anthropic.Anthropic()

COVER_LETTER_PROMPT = """You are a cover letter writing assistant. Write a concise, honest, humanised cover letter for the candidate below, tailored to the job description.

STRICT RULES:
1. Only reference achievements, skills, and experience present in the SELECTED BULLETS and RELEVANT SKILLS provided below. Do not invent metrics, outcomes, or experience not stated there.
2. Do not claim expertise in any technology only mentioned in the job description but absent from the candidate's provided facts. If there's a genuine gap, do not paper over it with vague language ("familiar with", "exposure to") unless the source facts actually support that framing.
3. Tone: measured and matter-of-fact, like explaining your actual fit to a colleague, not selling yourself. Avoid hype and superlatives ("exactly", "perfect fit", "thrilled", "excited", "passionate"), corporate cliches ("synergy", "dynamic self-starter"), and em dashes. State genuine interest plainly once, without dramatizing it.
4. Length: 250-350 words, 3-4 paragraphs. No placeholder brackets like [Company Name] — use the real company name from the job description.
5. Output ONLY the cover letter text. No preamble, no explanation, no markdown formatting.

CANDIDATE NAME: {name}

SELECTED BULLETS (use only these facts, do not pull from elsewhere):
{selected_bullets}

RELEVANT SKILLS:
{relevant_skills}

MATCH SUMMARY (for your context on honest framing, including known gaps):
{match_summary}

JOB DESCRIPTION:
{job_description}

Write the cover letter now."""


def draft_cover_letter(resume_data: dict, tailor_result: dict, job_description: str) -> str:
    bullet_lookup = _build_bullet_lookup(resume_data)
    selected_bullets_text = "\n".join(
        f"- {bullet_lookup[bid]}"
        for bid in tailor_result["ranked_bullet_ids"]
        if bid in bullet_lookup
    )

    prompt = COVER_LETTER_PROMPT.format(
        name=resume_data["personal"]["name"],
        selected_bullets=selected_bullets_text,
        relevant_skills=", ".join(tailor_result["relevant_skills"]),
        match_summary=tailor_result["match_summary"],
        job_description=job_description
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    return fix_missing_spaces(response.content[0].text.strip())


def _build_bullet_lookup(resume_data: dict) -> dict:
    lookup = {}
    for exp in resume_data.get("experience", []):
        for bullet in exp.get("bullets", []):
            lookup[bullet["id"]] = bullet["text"]
    for proj in resume_data.get("projects", []):
        for bullet in proj.get("bullets", []):
            lookup[bullet["id"]] = bullet["text"]
    return lookup


TOOL_DEFINITION = {
    "name": "draft_cover_letter",
    "description": "Draft a cover letter grounded strictly in the tailored/selected resume facts for a given job description.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "resume_data": {"type": "object"},
            "tailor_result": {"type": "object", "description": "Output from tailor_resume"},
            "job_description": {"type": "string"}
        },
        "required": ["resume_data", "tailor_result", "job_description"]
    }
}

if __name__ == "__main__":
    from tailor_resume import tailor_resume

    with open("../../data/parsed_resume_reviewed.json") as f:
        resume = json.load(f)
    with open("../../data/sample_jd.txt") as f:
        jd = f.read()

    tailor_result = tailor_resume(resume, jd)
    letter = draft_cover_letter(resume, tailor_result, jd)
    print(letter)
