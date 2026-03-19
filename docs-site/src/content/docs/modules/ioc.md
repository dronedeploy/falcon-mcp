---
title: IOC
description: Search, create, and remove custom indicators of compromise.
---

# IOC Module

Search, create, and remove custom indicators of compromise.

## API Scopes

- `IOC Management:read`
- `IOC Management:write`

## Tools

### `falcon_add_ioc`

:::note
This tool modifies data.
:::

**Required scopes:** `IOC Management:write`

Create one or more custom IOCs.

**Example prompts:**

- "Block the domain evil.example.com"
- "Add a SHA256 hash IOC with prevent action"

### `falcon_remove_iocs`

:::caution
This tool performs destructive operations.
:::

**Required scopes:** `IOC Management:write`

Remove custom IOCs by IDs or FQL filter.

**Example prompts:**

- "Delete IOC with ID abc123"
- "Remove all expired IOCs"

### `falcon_search_iocs`

**Required scopes:** `IOC Management:read`

Search custom IOCs and return full IOC details.

**Example prompts:**

- "Find all active domain IOCs"
- "Show me SHA256 hash IOCs with prevent action"

## Resources

- **`falcon://ioc/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_iocs` tool.
