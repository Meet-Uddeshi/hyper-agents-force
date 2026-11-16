#!/usr/bin/env python3
"""
Unit tests for Log4j Vulnerability Scanner & Automated Resolver.
"""

import sys
import tempfile
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE_DIR))

from bin.log4j_scanner import Log4jScanner, is_vulnerable_log4j


def test_version_evaluation():
    """Verify vulnerable and patched Log4j versions."""
    # Vulnerable
    vuln, cves = is_vulnerable_log4j("2.14.1")
    assert vuln is True
    assert any("CVE-2021-44228" in c for c in cves)

    vuln, cves = is_vulnerable_log4j("2.15.0")
    assert vuln is True
    assert any("CVE-2021-45046" in c for c in cves)

    vuln, cves = is_vulnerable_log4j("2.16.0")
    assert vuln is True

    # Safe
    safe, _ = is_vulnerable_log4j("2.17.1")
    assert safe is False

    safe, _ = is_vulnerable_log4j("2.24.3")
    assert safe is False


def test_pom_xml_scan_and_fix():
    """Verify scanning and automated patching of Maven pom.xml."""
    mock_pom = """<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.example</groupId>
  <artifactId>demo</artifactId>
  <version>1.0.0</version>
  <dependencies>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-core</artifactId>
      <version>2.14.1</version>
    </dependency>
  </dependencies>
</project>"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        pom_file = Path(tmp_dir) / "pom.xml"
        pom_file.write_text(mock_pom, encoding="utf-8")

        # 1. Scan
        findings = Log4jScanner.scan_pom_xml(pom_file)
        assert len(findings) == 1
        assert findings[0]["installed_version"] == "2.14.1"
        assert any("CVE-2021-44228" in c for c in findings[0]["cves"])

        # 2. Fix
        res = Log4jScanner.fix_workspace(Path(tmp_dir), safe_version="2.17.1")
        assert len(res["patched_files"]) == 1

        # 3. Re-scan
        findings_after = Log4jScanner.scan_pom_xml(pom_file)
        assert len(findings_after) == 0
        patched_content = pom_file.read_text(encoding="utf-8")
        assert "2.17.1" in patched_content


def test_gradle_scan_and_fix():
    """Verify scanning and automated patching of Gradle build files."""
    mock_gradle = """dependencies {
    implementation 'org.apache.logging.log4j:log4j-core:2.14.1'
}"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        gradle_file = Path(tmp_dir) / "build.gradle"
        gradle_file.write_text(mock_gradle, encoding="utf-8")

        # 1. Scan
        findings = Log4jScanner.scan_gradle_file(gradle_file)
        assert len(findings) == 1
        assert findings[0]["installed_version"] == "2.14.1"

        # 2. Fix
        res = Log4jScanner.fix_workspace(Path(tmp_dir), safe_version="2.17.1")
        assert len(res["patched_files"]) == 1

        # 3. Re-scan
        findings_after = Log4jScanner.scan_gradle_file(gradle_file)
        assert len(findings_after) == 0
        patched_content = gradle_file.read_text(encoding="utf-8")
        assert "2.17.1" in patched_content


if __name__ == "__main__":
    test_version_evaluation()
    test_pom_xml_scan_and_fix()
    test_gradle_scan_and_fix()
    print("All log4j scanner tests passed successfully.")
