import re
import json
from mcp.server.fastmcp import FastMCP
import os

from dotenv import load_dotenv
load_dotenv()


EXAMPLES = {
    "welcome": "Welcome to the test MCP server. This example resource is static text.",
    "tools": "Tools are callable functions. Use them when the client wants an action or computation.",
    "prompts": "Prompts are reusable instruction templates. We will add them in the next phase.",
}

mcp = FastMCP(
    name="test_mcp_server",
    instructions=(
        "This is a small learning MCP server. Use its tools for simple deterministic "
        "text and math demos. Do not assume it has external network or database access."
    ),
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("MCP_PORT", 8000)),
)

@mcp.tool()
def add(a:float, b:float) -> float:
    """Add two numbers."""
    return a + b

@mcp.tool()
def word_count(text: str) -> dict[str, int]:
    """Count words, characters, non-space characters, and lines in text."""
    words = re.findall(r"\b\w+\b", text)
    return {
        "words": len(words),
        "characters": len(text),
        "characters_no_spaces": len(text.replace(" ", "")),
        "lines": len(text.splitlines()) or 1,
    }


@mcp.tool()
def slugify(text: str) -> str:
    """Convert text into a lowercase URL-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug or "empty"


@mcp.tool()
def summarize_notes(notes: str, max_bullets: int = 5) -> list[str]:
    """Create a simple deterministic bullet summary from rough notes."""
    if max_bullets < 1:
        max_bullets = 1
    if max_bullets > 10:
        max_bullets = 10

    parts = re.split(r"[.\n;]+", notes)
    bullets = [part.strip() for part in parts if part.strip()]
    return bullets[:max_bullets]

@mcp.resource("demo://about")
def about() -> str:
    """Describe what this demo MCP server exposes."""
    return (
        "This is a small FastMCP learning server. It exposes simple tools for "
        "math and text processing, plus resources that clients can read as context."
    )


@mcp.resource("demo://config")
def config() -> str:
    """Return basic server configuration as JSON text."""
    return json.dumps(
        {
            "name": "test-mcp-server",
            "transport": "stdio",
            "features": ["tools", "resources", "prompts"],
            "external_access": False,
        },
        indent=2,
    )

@mcp.resource("demo://examples/{name}")
def example(name: str) -> str:
    """Return an allow-listed example resource by name."""
    if name not in EXAMPLES:
        allowed = ", ".join(sorted(EXAMPLES))
        raise ValueError(f"Unknown example '{name}'. Allowed examples: {allowed}.")

    return EXAMPLES[name]

@mcp.prompt()
def explain_text(text: str, audience: str = "beginner") -> str:
    """Create a prompt for explaining text to a target audience."""
    return (
        f"Explain the following text for a {audience} audience.\n\n"
        f"Text:\n{text}\n\n"
        "Keep the explanation clear, practical, and concise."
    )


@mcp.prompt()
def review_notes(notes: str) -> str:
    """Create a prompt for reviewing rough notes."""
    return (
        "Review these rough notes and turn them into useful feedback.\n\n"
        f"Notes:\n{notes}\n\n"
        "Return:\n"
        "- Key ideas\n"
        "- Confusing parts\n"
        "- Suggested improvements"
    )


@mcp.prompt()
def tool_choice_practice(task: str) -> str:
    """Create a prompt for deciding whether to use a tool, resource, or prompt."""
    return (
        "Given this task, decide whether an MCP tool, resource, or prompt is most appropriate.\n\n"
        f"Task:\n{task}\n\n"
        "Answer with:\n"
        "- Best MCP capability type\n"
        "- Why\n"
        "- What input/resource URI would be used"
    )

def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()