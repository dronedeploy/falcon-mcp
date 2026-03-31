---
title: Module Overview
description: Overview of all available Falcon MCP modules with API scopes.
---

The Falcon MCP Server provides the following modules. Each module requires specific CrowdStrike API scopes.

| Module | API Scopes | Description |
|--------|-------------------|-------------|
| [Cloud Security](/falcon-mcp/modules/cloud/) | `Cloud Security API Assets:read`, `Falcon Container Image:read` | Find and analyze Kubernetes containers, container image vulnerabilities, and CSPM cloud asset inventory. |
| [Custom IOA](/falcon-mcp/modules/custom-ioa/) | `Custom IOA Rules:read`, `Custom IOA Rules:write` | Create and manage Custom IOA behavioral detection rules and rule groups. |
| [Detections](/falcon-mcp/modules/detections/) | `Alerts:read` | Find and analyze detections to understand malicious activity in your environment. |
| [Discover](/falcon-mcp/modules/discover/) | `Assets:read` | Search and analyze application inventory and unmanaged assets across your environment. |
| [Firewall Management](/falcon-mcp/modules/firewall/) | `Firewall Management:read`, `Firewall Management:write` | Search and manage Falcon firewall rules and rule groups. |
| [Hosts](/falcon-mcp/modules/hosts/) | `Hosts:read` | Manage and query host/device information across your CrowdStrike environment. |
| [Identity Protection](/falcon-mcp/modules/idp/) | `Identity Protection Assessment:read`, `Identity Protection Detections:read`, `Identity Protection Entities:read`, `Identity Protection Timeline:read`, `Identity Protection GraphQL:write` | Comprehensive entity investigation and identity protection analysis. |
| [Incidents](/falcon-mcp/modules/incidents/) | `Incidents:read` | Analyze security incidents, behaviors, and coordinated activities. |
| [Intel](/falcon-mcp/modules/intel/) | `Actors (Falcon Intelligence):read`, `Indicators (Falcon Intelligence):read`, `Reports (Falcon Intelligence):read` | Research threat actors, IOCs, and intelligence reports. |
| [IOC](/falcon-mcp/modules/ioc/) | `IOC Management:read`, `IOC Management:write` | Search, create, and remove custom indicators of compromise. |
| [NGSIEM](/falcon-mcp/modules/ngsiem/) | `NGSIEM:read`, `NGSIEM:write` | Execute CQL queries against CrowdStrike Next-Gen SIEM. |
| [Scheduled Reports](/falcon-mcp/modules/scheduled-reports/) | `Scheduled Reports:read` | Manage scheduled reports and searches, run on demand, and download results. |
| [Sensor Usage](/falcon-mcp/modules/sensor-usage/) | `Sensor Usage:read` | Access and analyze sensor usage data. |
| [Serverless](/falcon-mcp/modules/serverless/) | `Falcon Container Image:read` | Search for vulnerabilities in serverless functions across cloud providers. |
| [Spotlight](/falcon-mcp/modules/spotlight/) | `Vulnerabilities:read` | Manage and analyze vulnerability data and security assessments. |
