---
title: API Credentials
description: Create and configure CrowdStrike API credentials for the Falcon MCP Server.
---

Before using the Falcon MCP Server, you need to create API credentials in your CrowdStrike console.

## Creating API Credentials

1. **Log into your CrowdStrike console**
2. **Navigate to Support > API Clients and Keys**
3. **Click "Add new API client"**
4. **Configure your API client**:
   - **Client Name**: Choose a descriptive name (e.g., "Falcon MCP Server")
   - **Description**: Optional description for your records
   - **API Scopes**: Select the scopes based on which modules you plan to use

:::caution
Ensure your API client has the necessary scopes for the modules you plan to use. You can always update scopes later in the CrowdStrike console.
:::

## Required API Scopes by Module

| Module | Required API Scopes | Purpose |
|--------|-------------------|---------|
| **Cloud Security** | `Falcon Container Image:read`, `Cloud Security API Assets:Read` | Kubernetes containers, image vulnerabilities, and CSPM asset inventory |
| **Core** | _No additional scopes_ | Basic connectivity and system information |
| **Custom IOA** | `Custom IOA Rules:read`, `Custom IOA Rules:write` | Create and manage Custom IOA behavioral detection rules |
| **Detections** | `Alerts:read` | Find and analyze detections |
| **Discover** | `Assets:read` | Search application inventory |
| **Hosts** | `Hosts:read` | Manage and query host/device information |
| **Identity Protection** | `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection Detections:read`, `Identity Protection Assessment:read`, `Identity Protection GraphQL:write` | Entity investigation and identity protection |
| **Incidents** | `Incidents:read` | Analyze security incidents |
| **NGSIEM** | `NGSIEM:read`, `NGSIEM:write` | Execute CQL queries against Next-Gen SIEM |
| **Intel** | `Actors (Falcon Intelligence):read`, `Indicators (Falcon Intelligence):read`, `Reports (Falcon Intelligence):read` | Threat actors, IOCs, and intelligence reports |
| **IOC** | `IOC Management:read`, `IOC Management:write` | Search, create, and remove custom IOCs |
| **Firewall Management** | `Firewall Management:read`, `Firewall Management:write` | Search and manage firewall rules |
| **Scheduled Reports** | `Scheduled Reports:read` | Manage and download scheduled reports |
| **Sensor Usage** | `Sensor Usage:read` | Sensor usage data |
| **Serverless** | `Falcon Container Image:read` | Serverless function vulnerabilities |
| **Spotlight** | `Vulnerabilities:read` | Vulnerability data and assessments |

## API Region URLs

Select the correct base URL for your CrowdStrike region:

| Region | URL |
|--------|-----|
| US-1 (Default) | `https://api.crowdstrike.com` |
| US-2 | `https://api.us-2.crowdstrike.com` |
| EU-1 | `https://api.eu-1.crowdstrike.com` |
| US-GOV | `https://api.laggar.gcw.crowdstrike.com` |
