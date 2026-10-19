# LangGraph Agent Tools (finalized)

All tools call the existing service functions. They never touch the database directly. Arguments with fixed values use Literal types, and tool results are short plain-text strings the LLM can read.

| # | Tool | Purpose | Service it uses |
|---|---|---|---|
| 1 | log_interaction | Resolve the HCP and products by name, validate with InteractionCreate, save with source "ai_chat" | interaction_service.create_interaction |
| 2 | edit_interaction | Change fields of an existing interaction through InteractionUpdate | interaction_service.update_interaction |
| 3 | search_hcp | Find HCPs by name, specialty, city or hospital | hcp_service.search_hcps |
| 4 | get_interaction_history | Return the rep's recent interactions with one HCP | interaction_service.list_interactions |
| 5 | schedule_followup | Add a follow-up with a due date to an existing interaction | new function in interaction_service |
| 6 (optional) | suggest_next_action | Suggest next steps from an HCP's history | LLM over get_interaction_history output |

## Rules
- The rep is always the logged-in user. The agent can never act for another rep.
- HCP names are resolved to ids inside the tool. Zero or multiple matches return a clarifying message, never a guess.
- If required details are missing, the agent asks the rep instead of inventing values.
- Tool errors (ServiceError, validation errors) are returned to the LLM as text so it can explain them to the rep.
- The agent loop has a maximum number of steps.