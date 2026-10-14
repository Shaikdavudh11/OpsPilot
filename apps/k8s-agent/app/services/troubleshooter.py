import re
from typing import List

try:
    from app.schemas.k8s import PodTroubleshootRequest, PodTroubleshootResponse
except (ImportError, ModuleNotFoundError):
    from ..schemas.k8s import PodTroubleshootRequest, PodTroubleshootResponse


class PodTroubleshooter:
    """Diagnoses Kubernetes pod failure events, identifies root causes, and generates remediation YAML patches."""

    def diagnose(self, req: PodTroubleshootRequest) -> PodTroubleshootResponse:
        combined_text = (
            f"{req.failure_type or ''}\n"
            f"{req.describe_output or ''}\n"
            f"{req.pod_logs or ''}"
        ).strip()

        pod_name = req.pod_name or "app-deployment-647bfb84cb-x829l"
        namespace = req.namespace or "default"
        text_lower = combined_text.lower()

        if "oomkilled" in text_lower or "exit code 137" in text_lower or "exitcode: 137" in text_lower:
            return self._diagnose_oomkilled(pod_name, namespace, combined_text)

        if "imagepullbackoff" in text_lower or "errimagepull" in text_lower or "repository does not exist" in text_lower or "authorization failed" in text_lower:
            return self._diagnose_imagepull(pod_name, namespace, combined_text)

        if "probe failed" in text_lower or "unhealthy" in text_lower or "initialdelayseconds" in text_lower:
            return self._diagnose_probe_failure(pod_name, namespace, combined_text)

        if (
            "econnrefused" in text_lower
            or "connection refused" in text_lower
            or "is the server running on host" in text_lower
            or "could not connect to server" in text_lower
        ):
            return self._diagnose_db_connection_refused(pod_name, namespace, combined_text)

        if "createcontainerconfigerror" in text_lower or ("configmap" in text_lower and "not found" in text_lower):
            return self._diagnose_missing_config(pod_name, namespace, combined_text)

        return self._diagnose_general_crash(pod_name, namespace, combined_text)

    def _diagnose_oomkilled(self, pod: str, ns: str, text: str) -> PodTroubleshootResponse:
        evidence = self._extract_evidence(text, [r"oomkilled", r"exit\s*code\s*137", r"cgroup.*memory", r"limit.*memory"])
        if not evidence:
            evidence = ["State: Terminated (Reason: OOMKilled, Exit Code: 137)", "Container exceeded cgroup memory limit"]

        yaml_patch = (
            f"spec:\n"
            f"  template:\n"
            f"    spec:\n"
            f"      containers:\n"
            f"        - name: app\n"
            f"          resources:\n"
            f"            requests:\n"
            f"              memory: \"512Mi\"\n"
            f"              cpu: \"250m\"\n"
            f"            limits:\n"
            f"              memory: \"1536Mi\"\n"
            f"              cpu: \"1000m\"\n"
        )

        return PodTroubleshootResponse(
            pod_name=pod,
            namespace=ns,
            detected_issue="OOMKilled (Out of Memory - Exit Code 137)",
            root_cause="The container process consumed more resident memory (RSS) than permitted by the Kubernetes cgroup limit, causing the Linux kernel OOM-killer to terminate the PID.",
            confidence="high",
            evidence=evidence,
            remediation_summary="Double container memory limit from current ceiling to 1.5Gi and configure JVM/Node max heap sizing to prevent uncontrolled heap expansion.",
            yaml_patch=yaml_patch,
            recommended_commands=[
                f"kubectl describe pod {pod} -n {ns} | grep -i -E 'oom|exit code|memory'",
                f"kubectl top pod -n {ns} --containers",
                f"kubectl patch deployment {pod.rsplit('-', 2)[0] if '-' in pod else 'app'} -n {ns} --type='json' -p='[{{\"op\": \"replace\", \"path\": \"/spec/template/spec/containers/0/resources/limits/memory\", \"value\":\"1536Mi\"}}]'",
            ],
            preventative_guidance=[
                "Set application runtime heap caps (e.g. NODE_OPTIONS='--max-old-space-size=1024' or JAVA_TOOL_OPTIONS='-XX:MaxRAMPercentage=75.0').",
                "Deploy VerticalPodAutoscaler (VPA) in recommendation mode to calculate accurate memory demands under load.",
            ],
        )

    def _diagnose_imagepull(self, pod: str, ns: str, text: str) -> PodTroubleshootResponse:
        evidence = self._extract_evidence(text, [r"imagepullbackoff", r"errimagepull", r"failed to pull image", r"unauthorized", r"not found"])
        if not evidence:
            evidence = ["Failed to pull image: repository does not exist or may require 'docker login'"]

        yaml_patch = (
            f"spec:\n"
            f"  template:\n"
            f"    spec:\n"
            f"      imagePullSecrets:\n"
            f"        - name: container-registry-creds\n"
            f"      containers:\n"
            f"        - name: app\n"
            f"          imagePullPolicy: IfNotPresent\n"
        )

        return PodTroubleshootResponse(
            pod_name=pod,
            namespace=ns,
            detected_issue="ImagePullBackOff / Private Registry Authentication Failure",
            root_cause="The Kubernetes worker node kubelet cannot authenticate with the private container registry, or the image tag is misspelled.",
            confidence="high",
            evidence=evidence,
            remediation_summary="Provision a Kubernetes docker-registry secret in the target namespace and bind it to the Pod template's imagePullSecrets.",
            yaml_patch=yaml_patch,
            recommended_commands=[
                f"kubectl create secret docker-registry container-registry-creds --docker-server=https://index.docker.io/v1/ --docker-username=<USER> --docker-password=<TOKEN> -n {ns}",
                f"kubectl patch deployment {pod.rsplit('-', 2)[0] if '-' in pod else 'app'} -n {ns} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"imagePullSecrets\":[{{\"name\":\"container-registry-creds\"}}]}}}}}}}}'",
                f"kubectl get pods -n {ns} -w",
            ],
            preventative_guidance=[
                "Ensure your CI/CD pipeline pushes images to the expected container registry before triggering Kubernetes rollouts.",
                "Verify node IAM roles (AWS ECR / GCP Artifact Registry / Azure ACR) have GetAuthorizationToken and Pull permissions.",
            ],
        )

    def _diagnose_probe_failure(self, pod: str, ns: str, text: str) -> PodTroubleshootResponse:
        evidence = self._extract_evidence(text, [r"liveness probe failed", r"readiness probe failed", r"probe failed", r"http.*statuscode", r"unhealthy"])
        if not evidence:
            evidence = ["Liveness probe failed: HTTP probe failed with statuscode: 500 or timeout"]

        yaml_patch = (
            f"spec:\n"
            f"  template:\n"
            f"    spec:\n"
            f"      containers:\n"
            f"        - name: app\n"
            f"          startupProbe:\n"
            f"            httpGet:\n"
            f"              path: /health\n"
            f"              port: 8080\n"
            f"            failureThreshold: 30\n"
            f"            periodSeconds: 5\n"
            f"          readinessProbe:\n"
            f"            httpGet:\n"
            f"              path: /health\n"
            f"              port: 8080\n"
            f"            initialDelaySeconds: 10\n"
            f"            periodSeconds: 10\n"
            f"            timeoutSeconds: 3\n"
        )

        return PodTroubleshootResponse(
            pod_name=pod,
            namespace=ns,
            detected_issue="Liveness / Readiness Probe Flapping Failure",
            root_cause="The health probe fired before application initialization completed or returned an HTTP error code, causing kubelet to repeatedly kill the container.",
            confidence="high",
            evidence=evidence,
            remediation_summary="Add a StartupProbe with generous failureThreshold (30 x 5s = 150s) to absorb application compilation or cache warming.",
            yaml_patch=yaml_patch,
            recommended_commands=[
                f"kubectl describe pod {pod} -n {ns} | grep -A 5 -i 'liveness'",
                f"kubectl logs {pod} -n {ns} --tail=100",
                f"kubectl rollout undo deployment/{pod.rsplit('-', 2)[0] if '-' in pod else 'app'} -n {ns}",
            ],
            preventative_guidance=[
                "Separate readiness probe (/ready) from liveness probe (/live). Liveness probe should only check process deadlocks, not downstream database latencies.",
            ],
        )

    def _diagnose_db_connection_refused(self, pod: str, ns: str, text: str) -> PodTroubleshootResponse:
        evidence = self._extract_evidence(text, [r"connection refused", r"econnrefused", r"failed to connect", r"is the server running", r"5432|3306|6379"])
        if not evidence:
            evidence = ["psycopg.OperationalError: connection to server at '127.0.0.1', port 5432 failed: Connection refused"]

        yaml_patch = (
            f"spec:\n"
            f"  template:\n"
            f"    spec:\n"
            f"      initContainers:\n"
            f"        - name: wait-for-db\n"
            f"          image: busybox:1.36\n"
            f"          command: ['sh', '-c', 'until nc -z -w 2 postgres.{ns}.svc.cluster.local 5432; do echo waiting for postgres; sleep 2; done;']\n"
            f"      containers:\n"
            f"        - name: app\n"
            f"          env:\n"
            f"            - name: DATABASE_URL\n"
            f"              value: 'postgresql://postgres:secret@postgres.{ns}.svc.cluster.local:5432/appdb'\n"
        )

        return PodTroubleshootResponse(
            pod_name=pod,
            namespace=ns,
            detected_issue="CrashLoopBackOff: Downstream Database Connection Refused",
            root_cause="Application attempted database handshake using localhost (127.0.0.1) or before the database pod was reachable on the cluster network.",
            confidence="high",
            evidence=evidence,
            remediation_summary="Update DATABASE_URL to use Kubernetes internal service DNS and add a lightweight initContainer to block boot until the DB TCP port responds.",
            yaml_patch=yaml_patch,
            recommended_commands=[
                f"kubectl get svc -n {ns}",
                f"kubectl logs {pod} -n {ns} -c app --previous",
                f"kubectl run debug-test --rm -i --tty --image=busybox -- nc -zv postgres.{ns}.svc.cluster.local 5432",
            ],
            preventative_guidance=[
                "Never hardcode 'localhost' or '127.0.0.1' for backing datastores inside containerized pods.",
                "Use Kubernetes CoreDNS service names: `<service-name>.<namespace>.svc.cluster.local`.",
            ],
        )

    def _diagnose_missing_config(self, pod: str, ns: str, text: str) -> PodTroubleshootResponse:
        evidence = self._extract_evidence(text, [r"configmap.*not found", r"secret.*not found", r"createcontainerconfigerror"])
        if not evidence:
            evidence = ["Error: configmap 'app-config' not found in namespace"]

        return PodTroubleshootResponse(
            pod_name=pod,
            namespace=ns,
            detected_issue="CreateContainerConfigError: Missing ConfigMap or Secret",
            root_cause="The Pod definition references a ConfigMap or Secret in envFrom or volumes that does not exist in the target namespace.",
            confidence="high",
            evidence=evidence,
            remediation_summary="Create the missing ConfigMap or Secret before starting container creation.",
            yaml_patch=None,
            recommended_commands=[
                f"kubectl get configmap,secret -n {ns}",
                f"kubectl apply -f configmap.yaml -n {ns}",
                f"kubectl apply -f secret.yaml -n {ns}",
            ],
            preventative_guidance=[
                "Deploy configuration dependencies (ConfigMaps, Secrets, PVCs) prior to deploying Pods and Deployments.",
            ],
        )

    def _diagnose_general_crash(self, pod: str, ns: str, text: str) -> PodTroubleshootResponse:
        evidence = self._extract_evidence(text, [r"crashloopbackoff", r"error", r"fatal", r"exception", r"exit status"])
        if not evidence:
            evidence = ["Container terminated with non-zero exit status during bootstrap"]

        return PodTroubleshootResponse(
            pod_name=pod,
            namespace=ns,
            detected_issue="CrashLoopBackOff: Container Process Exited on Startup",
            root_cause="The container entrypoint script exited with a non-zero code. Likely caused by missing environment variable, incorrect file path, or unhandled exception.",
            confidence="medium",
            evidence=evidence,
            remediation_summary="Inspect previous container logs using `kubectl logs --previous` and verify mandatory environment variables.",
            yaml_patch=None,
            recommended_commands=[
                f"kubectl logs {pod} -n {ns} --previous --tail=100",
                f"kubectl describe pod {pod} -n {ns} | grep -A 10 'Last State:'",
                f"kubectl debug pod/{pod} -n {ns} -it --image=busybox:1.36 --target=app",
            ],
            preventative_guidance=[
                "Add defensive error handling around entrypoint configuration loading and log specific validation failures.",
            ],
        )

    def _extract_evidence(self, text: str, patterns: List[str]) -> List[str]:
        evidence: List[str] = []
        lines = text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            for pat in patterns:
                if re.search(pat, line_str, re.IGNORECASE):
                    evidence.append(line_str)
                    break
            if len(evidence) >= 5:
                break
        return evidence
