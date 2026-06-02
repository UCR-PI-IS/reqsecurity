from mcp.server.fastmcp import FastMCP
from models.Claude import Claude
from SecurityRequirementGenerator import SecurityRequirementGenerator
from constants import SYSTEM_PATTERN_PROMPT, USER_PATTERN_PROMPT, API_KEY, MCP_INSTRUCTIONS


# Nombre del servidor
mcp = FastMCP(
    name="Req2Seq", 
    instructions=MCP_INSTRUCTIONS,
    host="0.0.0.0",
    port=8000
)
model = Claude(
    api_key=API_KEY,
    model="claude-haiku-4-5-20251001",
    role=SYSTEM_PATTERN_PROMPT,
    temperature=0,
    top_k=0.5
)
generator = SecurityRequirementGenerator(model, USER_PATTERN_PROMPT)

# Tool simple
@mcp.tool()
def generate_security_requirements(context: str, functional_requirement: str) -> dict:
    """
    Generate security requirements based on a functional requirement.
    """
    return generator.generate(context, functional_requirement)["parsed_response"]
    

if __name__ == "__main__":
    mcp.run(transport="streamable-http")