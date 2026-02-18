"""
Tool to append a new Interest entry to my_interests.md (source of truth for user context).
"""
from pathlib import Path
from typing import Type

from pydantic import BaseModel, Field

from crewai.tools import BaseTool

DEFAULT_INTERESTS_PATH = Path(__file__).resolve().parent.parent / "my_interests.md"


class AppendInterestsToolInput(BaseModel):
    """Input schema for AppendInterestsTool."""

    interest_line: str = Field(
        ...,
        description="One concise line describing a new interest or area to learn, e.g. 'Domain-driven design' or 'Climate tech investing'"
    )


class AppendInterestsTool(BaseTool):
    """Appends a new bullet under '## Interests' in my_interests.md. Use when the research subject has expertise the user does not yet have and should add to their interests."""

    name: str = "Append to My Interests"
    description: str = (
        "Appends a new interest entry to the user's my_interests.md file. "
        "Use only when the person researched has an expertise or area that the user does not yet have "
        "and that would be valuable to add to the user's interests. Pass a single concise line (e.g. 'Climate tech' or 'Product-led growth')."
    )
    args_schema: Type[BaseModel] = AppendInterestsToolInput
    file_path: Path = DEFAULT_INTERESTS_PATH

    def _run(self, interest_line: str) -> str:
        path = self.file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        content = interest_line.strip()
        if not content:
            return "No content to append."
        new_line = f"- {content}\n"
        try:
            existing = path.read_text(encoding="utf-8")
            # Ensure there is an "## Interests" section
            if "## Interests" not in existing:
                existing += "\n## Interests\n"
            # Insert after the first "## Interests" block (after first newline)
            marker = "## Interests"
            idx = existing.find(marker)
            if idx == -1:
                existing += "\n## Interests\n" + new_line
            else:
                # Find end of line after "## Interests"
                line_end = existing.find("\n", idx) + 1
                insert_pos = line_end
                # Optionally find last bullet under Interests (before next ##)
                next_section = existing.find("\n## ", line_end)
                if next_section == -1:
                    insert_pos = len(existing)
                else:
                    insert_pos = next_section
                existing = existing[:insert_pos] + new_line + existing[insert_pos:]
            path.write_text(existing, encoding="utf-8")
            return f"Appended interest: {content}"
        except Exception as e:
            return f"Failed to append to my_interests.md: {e}"
