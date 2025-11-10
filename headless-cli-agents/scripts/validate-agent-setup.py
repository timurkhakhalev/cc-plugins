#!/usr/bin/env python3
"""
CLI Agent Setup Validation Script

This script checks if various AI coding CLI agents are properly installed,
configured, and authenticated for headless operation.

Usage:
    python validate-agent-setup.py [agent_name]

If agent_name is provided, only that agent will be checked.
Otherwise, all available agents will be validated.
"""

import subprocess
import sys
import json
import os
from typing import Dict, List, Tuple, Optional

# Agent configuration
AGENTS = {
    "claude": {
        "commands": ["claude", "claude -p 'test'"],
        "install_url": "https://claude.ai/install",
        "auth_check": "claude auth status",
        "description": "Anthropic Claude Code CLI"
    },
    "codex": {
        "commands": ["codex", "codex exec 'test'"],
        "install_url": "https://platform.openai.com/docs/cli",
        "auth_check": "codex auth verify",
        "description": "OpenAI Codex CLI"
    },
    "gemini": {
        "commands": ["gemini", "gemini -p 'test'"],
        "install_url": "https://geminicli.com/docs/installation",
        "auth_check": "gemini auth status",
        "description": "Google Gemini CLI"
    },
    "opencode": {
        "commands": ["opencode", "opencode -p 'test'"],
        "install_url": "https://github.com/opencode-ai/opencode",
        "auth_check": "echo 'Check environment variables for API keys'",
        "description": "OpenCode CLI (multi-provider)"
    },
    "qwen": {
        "commands": ["qwen", "qwen -p 'test'"],
        "install_url": "https://github.com/QwenLM/qwen-code",
        "auth_check": "qwen auth status",
        "description": "Alibaba Qwen Code CLI"
    },
    "droid": {
        "commands": ["droid", "droid exec 'test'"],
        "install_url": "https://docs.factory.ai/cli/installation",
        "auth_check": "droid auth status",
        "description": "Factory Droid CLI"
    }
}

def run_command(cmd: str, timeout: int = 30) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd.split() if isinstance(cmd, str) else cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def check_agent_installation(agent_name: str, config: Dict) -> Dict:
    """Check if an agent is properly installed"""
    results = {
        "agent": agent_name,
        "description": config["description"],
        "installed": False,
        "version": None,
        "auth_status": "unknown",
        "basic_test": False,
        "errors": [],
        "recommendations": []
    }

    # Check if command exists
    cmd = config["commands"][0]
    exit_code, stdout, stderr = run_command(f"which {cmd}")

    if exit_code != 0:
        results["errors"].append(f"Command '{cmd}' not found in PATH")
        results["recommendations"].append(f"Install from: {config['install_url']}")
        return results

    results["installed"] = True
    results["version"] = stdout.strip() or "Unknown version"

    # Check authentication
    if "auth_check" in config:
        exit_code, auth_stdout, auth_stderr = run_command(config["auth_check"])
        if exit_code == 0:
            results["auth_status"] = "authenticated"
        else:
            results["auth_status"] = "not_authenticated"
            results["errors"].append(f"Authentication check failed: {auth_stderr}")
            results["recommendations"].append("Run authentication command for this agent")

    # Basic functionality test (try to get help)
    exit_code, help_stdout, help_stderr = run_command(f"{cmd} --help", timeout=10)
    if exit_code == 0:
        results["basic_test"] = True

    return results

def check_environment_requirements() -> Dict:
    """Check general environment requirements"""
    results = {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "environment_variables": {},
        "recommendations": []
    }

    # Check for common environment variables
    env_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_BASE_URL",
        "CLAUDE_API_KEY"
    ]

    for var in env_vars:
        value = os.environ.get(var)
        results["environment_variables"][var] = "SET" if value else "NOT_SET"

    # Check git availability
    exit_code, stdout, stderr = run_command("git --version")
    if exit_code != 0:
        results["recommendations"].append("Install git for better agent integration")

    return results

def print_results(results: List[Dict], env_info: Dict, format_type: str = "table"):
    """Print validation results in specified format"""

    if format_type == "json":
        output = {
            "environment": env_info,
            "agents": results
        }
        print(json.dumps(output, indent=2))
        return

    # Table format
    print("\n" + "="*80)
    print("🤖 CLI AGENT SETUP VALIDATION")
    print("="*80)

    print(f"\n📁 Working Directory: {env_info['working_directory']}")
    print(f"🐍 Python Version: {env_info['python_version'].split()[0]}")

    print("\n🔑 Environment Variables:")
    for var, status in env_info["environment_variables"].items():
        status_icon = "✅" if status == "SET" else "❌"
        print(f"  {status_icon} {var}: {status}")

    print("\n" + "="*80)
    print("AGENT STATUS")
    print("="*80)

    for result in results:
        agent = result["agent"]
        description = result["description"]

        # Status icons
        install_icon = "✅" if result["installed"] else "❌"
        auth_icon = "✅" if result["auth_status"] == "authenticated" else "❌" if result["auth_status"] == "not_authenticated" else "⚠️"
        test_icon = "✅" if result["basic_test"] else "❌"

        print(f"\n{install_icon} {agent.upper()}: {description}")
        print(f"   📦 Installed: {'Yes' if result['installed'] else 'No'}")
        print(f"   🔐 Auth Status: {result['auth_status']}")
        print(f"   🧪 Basic Test: {'Pass' if result['basic_test'] else 'Fail'}")

        if result["version"]:
            print(f"   📋 Version: {result['version']}")

        if result["errors"]:
            print("   ❌ Errors:")
            for error in result["errors"]:
                print(f"      • {error}")

        if result["recommendations"]:
            print("   💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"      • {rec}")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    installed_count = sum(1 for r in results if r["installed"])
    auth_count = sum(1 for r in results if r["auth_status"] == "authenticated")

    print(f"📦 Agents Installed: {installed_count}/{len(results)}")
    print(f"🔐 Agents Authenticated: {auth_count}/{len(results)}")

    if env_info["recommendations"]:
        print("\n💡 General Recommendations:")
        for rec in env_info["recommendations"]:
            print(f"  • {rec}")

def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate CLI agent setup")
    parser.add_argument("agent", nargs="?", choices=list(AGENTS.keys()),
                       help="Specific agent to check (default: all)")
    parser.add_argument("--format", choices=["table", "json"], default="table",
                       help="Output format (default: table)")
    parser.add_argument("--quiet", action="store_true",
                       help="Only show summary")

    args = parser.parse_args()

    # Check environment
    env_info = check_environment_requirements()

    # Check agents
    if args.agent:
        agents_to_check = {args.agent: AGENTS[args.agent]}
    else:
        agents_to_check = AGENTS

    results = []
    for agent_name, config in agents_to_check.items():
        result = check_agent_installation(agent_name, config)
        results.append(result)

        if not args.quiet:
            print(f"Checking {agent_name}...", end=" ")
            if result["installed"]:
                print("✅ Found")
            else:
                print("❌ Not found")

    # Print results
    if not args.quiet:
        print_results(results, env_info, args.format)
    else:
        # Quiet summary
        installed = sum(1 for r in results if r["installed"])
        authenticated = sum(1 for r in results if r["auth_status"] == "authenticated")
        print(f"Installed: {installed}/{len(results)} | Authenticated: {authenticated}/{len(results)}")

    # Exit code based on results
    if not any(r["installed"] for r in results):
        sys.exit(2)  # No agents installed
    elif not all(r["installed"] for r in results):
        sys.exit(1)  # Some agents missing
    else:
        sys.exit(0)  # All good

if __name__ == "__main__":
    main()