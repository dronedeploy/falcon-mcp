---
title: Hosts
description: Manage and query host/device information across your CrowdStrike environment.
---

Manage and query host/device information across your CrowdStrike environment.

## API Scopes

- `Hosts:read`

## Tools

### `falcon_get_host_details`

**Required scopes:** `Hosts:read`

Retrieve detailed information for specified host device IDs.

This tool returns comprehensive host details for one or more device IDs.
Use this when you already have specific device IDs and need their full details.
For searching/discovering hosts, use the `falcon_search_hosts` tool instead.

**Example prompts:**

- "Get the full details for host device abc123"

### `falcon_search_hosts`

**Required scopes:** `Hosts:read`

Search for hosts in your CrowdStrike environment.

**Example prompts:**

- "Find all Windows hosts in my environment"
- "Show me hosts last seen in the past 24 hours"

## Resources

- **`falcon://hosts/search/fql-guide`**: Contains the guide for the `filter` param of the `falcon_search_hosts` tool.
