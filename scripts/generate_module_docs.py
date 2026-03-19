"""Generate Starlight documentation pages from falcon_mcp module source code.

Introspects module classes, tool methods, and resource definitions to produce
markdown files for docs-site/src/content/docs/modules/.

Usage:
    uv run python scripts/generate_module_docs.py
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import re
import sys
from pathlib import Path
from typing import Any

from falcon_mcp.common.api_scopes import API_SCOPE_REQUIREMENTS


# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_DIR = PROJECT_ROOT / "docs-site" / "src" / "content" / "docs" / "modules"

# Module display metadata (scopes are derived from api_scopes.py automatically)
MODULE_METADATA: dict[str, dict[str, Any]] = {
    "cloud": {
        "title": "Cloud Security",
        "description": "Find and analyze Kubernetes containers, container image vulnerabilities, and CSPM cloud asset inventory.",
    },
    "customioa": {
        "title": "Custom IOA",
        "slug": "custom-ioa",
        "description": "Create and manage Custom IOA behavioral detection rules and rule groups.",
    },
    "detections": {
        "title": "Detections",
        "description": "Find and analyze detections to understand malicious activity in your environment.",
    },
    "discover": {
        "title": "Discover",
        "description": "Search and analyze application inventory and unmanaged assets across your environment.",
    },
    "firewall": {
        "title": "Firewall Management",
        "description": "Search and manage Falcon firewall rules and rule groups.",
    },
    "hosts": {
        "title": "Hosts",
        "description": "Manage and query host/device information across your CrowdStrike environment.",
    },
    "idp": {
        "title": "Identity Protection",
        "description": "Comprehensive entity investigation and identity protection analysis.",
    },
    "incidents": {
        "title": "Incidents",
        "description": "Analyze security incidents, behaviors, and coordinated activities.",
    },
    "intel": {
        "title": "Intel",
        "description": "Research threat actors, IOCs, and intelligence reports.",
    },
    "ioc": {
        "title": "IOC",
        "description": "Search, create, and remove custom indicators of compromise.",
    },
    "ngsiem": {
        "title": "NGSIEM",
        "description": "Execute CQL queries against CrowdStrike Next-Gen SIEM.",
    },
    "scheduledreports": {
        "title": "Scheduled Reports",
        "slug": "scheduled-reports",
        "description": "Manage scheduled reports and searches, run on demand, and download results.",
    },
    "sensorusage": {
        "title": "Sensor Usage",
        "slug": "sensor-usage",
        "description": "Access and analyze sensor usage data.",
    },
    "serverless": {
        "title": "Serverless",
        "description": "Search for vulnerabilities in serverless functions across cloud providers.",
    },
    "spotlight": {
        "title": "Spotlight",
        "description": "Manage and analyze vulnerability data and security assessments.",
    },
}

# Natural language prompt examples for each tool, shown in generated docs
TOOL_EXAMPLES: dict[str, list[str]] = {
    # Cloud
    "falcon_search_kubernetes_containers": [
        "Find all containers running in AWS clusters",
        "Show me containers in the prod cluster",
    ],
    "falcon_count_kubernetes_containers": [
        "How many containers are running in Azure?",
    ],
    "falcon_search_images_vulnerabilities": [
        "Find image vulnerabilities with CVSS score above 7",
    ],
    "falcon_search_cspm_assets": [
        "Find all AWS EC2 instances in my cloud inventory",
    ],
    # Custom IOA
    "falcon_search_ioa_rule_groups": [
        "Find enabled Windows Custom IOA rule groups",
    ],
    "falcon_get_ioa_platforms": [
        "What platforms are available for Custom IOA rule groups?",
    ],
    "falcon_get_ioa_rule_types": [
        "What Custom IOA rule types are available?",
    ],
    "falcon_create_ioa_rule_group": [
        "Create a Windows IOA rule group named 'Suspicious PowerShell Activity'",
    ],
    "falcon_update_ioa_rule_group": [
        "Disable IOA rule group abc123",
    ],
    "falcon_delete_ioa_rule_groups": [
        "Delete Custom IOA rule groups abc123 and def456",
    ],
    "falcon_create_ioa_rule": [
        "Add a process creation rule to IOA group abc123 that detects cmd.exe spawned from Word",
    ],
    "falcon_update_ioa_rule": [
        "Enable IOA rule instance abc in group xyz",
    ],
    "falcon_delete_ioa_rules": [
        "Delete rules from IOA group abc123",
    ],
    # Detections
    "falcon_search_detections": [
        "Show me new high severity detections from the last 7 days",
        "Find all unassigned critical detections",
    ],
    "falcon_get_detection_details": [
        "Get me the details for this detection",
    ],
    # Discover
    "falcon_search_applications": [
        "Find all Chrome installations across my environment",
    ],
    "falcon_search_unmanaged_assets": [
        "Show me unmanaged Windows devices on the network",
    ],
    # Firewall
    "falcon_search_firewall_rules": [
        "Show me all enabled Windows firewall rules",
        "Find firewall rules matching 'outbound'",
    ],
    "falcon_search_firewall_rule_groups": [
        "Find all enabled firewall rule groups for Windows",
    ],
    "falcon_search_firewall_policy_rules": [
        "Show me all rules in firewall policy abc123",
    ],
    "falcon_create_firewall_rule_group": [
        "Create a Windows firewall rule group named 'Prod Outbound'",
    ],
    "falcon_delete_firewall_rule_groups": [
        "Delete firewall rule group abc123",
    ],
    # Hosts
    "falcon_search_hosts": [
        "Find all Windows hosts in my environment",
        "Show me hosts last seen in the past 24 hours",
    ],
    "falcon_get_host_details": [
        "Get the full details for host device abc123",
    ],
    # Identity Protection
    "falcon_idp_investigate_entity": [
        "Investigate user john.doe@company.com and show their risk assessment",
        "Look up entity Administrator in domain CORP.LOCAL",
    ],
    # Incidents
    "falcon_search_incidents": [
        "Find all open high-severity incidents",
        "Show me incidents from the past week",
    ],
    "falcon_get_incident_details": [
        "Get details for incident inc:abc123",
    ],
    "falcon_show_crowd_score": [
        "Show me the current CrowdScore for my environment",
    ],
    "falcon_search_behaviors": [
        "Find behaviors associated with lateral movement",
    ],
    "falcon_get_behavior_details": [
        "Get details for behavior behav:abc123",
    ],
    # Intel
    "falcon_search_actors": [
        "Find threat actors targeting financial services",
        "Search for BEAR adversary groups",
    ],
    "falcon_search_indicators": [
        "Find intelligence IOCs of type domain published this year",
    ],
    "falcon_search_reports": [
        "Find intelligence reports published in the last 30 days",
    ],
    "falcon_get_mitre_report": [
        "Generate MITRE ATT&CK report for FANCY BEAR",
    ],
    # IOC
    "falcon_search_iocs": [
        "Find all active domain IOCs",
        "Show me SHA256 hash IOCs with prevent action",
    ],
    "falcon_add_ioc": [
        "Block the domain evil.example.com",
        "Add a SHA256 hash IOC with prevent action",
    ],
    "falcon_remove_iocs": [
        "Delete IOC with ID abc123",
        "Remove all expired IOCs",
    ],
    # NGSIEM
    "falcon_search_ngsiem": [
        "Run this CQL query for the last 24 hours: #event_simpleName=ProcessRollup2",
        "Search NGSIEM for DNS events from January 2025",
    ],
    # Scheduled Reports
    "falcon_search_scheduled_reports": [
        "Show me all active scheduled reports",
    ],
    "falcon_launch_scheduled_report": [
        "Run scheduled report abc123 now",
    ],
    "falcon_search_report_executions": [
        "Show me completed executions for report abc123",
    ],
    "falcon_download_report_execution": [
        "Download the results for report execution abc123",
    ],
    # Sensor Usage
    "falcon_search_sensor_usage": [
        "Show me sensor usage data for the week of 2024-06-11",
    ],
    # Serverless
    "falcon_search_serverless_vulnerabilities": [
        "Find HIGH severity vulnerabilities in AWS Lambda functions",
    ],
    # Spotlight
    "falcon_search_vulnerabilities": [
        "Show me open HIGH severity vulnerabilities",
        "Find vulnerabilities on host xyz",
    ],
}

# Lines matching these patterns are stripped from docstrings
_DOCSTRING_NOISE_PATTERNS = [
    re.compile(r"^\s*IMPORTANT:\s*You must use the\b", re.IGNORECASE),
    re.compile(r"^\s*IMPORTANT:\s*use the\b", re.IGNORECASE),
    re.compile(r"^\s*This resource contains the guide\b", re.IGNORECASE),
    re.compile(r"^\s*Returns FQL syntax guide on error\b", re.IGNORECASE),
    re.compile(r"^\s*when you need to use the\b", re.IGNORECASE),
]


def clean_docstring(doc: str) -> str:
    """Strip noise sentences from a tool docstring."""
    lines = doc.splitlines()
    cleaned: list[str] = []
    for line in lines:
        if any(p.match(line) for p in _DOCSTRING_NOISE_PATTERNS):
            continue
        cleaned.append(line)

    # Collapse consecutive blank lines
    result: list[str] = []
    prev_blank = False
    for line in cleaned:
        is_blank = line.strip() == ""
        if is_blank and prev_blank:
            continue
        result.append(line)
        prev_blank = is_blank

    return "\n".join(result).strip()


def discover_module_classes() -> dict[str, type]:
    """Discover all module classes using the same logic as the registry."""
    modules_path = str(PROJECT_ROOT / "falcon_mcp" / "modules")
    result = {}

    for _, name, is_pkg in pkgutil.iter_modules([modules_path]):
        if is_pkg or name == "base":
            continue
        mod = importlib.import_module(f"falcon_mcp.modules.{name}")
        for attr_name in dir(mod):
            if attr_name.endswith("Module") and attr_name != "BaseModule":
                cls = getattr(mod, attr_name)
                module_key = attr_name.lower().replace("module", "")
                result[module_key] = cls

    return result


def extract_module_scopes(module_cls: type) -> list[str]:
    """Derive API scopes by finding operation names in module source and looking them up in API_SCOPE_REQUIREMENTS."""
    source = inspect.getsource(module_cls)

    # Find all string literals that match known operation names
    all_strings = set(re.findall(r'["\'](\w+)["\']', source))
    scopes: set[str] = set()
    for op_name, op_scopes in API_SCOPE_REQUIREMENTS.items():
        if op_name in all_strings:
            scopes.update(op_scopes)

    # Sort: read scopes first, then write, alphabetically within each group
    return sorted(scopes, key=lambda s: (":write" in s, s))


def extract_tool_scopes(method: Any, module_cls: type) -> list[str]:
    """Derive API scopes for a single tool method by tracing its helper calls.

    Only follows private helpers defined on the concrete module class itself,
    NOT inherited BaseModule helpers (which contain operation names from all modules).
    """
    try:
        method_source = inspect.getsource(method)
    except (TypeError, OSError):
        return []

    # Collect combined source: the method itself + own-class private helpers it calls
    combined_source = method_source

    # Only trace helpers defined directly on this class (not inherited from BaseModule)
    own_methods = set(module_cls.__dict__.keys())

    # Find private helper calls: self._something(
    helper_names = re.findall(r'self\.(_\w+)\(', method_source)
    for helper_name in helper_names:
        if helper_name in own_methods:
            helper = module_cls.__dict__[helper_name]
            if callable(helper):
                try:
                    combined_source += "\n" + inspect.getsource(helper)
                except (TypeError, OSError):
                    pass

    # Find all string literals and look them up in API_SCOPE_REQUIREMENTS
    all_strings = set(re.findall(r'["\'](\w+)["\']', combined_source))
    scopes: set[str] = set()
    for op_name, op_scopes in API_SCOPE_REQUIREMENTS.items():
        if op_name in all_strings:
            scopes.update(op_scopes)

    return sorted(scopes, key=lambda s: (":write" in s, s))



def extract_tool_info(method: Any) -> dict[str, Any]:
    """Extract tool name and docstring from a tool method."""
    doc = inspect.getdoc(method) or ""

    return {
        "docstring": doc,
    }


def extract_resource_info(module_cls: type) -> list[dict[str, str]]:
    """Extract resource URIs and descriptions by inspecting register_resources."""
    try:
        source = inspect.getsource(module_cls.register_resources)
    except (AttributeError, TypeError):
        return []

    resources = []

    # Find each TextResource( and collect its full block by tracking parens
    for m in re.finditer(r'TextResource\(', source):
        start = m.end()
        depth = 1
        pos = start
        while pos < len(source) and depth > 0:
            if source[pos] == '(':
                depth += 1
            elif source[pos] == ')':
                depth -= 1
            pos += 1
        block = source[start:pos - 1]

        uri_m = re.search(r'uri=AnyUrl\(["\']([^"\']+)["\']\)', block)
        name_m = re.search(r'name=["\']([^"\']+)["\']', block)
        desc_m = re.search(r'description=["\']([^"\']+)["\']', block)

        if uri_m:
            resources.append({
                "uri": uri_m.group(1),
                "name": name_m.group(1) if name_m else "",
                "description": desc_m.group(1) if desc_m else "",
            })

    return resources


def extract_tool_annotations(module_cls: type) -> dict[str, dict[str, bool]]:
    """Extract tool annotations from register_tools source."""
    source = inspect.getsource(module_cls.register_tools)
    annotations = {}

    # Find _add_tool calls with explicit annotations
    tool_pattern = r'self\._add_tool\([^)]*?name=["\']([\w]+)["\'][^)]*?annotations=ToolAnnotations\(\s*([^)]+)\)'
    for match in re.finditer(tool_pattern, source, re.DOTALL):
        tool_name = match.group(1)
        anno_str = match.group(2)

        anno = {}
        for key in ["readOnlyHint", "destructiveHint", "idempotentHint"]:
            val_match = re.search(rf'{key}=(\w+)', anno_str)
            if val_match:
                anno[key] = val_match.group(1) == "True"

        annotations[tool_name] = anno

    return annotations


def generate_module_page(module_key: str, module_cls: type) -> str:
    """Generate a complete markdown page for a module."""
    meta = MODULE_METADATA.get(module_key, {})
    title = meta.get("title", module_key.title())
    description = meta.get("description", f"{title} module for CrowdStrike Falcon.")
    scopes = extract_module_scopes(module_cls)

    # Extract tools
    tools = []
    tool_annotations = extract_tool_annotations(module_cls)

    for attr_name in dir(module_cls):
        method = getattr(module_cls, attr_name)
        if callable(method) and not attr_name.startswith("_") and attr_name not in (
            "register_tools", "register_resources"
        ):
            # Check if this method is registered as a tool
            source = inspect.getsource(module_cls.register_tools)
            if attr_name in source:
                info = extract_tool_info(method)
                info["name"] = f"falcon_{attr_name}"
                info["raw_name"] = attr_name
                info["method"] = method

                # Get annotations
                if attr_name in tool_annotations:
                    info["annotations"] = tool_annotations[attr_name]
                else:
                    info["annotations"] = {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "idempotentHint": True,
                    }

                # Get per-tool scopes
                info["scopes"] = extract_tool_scopes(method, module_cls)

                # Example prompts (from static TOOL_EXAMPLES dict)
                info["examples"] = TOOL_EXAMPLES.get(info["name"], [])

                tools.append(info)

    # Extract resources
    resources = extract_resource_info(module_cls)

    # Build markdown
    lines = []
    lines.append("---")
    lines.append(f"title: {title}")
    lines.append(f"description: {description}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {title} Module")
    lines.append("")
    lines.append(description)
    lines.append("")

    # API Scopes
    if scopes:
        lines.append("## API Scopes")
        lines.append("")
        for scope in scopes:
            lines.append(f"- `{scope}`")
        lines.append("")

    # Tools
    if tools:
        lines.append("## Tools")
        lines.append("")
        for tool in tools:
            read_only = tool["annotations"].get("readOnlyHint", True)
            destructive = tool["annotations"].get("destructiveHint", False)

            lines.append(f"### `{tool['name']}`")
            lines.append("")

            # Admonition for mutating/destructive tools
            if destructive:
                lines.append(":::caution")
                lines.append("This tool performs destructive operations.")
                lines.append(":::")
                lines.append("")
            elif not read_only:
                lines.append(":::note")
                lines.append("This tool modifies data.")
                lines.append(":::")
                lines.append("")

            # Per-tool scopes
            tool_scopes = tool.get("scopes", [])
            if tool_scopes:
                lines.append(f"**Required scopes:** {', '.join(f'`{s}`' for s in tool_scopes)}")
                lines.append("")

            # Cleaned docstring
            cleaned = clean_docstring(tool["docstring"])
            if cleaned:
                lines.append(cleaned)
                lines.append("")

            # Example prompts
            examples = tool.get("examples", [])
            if examples:
                lines.append("**Example prompts:**")
                lines.append("")
                for ex in examples:
                    lines.append(f'- "{ex}"')
                lines.append("")

    # Resources
    if resources:
        lines.append("## Resources")
        lines.append("")
        for r in resources:
            lines.append(f"- **`{r['uri']}`**: {r['description']}")
        lines.append("")

    return "\n".join(lines)


def generate_overview_page(modules: dict[str, type]) -> str:
    """Generate the modules overview page with summary table."""
    lines = []
    lines.append("---")
    lines.append("title: Module Overview")
    lines.append("description: Overview of all available Falcon MCP modules with API scopes.")
    lines.append("---")
    lines.append("")
    lines.append("# Module Overview")
    lines.append("")
    lines.append("The Falcon MCP Server provides the following modules. Each module requires specific CrowdStrike API scopes.")
    lines.append("")
    lines.append("| Module | API Scopes | Description |")
    lines.append("|--------|-------------------|-------------|")

    for key in sorted(MODULE_METADATA.keys()):
        meta = MODULE_METADATA[key]
        title = meta["title"]
        slug = meta.get("slug", key)
        module_cls = modules.get(key)
        scopes_list = extract_module_scopes(module_cls) if module_cls else []
        scopes = ", ".join(f"`{s}`" for s in scopes_list)
        desc = meta.get("description", "")
        lines.append(f"| [{title}](/falcon-mcp/modules/{slug}/) | {scopes} | {desc} |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Generate all module documentation pages."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    modules = discover_module_classes()
    print(f"Discovered {len(modules)} modules: {', '.join(sorted(modules.keys()))}")

    # Generate overview page
    overview = generate_overview_page(modules)
    (OUTPUT_DIR / "overview.md").write_text(overview)
    print("  Generated: modules/overview.md")

    # Generate per-module pages
    for key, cls in sorted(modules.items()):
        meta = MODULE_METADATA.get(key, {})
        slug = meta.get("slug", key)
        filename = f"{slug}.md"

        page = generate_module_page(key, cls)
        (OUTPUT_DIR / filename).write_text(page)
        print(f"  Generated: modules/{filename}")

    print(f"\nDone. {len(modules) + 1} files written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
