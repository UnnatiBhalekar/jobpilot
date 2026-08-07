"""
parse_resume MCP tool.

Takes raw resume text (already extracted from PDF via a library like
pypdf or pdfplumber) and converts it into the structured, tagged JSON
format defined in schema/resume_schema.json.

This is an EXTRACTION task, not a generation task: the LLM is only
allowed to reformat what already exists in the source text. It must
never invent skills, tools, metrics, or experience that aren't
literally present.
"""

import json
import anthropic

from text_utils import fix_missing_spaces

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

EXTRACTION_PROMPT = """You are a precise resume-parsing assistant. Your ONLY job is to convert the raw resume text below into structured JSON. You are extracting, not writing.

STRICT RULES:
1. Do not add any skill, tool, technology, or claim that is not literally present in the source text. If something is implied but not stated, leave it out.
2. Every bullet's "text" field must be the original wording from the resume, unchanged (you may only fix obvious OCR typos).
3. For each bullet, add 3-6 lowercase kebab-case tags describing the skills/domains it demonstrates (e.g. "spring-boot", "aws", "security", "system-design"). Tags must be inferable directly from that bullet's own text.
4. If a field is missing or unclear in the source, use null. Never guess a value to fill a gap.
5. Output ONLY valid JSON matching the schema below. No preamble, no markdown code fences, no explanation.

SCHEMA:
{schema}

RESUME TEXT:
{resume_text}

Output the JSON now."""


def parse_resume(resume_text: str, schema_path: str = "../../schema/resume_schema.json") -> dict:
    with open(schema_path) as f:
        schema = json.load(f)

    prompt = EXTRACTION_PROMPT.format(
        schema=json.dumps(schema, indent=2),
        resume_text=resume_text
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return _clean_resume_text(json.loads(raw))


def _clean_resume_text(data: dict) -> dict:
    if data.get("summary"):
        data["summary"] = fix_missing_spaces(data["summary"])
    for exp in data.get("experience", []):
        for bullet in exp.get("bullets", []):
            bullet["text"] = fix_missing_spaces(bullet["text"])
    for proj in data.get("projects", []):
        for bullet in proj.get("bullets", []):
            bullet["text"] = fix_missing_spaces(bullet["text"])
    return data


TOOL_DEFINITION = {
    "name": "parse_resume",
    "description": "Extract raw resume text into structured, tagged JSON. Never invents claims not present in the source.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "resume_text": {
                "type": "string",
                "description": "Raw text extracted from the resume PDF"
            }
        },
        "required": ["resume_text"]
    }
}

if __name__ == "__main__":
    with open("../../data/sample_resume.txt") as f:
        text = f.read()
    result = parse_resume(text)
    print(json.dumps(result, indent=2))
