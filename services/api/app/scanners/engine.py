import hashlib
import re
from dataclasses import dataclass

SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "aws-access-key", "critical"),
    (r"ghp_[a-zA-Z0-9]{36}", "github-pat", "critical"),
    (r"glpat-[a-zA-Z0-9\-_]{20,}", "gitlab-pat", "critical"),
    (r"sk-[a-zA-Z0-9]{20,}", "generic-api-key", "high"),
    (r"password\s*=\s*['\"][^'\"]{8,}['\"]", "hardcoded-password", "high"),
]

CVE_PATTERN = re.compile(r"(CVE-\d{4}-\d+)", re.IGNORECASE)


@dataclass
class ScanFinding:
    scanner: str
    rule_id: str
    severity: str
    title: str
    description: str
    file_path: str
    line_start: int
    metadata: dict

    @property
    def fingerprint(self) -> str:
        raw = f"{self.scanner}:{self.rule_id}:{self.file_path}:{self.title}"
        return hashlib.sha256(raw.encode()).hexdigest()[:32]


def scan_content_for_secrets(file_path: str, content: str) -> list[ScanFinding]:
    findings: list[ScanFinding] = []
    for line_no, line in enumerate(content.splitlines(), start=1):
        for pattern, rule_id, severity in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(
                    ScanFinding(
                        scanner="secrets",
                        rule_id=rule_id,
                        severity=severity,
                        title=f"Potential secret detected ({rule_id})",
                        description=f"Pattern match for {rule_id} in {file_path}",
                        file_path=file_path,
                        line_start=line_no,
                        metadata={"matched_line_preview": line[:80]},
                    )
                )
    return findings


def scan_package_json(file_path: str, content: str) -> list[ScanFinding]:
    """Lightweight SCA stub — flags known-vulnerable package versions for demo."""
    findings: list[ScanFinding] = []
    vulnerable = {
        "lodash": ["4.17.20", "4.17.19", "4.17.15"],
        "axios": ["0.21.0", "0.21.1"],
        "minimist": ["1.2.0", "1.2.1", "1.2.2"],
    }
    for pkg, versions in vulnerable.items():
        for ver in versions:
            pattern = rf'"{pkg}"\s*:\s*"{re.escape(ver)}"'
            if re.search(pattern, content):
                findings.append(
                    ScanFinding(
                        scanner="sca",
                        rule_id=f"cve-stub-{pkg}-{ver}",
                        severity="high",
                        title=f"Vulnerable dependency: {pkg}@{ver}",
                        description=f"{pkg} {ver} has known vulnerabilities. Upgrade to latest patched version.",
                        file_path=file_path,
                        line_start=1,
                        metadata={"package": pkg, "installed": ver, "scanner": "sca-stub"},
                    )
                )
    if CVE_PATTERN.search(content):
        for match in CVE_PATTERN.finditer(content):
            findings.append(
                ScanFinding(
                    scanner="sca",
                    rule_id=match.group(1).lower(),
                    severity="medium",
                    title=f"Referenced vulnerability {match.group(1)}",
                    description="CVE reference found in dependency manifest or lockfile context.",
                    file_path=file_path,
                    line_start=1,
                    metadata={"cve": match.group(1)},
                )
            )
    return findings


def scan_files(files: dict[str, str]) -> list[ScanFinding]:
    all_findings: list[ScanFinding] = []
    for path, content in files.items():
        all_findings.extend(scan_content_for_secrets(path, content))
        if path.endswith("package.json"):
            all_findings.extend(scan_package_json(path, content))
    return all_findings
