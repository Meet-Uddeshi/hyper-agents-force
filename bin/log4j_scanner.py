#!/usr/bin/env python3
"""
Log4j Vulnerability Scanner & Automated Resolver for Hyper Agents Force.

Scans Maven (pom.xml), Gradle (build.gradle/kts), and Java build manifests for
Log4Shell and related CVEs:
  - CVE-2021-44228 (Log4Shell RCE, versions 2.0-beta9 to 2.14.1)
  - CVE-2021-45046 (Incomplete fix RCE, versions <= 2.15.0)
  - CVE-2021-45105 (Context Lookup DoS, versions <= 2.16.0)
  - CVE-2021-44832 (JDBC Appender RCE, versions <= 2.17.0)

Provides automated safe version upgrading (--fix) to safe baseline (2.17.1 or 2.24.3).
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

SAFE_LOG4J_VERSION = "2.17.1"

# Regex patterns for Gradle dependency blocks
GRADLE_LOG4J_PATTERNS = [
    re.compile(r"""(?:implementation|compile|api|runtimeOnly)\s*['"](org\.apache\.logging\.log4j:log4j-(?:core|api)):([0-9a-zA-Z\.\-_]+)['"]"""),
    re.compile(r"""group:\s*['"]org\.apache\.logging\.log4j['"],\s*name:\s*['"](log4j-(?:core|api))['"],\s*version:\s*['"]([0-9a-zA-Z\.\-_]+)['"]"""),
]

# Regex pattern for properties
PROPERTY_LOG4J_PAT = re.compile(r"""<log4j2?\.version>([0-9a-zA-Z\.\-_]+)</log4j2?\.version>""")


def parse_semver(v_str: str) -> Tuple[int, int, int]:
    """Extracts numeric semver components (major, minor, patch) safely."""
    # Clean string like 2.14.1-rc1 -> 2.14.1
    clean = re.sub(r"-[a-zA-Z0-9\._]+", "", v_str.strip())
    parts = clean.split(".")
    major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    return major, minor, patch


def is_vulnerable_log4j(version_str: str) -> Tuple[bool, List[str]]:
    """Evaluates whether the Log4j version is vulnerable to known CVEs."""
    cves = []
    try:
        major, minor, patch = parse_semver(version_str)
    except Exception:
        return False, []

    # Log4j 1.x is end-of-life and has CVE-2019-17571 / JMSAppender issues
    if major == 1:
        cves.append("CVE-2019-17571 (Log4j 1.x EOL Deserialization)")
        return True, cves

    # Log4j 2.x vulnerabilities
    if major == 2:
        if (minor < 15) or (minor == 14) or (minor == 15 and patch == 0):
            cves.append("CVE-2021-44228 (Log4Shell JNDI RCE - CVSS 10.0)")
            cves.append("CVE-2021-45046 (Thread Context Message RCE)")
        if minor <= 16:
            cves.append("CVE-2021-45105 (Context Lookup DoS)")
        if minor == 17 and patch == 0:
            cves.append("CVE-2021-44832 (JDBC Appender Arbitrary Code Execution)")

    return len(cves) > 0, cves


