"""
Shared text-cleanup utilities for MCP tools.

Fixes a recurring PDF-extraction artifact: pypdf sometimes drops the
space between two words that were visually adjacent but on different
text-rendering runs in the PDF (e.g. "experienceapplying" instead of
"experience applying"). The naive fix — insert a space wherever a
lowercase letter is followed by an uppercase letter — would incorrectly
break real compound terms like "GitHub" or "LinkedIn", so those are
protected first.
"""

import re

# Known intentional camelCase / compound terms that must NOT be split.
# Extend this list as you encounter more false positives.
PROTECTED_TERMS = [
    "GitHub", "LinkedIn", "JavaScript", "TypeScript", "OAuth2", "OAuth",
    "DevOps", "PowerShell", "OpenID", "MacBook", "iOS", "GraphQL",
    "PostgreSQL", "MongoDB", "NodeJS", "ReactJS", "VueJS", "JetBrains",
    "WordPress", "YouTube", "PayPal", "eBay", "iPhone", "AppSecSentinel",
    "SonarCloud",
]


def fix_missing_spaces(text: str) -> str:
    if not text:
        return text

    # Temporarily swap protected terms for placeholders so the regex
    # below can't touch them.
    placeholders = {}
    working = text
    for i, term in enumerate(PROTECTED_TERMS):
        token = f"@@{i}@@"
        if term in working:
            placeholders[token] = term
            working = working.replace(term, token)

    # Insert a space wherever a lowercase letter is immediately followed
    # by an uppercase letter with no existing space between them.
    working = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', working)

    # Restore the protected terms.
    for token, term in placeholders.items():
        working = working.replace(token, term)

    return working
