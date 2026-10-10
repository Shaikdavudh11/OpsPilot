import re
from typing import List
from app.schemas.incident import (
    IncidentAnalysisResponse,
    Severity,
    LikelyRootCause,
    EvidenceItem,
    RecommendationItem,
    PreventionItem,
    RiskLevel,
    Confidence,
)
from app.services.providers.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """
    Deterministic AI provider that evaluates infrastructure logs using
    SRE pattern recognition. Extracts factual evidence directly from input logs
    without inventing hallucinated lines or external metrics.
    """

    async def analyze(
        self,
        sanitized_logs: str,
        title: str,
        environment: str,
        service_name: str,
    ) -> IncidentAnalysisResponse:
        log_lower = sanitized_logs.lower()
        lines = [line.strip() for line in sanitized_logs.split("\n") if line.strip()]

        # Helper to find real matching log lines for evidence
        def find_evidence_lines(keywords: List[str], max_items: int = 3) -> List[EvidenceItem]:
            evidence = []
            for idx, line in enumerate(lines):
                if any(kw.lower() in line.lower() for kw in keywords):
                    evidence.append(
                        EvidenceItem(
                            source=f"log_stream:line_{idx + 1}",
                            finding=line[:250],
                        )
                    )
                    if len(evidence) >= max_items:
                        break
            if not evidence and lines:
                evidence.append(
                    EvidenceItem(
                        source="log_stream:header",
                        finding=lines[0][:250],
                    )
                )
            return evidence

        # Scenario 1: PostgreSQL connection refused
        if (
            "connection refused" in log_lower
            and ("5432" in log_lower or "postgres" in log_lower)
        ) or "psycopg" in log_lower or "could not connect to server" in log_lower:
            return IncidentAnalysisResponse(
                title=title if title != "Uncategorized Incident" else "PostgreSQL Database Connection Refused",
                severity=Severity.HIGH,
                summary=(
                    f"Service '{service_name}' in {environment} cannot establish a TCP connection to the PostgreSQL database on port 5432. "
                    "All database queries and transactions are failing with ECONNREFUSED."
                ),
                likely_root_cause=LikelyRootCause(
                    description="The target PostgreSQL service is down, listening on a different network interface, or blocked by firewall/security group rules.",
                    confidence=Confidence.HIGH,
                    reasoning=(
                        "Logs explicitly state TCP connection refused on port 5432. "
                        "Because the connection was refused rather than timed out, the host was reachable but no process was listening on the target port."
                    ),
                ),
                evidence=find_evidence_lines(["connection refused", "5432", "postgres", "psycopg", "could not connect"]),
                recommendations=[
                    RecommendationItem(
                        action="Check if the PostgreSQL daemon is active on the database host or container.",
                        reason="Connection refused indicates the operating system responded with RST, meaning no process is bound to port 5432.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="pg_isready -h db.internal -p 5432 || sudo systemctl status postgresql",
                    ),
                    RecommendationItem(
                        action="Inspect PostgreSQL postgresql.conf listen_addresses setting.",
                        reason="If postgresql.conf has listen_addresses = 'localhost', external containers or hosts will be rejected.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="grep -E '^listen_addresses' /etc/postgresql/*/main/postgresql.conf",
                    ),
                    RecommendationItem(
                        action="Verify security group and network access control list (NACL) rules between the application and database subnets.",
                        reason="Misconfigured ingress security groups will reject or drop connection attempts.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="nc -zv db.internal 5432",
                    ),
                ],
                prevention=[
                    PreventionItem(
                        strategy="Connection Pooling and Health-Check Circuit Breakers",
                        details="Configure PgBouncer or an application-level pool (e.g., SQLAlchemy Pool with pool_pre_ping=True) so transient drops do not crash workers.",
                    ),
                    PreventionItem(
                        strategy="Database Liveness Monitoring and Automated Alerting",
                        details="Deploy Prometheus postgres_exporter to alert SREs when database liveness fails before application pools deplete.",
                    ),
                ],
                limitations=[
                    "Cannot verify PostgreSQL process state on remote host from application logs alone.",
                    "Cannot inspect cloud provider VPC route tables or security group configurations without infrastructure access.",
                ],
            )

        # Scenario 2: Kubernetes ImagePullBackOff / ErrImagePull
        if (
            "imagepullbackoff" in log_lower
            or "errimagepull" in log_lower
            or "failed to pull image" in log_lower
            or "manifest unknown" in log_lower
        ):
            return IncidentAnalysisResponse(
                title=title if title != "Uncategorized Incident" else "Kubernetes Pod ImagePullBackOff Failure",
                severity=Severity.HIGH,
                summary=(
                    f"Kubernetes workload '{service_name}' in {environment} cannot start because the kubelet failed to pull the container image from the container registry."
                ),
                likely_root_cause=LikelyRootCause(
                    description="The container image tag does not exist, the repository URL is mistyped, or registry pull secrets (imagePullSecrets) are missing or expired.",
                    confidence=Confidence.HIGH,
                    reasoning=(
                        "Kubelet emitted ErrImagePull followed by ImagePullBackOff. "
                        "The registry returned an error or authentication rejection during manifest download."
                    ),
                ),
                evidence=find_evidence_lines(["imagepullbackoff", "errimagepull", "failed to pull", "manifest", "registry"]),
                recommendations=[
                    RecommendationItem(
                        action="Describe the failing pod to inspect the exact kubelet pull error message.",
                        reason="Pod events will reveal whether the failure was an HTTP 401/403 (auth) or HTTP 404 (tag not found).",
                        risk_level=RiskLevel.LOW,
                        suggested_command=f"kubectl describe pod -l app={service_name} -n {environment}",
                    ),
                    RecommendationItem(
                        action="Verify that the image tag exists in the registry.",
                        reason="Frequently triggered when CI pipeline fails to push the image before Helm or ArgoCD deployment triggers.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="docker manifest inspect <REGISTRY_URL>/<IMAGE>:<TAG>",
                    ),
                    RecommendationItem(
                        action="Check imagePullSecrets in the Kubernetes namespace and Pod spec.",
                        reason="Missing or invalid docker-registry secret prevents kubelet from authenticating with private registries.",
                        risk_level=RiskLevel.LOW,
                        suggested_command=f"kubectl get secret -n {environment} -l type=kubernetes.io/dockerconfigjson",
                    ),
                ],
                prevention=[
                    PreventionItem(
                        strategy="Atomic CI/CD Deployment Gates",
                        details="Ensure CI release jobs only trigger deployment manifests after registry push has returned HTTP 200 and image digest is confirmed.",
                    ),
                    PreventionItem(
                        strategy="Registry Pull Secret Automation",
                        details="Use Kubernetes External Secrets Operator or AWS/GCP workload identity to rotate container registry credentials automatically.",
                    ),
                ],
                limitations=[
                    "Cannot authenticate against private container registry to test image existence directly.",
                    "Unable to inspect cluster-wide imagePullSecrets without kubeconfig credentials.",
                ],
            )

        # Scenario 3: Kubernetes CrashLoopBackOff / OOMKilled / Exit 137
        if (
            "crashloopbackoff" in log_lower
            or "oomkilled" in log_lower
            or "exit code 137" in log_lower
            or "terminated with exit code" in log_lower
        ):
            is_oom = "oom" in log_lower or "137" in log_lower
            return IncidentAnalysisResponse(
                title=title if title != "Uncategorized Incident" else ("Kubernetes Pod OOMKilled" if is_oom else "Kubernetes CrashLoopBackOff"),
                severity=Severity.CRITICAL if environment == "production" else Severity.HIGH,
                summary=(
                    f"Pod for '{service_name}' in {environment} crashed repeatedly immediately upon startup, causing Kubernetes to back off restarts."
                    + (" Container was terminated by kernel OOM-killer due to memory limit breach." if is_oom else "")
                ),
                likely_root_cause=LikelyRootCause(
                    description="Container process exceeded allocated cgroup memory limit (OOMKilled) or crashed on unhandled startup exception." if is_oom else "Application startup command failed or exited unexpectedly with non-zero exit code.",
                    confidence=Confidence.HIGH,
                    reasoning=(
                        "Logs indicate repeated pod restarts and termination. "
                        + ("Exit code 137 explicitly confirms SIGKILL delivered by the Linux kernel OOM killer." if is_oom else "Process failed during initialization before readiness probe succeeded.")
                    ),
                ),
                evidence=find_evidence_lines(["crashloopbackoff", "oomkilled", "137", "exit code", "back-off", "terminated"]),
                recommendations=[
                    RecommendationItem(
                        action="Inspect the previous terminated container logs.",
                        reason="kubectl logs --previous retrieves the stdout/stderr of the crashed container before restart.",
                        risk_level=RiskLevel.LOW,
                        suggested_command=f"kubectl logs -l app={service_name} -n {environment} --previous --tail=100",
                    ),
                    RecommendationItem(
                        action="Check pod resource limits and current cgroup memory consumption.",
                        reason="Identify if memory limit is set too low for JVM heap, Node.js heap, or worker processes.",
                        risk_level=RiskLevel.LOW,
                        suggested_command=f"kubectl top pod -l app={service_name} -n {environment}",
                    ),
                    RecommendationItem(
                        action="Inspect pod status and termination reason in pod spec.",
                        reason="Pod spec lastState.terminated contains exact reason (e.g., OOMKilled, Error) and exitCode.",
                        risk_level=RiskLevel.LOW,
                        suggested_command=f"kubectl get pod -l app={service_name} -n {environment} -o jsonpath='{{.items[*].status.containerStatuses[*].lastState.terminated}}'",
                    ),
                ],
                prevention=[
                    PreventionItem(
                        strategy="Right-Sizing Pod Resources and Vertical Pod Autoscaler",
                        details="Profile memory usage under load and establish container memory limits with at least 25% safety headroom above max resident memory.",
                    ),
                    PreventionItem(
                        strategy="Graceful Startup Probes",
                        details="Configure startupProbe with sufficient initialDelaySeconds and failureThreshold to prevent premature liveness probe kills during cold starts.",
                    ),
                ],
                limitations=[
                    "Cannot retrieve kernel dmesg logs from Kubernetes worker nodes to inspect host-level memory events.",
                    "Application configuration files (e.g. JVM -Xmx settings) are not visible in stdout logs.",
                ],
            )

        # Scenario 4: Docker container startup crash (Entrypoint / missing file / missing env)
        if (
            "docker" in log_lower
            or "exec user process caused: no such file or directory" in log_lower
            or "entrypoint" in log_lower
            or "container exited with code 1" in log_lower
            or "standard_init_linux.go" in log_lower
        ):
            return IncidentAnalysisResponse(
                title=title if title != "Uncategorized Incident" else "Docker Container Exits During Startup",
                severity=Severity.HIGH,
                summary=(
                    f"Docker container for '{service_name}' exited immediately after initiation. "
                    "Entrypoint binary or startup script failed to execute."
                ),
                likely_root_cause=LikelyRootCause(
                    description="The container ENTRYPOINT or CMD points to a nonexistent binary, an unexecutable script, or a shell script with Windows CRLF line endings.",
                    confidence=Confidence.HIGH,
                    reasoning=(
                        "Logs indicate the container initialization process failed at standard_init_linux or returned exit code 1/127 immediately upon container spawn."
                    ),
                ),
                evidence=find_evidence_lines(["exec user process", "no such file", "exited with code", "entrypoint", "standard_init_linux"]),
                recommendations=[
                    RecommendationItem(
                        action="Check Dockerfile ENTRYPOINT and file permissions.",
                        reason="Ensure the target script has executable permissions (chmod +x) and uses '#!/bin/sh' or '#!/bin/bash'.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="docker run --rm --entrypoint /bin/sh <IMAGE_NAME> -c 'ls -la /entrypoint.sh'",
                    ),
                    RecommendationItem(
                        action="Verify script line endings in the source repository.",
                        reason="Files saved with Windows CRLF line endings cause Linux containers to fail with 'no such file or directory'.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="file entrypoint.sh",
                    ),
                ],
                prevention=[
                    PreventionItem(
                        strategy="Container Healthchecks and CI Linting",
                        details="Add hadolint and container smoke test steps to CI pipelines to validate container entrypoint execution before publishing.",
                    ),
                    PreventionItem(
                        strategy="Standardize .gitattributes",
                        details="Commit a .gitattributes file enforcing '* text=auto eol=lf' across all shell scripts.",
                    ),
                ],
                limitations=[
                    "Cannot inspect the built container filesystem or layers without Docker daemon access.",
                ],
            )

        # Scenario 5: CI / GitHub Actions pipeline failure
        if (
            "github actions" in log_lower
            or "ci" in log_lower
            or "assertionerror" in log_lower
            or "test failed" in log_lower
            or "npm test" in log_lower
            or "pytest" in log_lower
        ):
            return IncidentAnalysisResponse(
                title=title if title != "Uncategorized Incident" else "CI Pipeline Test Suite Failure",
                severity=Severity.MEDIUM,
                summary=(
                    f"Automated test runner in CI pipeline for '{service_name}' failed with test assertion errors, blocking the build from deployment."
                ),
                likely_root_cause=LikelyRootCause(
                    description="One or more automated test cases failed due to assertion mismatches, mock regressions, or breaking changes in recent commits.",
                    confidence=Confidence.HIGH,
                    reasoning=(
                        "Log stream contains test execution output with explicit test failure status and stack trace."
                    ),
                ),
                evidence=find_evidence_lines(["assertionerror", "failed", "error", "test", "exit code 1"]),
                recommendations=[
                    RecommendationItem(
                        action="Locate the exact failing test function and assertion diff in CI output.",
                        reason="Pinpoint the exact expected vs actual values in the failed assertion.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="git diff HEAD~1..HEAD",
                    ),
                    RecommendationItem(
                        action="Run the failing test locally in isolation with verbose logging.",
                        reason="Reproducing locally confirms whether the bug is commit-specific or due to CI environment drift.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="npm test -- --testPathPattern=<FAILING_TEST> # or pytest -k <test_name> -v",
                    ),
                ],
                prevention=[
                    PreventionItem(
                        strategy="Pre-commit Hooks and Branch Protection",
                        details="Enforce local pre-commit hooks running unit tests and enable GitHub branch protection requiring passing CI checks prior to merge.",
                    ),
                    PreventionItem(
                        strategy="Deterministic Test Fixtures",
                        details="Eliminate flaky network calls or time-dependent assertions by enforcing hermetic test fixtures and frozen time libraries.",
                    ),
                ],
                limitations=[
                    "Cannot inspect git commit history or code diffs from test runner stdout.",
                ],
            )

        # Scenario 6: Application HTTP 500 / Unhandled Exception
        if (
            "http 500" in log_lower
            or "500 internal server error" in log_lower
            or "nullpointerexception" in log_lower
            or "typeerror: cannot read property" in log_lower
            or "traceback (most recent call last)" in log_lower
            or "unhandled exception" in log_lower
        ):
            return IncidentAnalysisResponse(
                title=title if title != "Uncategorized Incident" else "Application HTTP 500 Internal Server Error",
                severity=Severity.HIGH,
                summary=(
                    f"Application '{service_name}' in {environment} is returning HTTP 500 Internal Server Errors due to an unhandled runtime exception."
                ),
                likely_root_cause=LikelyRootCause(
                    description="An unhandled null reference, missing dictionary key, or unmanaged edge case occurred during request processing.",
                    confidence=Confidence.HIGH,
                    reasoning=(
                        "Logs contain a standard application stack trace culminating in an unhandled exception before the HTTP response could be generated."
                    ),
                ),
                evidence=find_evidence_lines(["500", "traceback", "exception", "error", "typeerror", "nullpointer"]),
                recommendations=[
                    RecommendationItem(
                        action="Inspect the top frame of the stack trace to locate the failing file and line number.",
                        reason="Identifies the exact code path and input parameter causing the runtime error.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="grep -A 10 -B 2 'Traceback' application.log",
                    ),
                    RecommendationItem(
                        action="Review recent application release tags and canary deployment status.",
                        reason="Determines whether this exception started immediately after a new deployment.",
                        risk_level=RiskLevel.LOW,
                        suggested_command="git log -n 5 --oneline",
                    ),
                ],
                prevention=[
                    PreventionItem(
                        strategy="Global Exception Handlers and Error Observability",
                        details="Implement global exception handling middleware that catches unexpected runtime errors, returns structured 500 JSON, and reports traces to Sentry.",
                    ),
                    PreventionItem(
                        strategy="Input Validation with Strict Schemas",
                        details="Use Pydantic or Zod schemas at API boundaries to reject malformed payloads before they reach business logic.",
                    ),
                ],
                limitations=[
                    "Full request payload and client user context are not visible in sanitized logs.",
                ],
            )

        # Generic / Unknown Log Fallback: Grounded, Honest Uncertainty
        error_lines = [l for l in lines if any(w in l.lower() for w in ["err", "fail", "crit", "warn", "fatal"])]
        sample_evidence = [
            EvidenceItem(
                source=f"log_stream:line_{i+1}",
                finding=el[:200],
            )
            for i, el in enumerate(error_lines[:3])
        ]
        if not sample_evidence and lines:
            sample_evidence = [
                EvidenceItem(
                    source="log_stream:line_1",
                    finding=lines[0][:200],
                )
            ]

        return IncidentAnalysisResponse(
            title=title if title != "Uncategorized Incident" else "Unclassified System Diagnostic Investigation",
            severity=Severity.MEDIUM,
            summary=(
                f"Diagnostic analysis conducted on provided log stream for '{service_name}' in {environment}. "
                "Logs contain error indicators but lack sufficient context to determine an unambiguous single root cause."
            ),
            likely_root_cause=LikelyRootCause(
                description="Potential operational anomaly indicated in log stream; requires correlated metrics and configuration files.",
                confidence=Confidence.LOW,
                reasoning=(
                    "Log lines suggest abnormal termination or error status, but key causal context (such as prior upstream request logs or kernel events) is absent."
                ),
            ),
            evidence=sample_evidence,
            recommendations=[
                RecommendationItem(
                    action="Collect preceding log lines (100+ lines prior to error event).",
                    reason="Single error lines often reflect symptoms rather than the initiating failure.",
                    risk_level=RiskLevel.LOW,
                    suggested_command="tail -n 200 /var/log/application.log",
                ),
                RecommendationItem(
                    action="Correlate with system metrics (CPU, Memory, Disk I/O, Network socket count).",
                    reason="Verify if external resource constraints precipitated the error.",
                    risk_level=RiskLevel.LOW,
                    suggested_command="top -b -n 1 | head -n 20; df -h",
                ),
            ],
            prevention=[
                PreventionItem(
                    strategy="Structured JSON Logging",
                    details="Migrate logs to structured JSON with trace_id, span_id, timestamp, and severity to enable automated correlation.",
                ),
                PreventionItem(
                    strategy="Centralized Log Aggregation",
                    details="Forward logs to OpenSearch, Datadog, or Grafana Loki with standardized alerting rules.",
                ),
            ],
            limitations=[
                "Evidence is limited to the submitted text snippet.",
                "Correlated system metrics (CPU, memory, disk, network) were not provided.",
                "Service configuration and upstream/downstream architecture diagrams were not provided.",
            ],
        )