class Log4jScanner:
    """Detects and resolves Log4j vulnerabilities in project dependencies."""

    @classmethod
    def scan_pom_xml(cls, pom_path: Path) -> List[Dict[str, Any]]:
        """Parses Maven pom.xml for vulnerable Log4j dependencies or properties."""
        findings = []
        try:
            content = pom_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return findings

        # Check properties
        prop_matches = PROPERTY_LOG4J_PAT.findall(content)
        for v in prop_matches:
            is_vuln, cves = is_vulnerable_log4j(v)
            if is_vuln:
                findings.append({
                    "file": str(pom_path),
                    "dependency": "log4j.version (Property)",
                    "installed_version": v,
                    "cves": cves,
                    "fix_available": True,
                })

        # Check dependency tags via regex to preserve line numbers and formatting
        dep_pat = re.compile(
            r"<dependency>[\s\S]*?<groupId>\s*org\.apache\.logging\.log4j\s*</groupId>[\s\S]*?<artifactId>\s*(log4j-(?:core|api))\s*</artifactId>[\s\S]*?<version>\s*([0-9a-zA-Z\.\-_$]+)\s*</version>[\s\S]*?</dependency>"
        )
        for match in dep_pat.finditer(content):
            artifact = match.group(1)
            ver = match.group(2)
            if not ver.startswith("$"):  # Skip variable expressions handled in properties
                is_vuln, cves = is_vulnerable_log4j(ver)
                if is_vuln:
                    findings.append({
                        "file": str(pom_path),
                        "dependency": f"org.apache.logging.log4j:{artifact}",
                        "installed_version": ver,
                        "cves": cves,
                        "fix_available": True,
                    })

        return findings

    @classmethod
    def scan_gradle_file(cls, gradle_path: Path) -> List[Dict[str, Any]]:
        """Parses build.gradle / build.gradle.kts for vulnerable Log4j dependencies."""
        findings = []
        try:
            content = gradle_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return findings

        for pat in GRADLE_LOG4J_PATTERNS:
            for match in pat.finditer(content):
                artifact = match.group(1)
                ver = match.group(2)
                is_vuln, cves = is_vulnerable_log4j(ver)
                if is_vuln:
                    findings.append({
                        "file": str(gradle_path),
                        "dependency": artifact,
                        "installed_version": ver,
                        "cves": cves,
                        "fix_available": True,
                    })

        return findings

    @classmethod
    def scan_workspace(cls, root_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Scans the workspace for all Java dependency definitions."""
        root = Path(root_dir or Path.cwd()).resolve()
        all_findings = []

        ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", ".agent", ".worktrees"}

        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in ignored for part in p.parts):
                continue

            name = p.name.lower()
            if name == "pom.xml":
                all_findings.extend(cls.scan_pom_xml(p))
            elif name in ("build.gradle", "build.gradle.kts"):
                all_findings.extend(cls.scan_gradle_file(p))

        risk = "CLEAN"
        if all_findings:
            risk = "CRITICAL"

        return {
            "root": str(root),
            "vulnerabilities_found": len(all_findings),
            "risk_level": risk,
            "findings": all_findings,
        }

    @classmethod
    def fix_workspace(cls, root_dir: Optional[Path] = None, safe_version: str = SAFE_LOG4J_VERSION) -> Dict[str, Any]:
        """Automatically updates vulnerable dependencies to the safe patched baseline."""
        root = Path(root_dir or Path.cwd()).resolve()
        modified_files = []

        ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", ".agent", ".worktrees"}

        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in ignored for part in p.parts):
                continue

            name = p.name.lower()
            if name == "pom.xml":
                content = p.read_text(encoding="utf-8", errors="ignore")
                original = content

                # Patch properties
                content = PROPERTY_LOG4J_PAT.sub(f"<log4j2.version>{safe_version}</log4j2.version>", content)

                # Patch explicit dependency versions
                dep_pat = re.compile(
                    r"(<groupId>\s*org\.apache\.logging\.log4j\s*</groupId>[\s\S]*?<artifactId>\s*log4j-(?:core|api)\s*</artifactId>[\s\S]*?<version>)\s*([0-9a-zA-Z\.\-_]+)(\s*</version>)"
                )
                def replace_pom_ver(m):
                    v = m.group(2)
                    is_vuln, _ = is_vulnerable_log4j(v)
                    if is_vuln:
                        return f"{m.group(1)}{safe_version}{m.group(3)}"
                    return m.group(0)

                content = dep_pat.sub(replace_pom_ver, content)

                if content != original:
                    p.write_text(content, encoding="utf-8")
                    modified_files.append(str(p.relative_to(root)))

            elif name in ("build.gradle", "build.gradle.kts"):
                content = p.read_text(encoding="utf-8", errors="ignore")
                original = content

                def replace_gradle(m):
                    artifact = m.group(1)
                    v = m.group(2)
                    is_vuln, _ = is_vulnerable_log4j(v)
                    if is_vuln:
                        return f"'{artifact}:{safe_version}'"
                    return m.group(0)

                for pat in GRADLE_LOG4J_PATTERNS:
                    content = pat.sub(replace_gradle, content)

                if content != original:
                    p.write_text(content, encoding="utf-8")
                    modified_files.append(str(p.relative_to(root)))

        return {
            "patched_files": modified_files,
            "safe_version": safe_version,
            "status": "SUCCESS" if modified_files else "NO_CHANGES_NEEDED",
        }


def main():
    root = Path(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else Path.cwd()
    fix_mode = "--fix" in sys.argv or (len(sys.argv) > 1 and sys.argv[1] == "fix")

    if fix_mode:
        res = Log4jScanner.fix_workspace(root)
        print(f"\nLog4j Automated Resolver:")
        print(f"- Patched Files: {len(res['patched_files'])}")
        for f in res["patched_files"]:
            print(f"  * {f} -> updated to safe version {res['safe_version']}")
        print()
    else:
        res = Log4jScanner.scan_workspace(root)
        print(f"\nLog4j Vulnerability Audit: {res['root']}")
        print(f"- Risk Level: [{res['risk_level']}]")
        print(f"- Vulnerabilities Found: {res['vulnerabilities_found']}")
        for f in res["findings"]:
            print(f"  * {f['file']}: {f['dependency']} (Installed: {f['installed_version']})")
            for cve in f["cves"]:
                print(f"    - {cve}")
        print()


if __name__ == "__main__":
    main()
