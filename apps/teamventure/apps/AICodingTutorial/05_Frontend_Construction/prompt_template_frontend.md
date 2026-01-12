# How to Generate Frontend Code (Prompt Template)

## Prompt Template

```markdown
# Context
1. @page_layouts_ascii.md (The Layout)
2. @design_tokens.json (The Style)
3. @component_mapping.md (File Structure)
4. @api_specification.yaml (Data Source)

# Task
Implement the **Session Detail Page** (`pages/session/detail`).

# Requirements
1. **WXML Structure**: Strictly follow the ASCII layout. Use Flexbox for alignment.
2. **Styling**: 
   - Use CSS Variables from `design_tokens.json` (e.g., `var(--brand-color)`).
   - Do NOT use hardcoded hex colors.
3. **Logic (JS/TS)**:
   - On `onLoad(options)`, fetch data using the API defined in YAML.
   - Implement the `MainAction` button logic as described in @interaction_flows.md.
   - Handle the "Waitlist" case specifically (show specific Modal).
```
