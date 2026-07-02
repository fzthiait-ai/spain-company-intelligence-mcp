# Spain Company Intelligence MCP

Search 2.8 million Spanish companies from the official BORME registry directly from any AI agent.

**No API key required.** Data from [openmercantil.es](https://openmercantil.es) and the official [BOE/BORME](https://www.boe.es) — public domain (CC BY 4.0).

## Tools

- **buscar_empresa** — Search companies by name or CIF/NIF tax ID
- **perfil_empresa** — Full company profile: address, capital, SIC code, registration date
- **directivos_empresa** — Current directors and officers with appointment dates
- **actos_empresa** — Corporate acts history: incorporations, capital changes, dissolutions
- **buscar_persona** — Find all companies where a person appears as director

## Example queries

- "Search for Spanish companies named Inditex"
- "Who are the directors of Mercadona?"
- "Show me the corporate acts for company slug mercadona-sa"
- "Find all companies where Juan García López is a director"
- "What is the registered address and capital of Telefónica?"

## Data coverage

- 2.8 million registered Spanish companies
- Directors and officers with appointment/resignation dates
- Corporate acts from the official BORME
- Registered address, capital, legal form, activity code (CNAE)
- Active and dissolved companies

---
## Install & Access
**Smithery** — works with Claude, Cursor, Windsurf, and all MCP clients:
```bash
npx -y @smithery/cli install @fzth-ia-it/spain-company-intelligence-mcp --client claude
```
[![Smithery](https://smithery.ai/badge/@fzth-ia-it/spain-company-intelligence-mcp)](https://smithery.ai/server/@fzth-ia-it/spain-company-intelligence-mcp)

**MCPize** — hosted, managed access with Free / PRO / ULTRA tiers:  
[mcpize.com](https://mcpize.com) → search `Spain Company Intelligence MCP`

**REST API** — prefer HTTP over MCP?  
[Spain BORME Company Registry API](https://rapidapi.com/ilozanoit/api/spain-borme-company-registry) on RapidAPI
