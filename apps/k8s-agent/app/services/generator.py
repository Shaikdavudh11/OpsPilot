import re
from typing import List

try:
    from app.schemas.k8s import DetectedStack, GeneratedManifests, DeploymentStep, K8sAnalysisResponse
except (ImportError, ModuleNotFoundError):
    from ..schemas.k8s import DetectedStack, GeneratedManifests, DeploymentStep, K8sAnalysisResponse


class K8sManifestGenerator:
    """Generates production-grade Kubernetes manifests, Dockerfile, and deployment plans."""

    def __init__(
        self,
        app_name: str,
        namespace: str,
        stack: DetectedStack,
        target_port: int = None,
        image_name: str = None,
    ):
        clean_name = re.sub(r"[^a-z0-9-]", "-", app_name.lower().strip()).strip("-")
        self.app_name = clean_name if clean_name else "production-app"
        self.namespace = namespace.strip() if namespace else "default"
        self.stack = stack
        self.port = target_port or stack.recommended_port or 8080
        self.image_name = image_name or f"myregistry.azurecr.io/{self.app_name}:v1.0.0"

    def generate_all(self, repo_source: str, repo_ref: str) -> K8sAnalysisResponse:
        dockerfile = self._generate_dockerfile()
        deployment = self._generate_deployment()
        service = self._generate_service()
        configmap = self._generate_configmap()
        secret = self._generate_secret()
        ingress = self._generate_ingress()
        hpa = self._generate_hpa()

        all_in_one = (
            f"# ================================================================\n"
            f"# OpsPilot Generated Production Kubernetes Manifest Bundle\n"
            f"# Application: {self.app_name} | Namespace: {self.namespace}\n"
            f"# ================================================================\n\n"
            f"{configmap}\n---\n"
            f"{secret}\n---\n"
            f"{service}\n---\n"
            f"{deployment}\n---\n"
            f"{ingress}\n---\n"
            f"{hpa}\n"
        )

        manifests = GeneratedManifests(
            dockerfile=dockerfile,
            deployment_yaml=deployment,
            service_yaml=service,
            configmap_yaml=configmap,
            secret_yaml=secret,
            ingress_yaml=ingress,
            hpa_yaml=hpa,
            all_in_one_yaml=all_in_one,
        )

        steps = self._generate_deployment_steps()
        recommendations = self._generate_recommendations()
        hardening = self._generate_security_hardening()

        return K8sAnalysisResponse(
            app_name=self.app_name,
            namespace=self.namespace,
            repo_source=repo_source,
            repo_reference=repo_ref,
            detected_stack=self.stack,
            manifests=manifests,
            deployment_steps=steps,
            production_recommendations=recommendations,
            security_hardening=hardening,
        )

    def _generate_dockerfile(self) -> str:
        lang = self.stack.primary_language.lower()
        framework = self.stack.framework.lower()

        if "python" in lang:
            return (
                f"# OpsPilot Production Multi-Stage Dockerfile for {self.stack.framework}\n"
                f"FROM python:3.12-slim AS builder\n"
                f"WORKDIR /app\n"
                f"RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*\n"
                f"COPY requirements.txt .\n"
                f"RUN pip install --no-cache-dir --user -r requirements.txt\n\n"
                f"FROM python:3.12-slim AS runner\n"
                f"WORKDIR /app\n"
                f"ENV PYTHONUNBUFFERED=1 \\\n"
                f"    PYTHONDONTWRITEBYTECODE=1 \\\n"
                f"    PATH=/home/appuser/.local/bin:$PATH \\\n"
                f"    PORT={self.port}\n\n"
                f"RUN groupadd -g 10001 appgroup && \\\n"
                f"    useradd -u 10001 -g appgroup -s /bin/bash -m appuser\n\n"
                f"COPY --from=builder /root/.local /home/appuser/.local\n"
                f"COPY --chown=appuser:appgroup . .\n\n"
                f"USER 10001\n"
                f"EXPOSE {self.port}\n\n"
                f"CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"{self.port}\"]\n"
            )

        if "node" in lang or "typescript" in lang or "javascript" in lang:
            if "next" in framework:
                return (
                    f"# OpsPilot Production Multi-Stage Dockerfile for Next.js\n"
                    f"FROM node:20-alpine AS deps\n"
                    f"WORKDIR /app\n"
                    f"RUN apk add --no-cache libc6-compat\n"
                    f"COPY package.json package-lock.json* ./\n"
                    f"RUN npm ci\n\n"
                    f"FROM node:20-alpine AS builder\n"
                    f"WORKDIR /app\n"
                    f"COPY --from=deps /app/node_modules ./node_modules\n"
                    f"COPY . .\n"
                    f"ENV NEXT_TELEMETRY_DISABLED=1\n"
                    f"RUN npm run build\n\n"
                    f"FROM node:20-alpine AS runner\n"
                    f"WORKDIR /app\n"
                    f"ENV NODE_ENV=production \\\n"
                    f"    PORT={self.port} \\\n"
                    f"    NEXT_TELEMETRY_DISABLED=1\n\n"
                    f"RUN addgroup --system --gid 1001 nodejs && \\\n"
                    f"    adduser --system --uid 1001 nextjs\n\n"
                    f"COPY --from=builder /app/public ./public\n"
                    f"COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./\n"
                    f"COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static\n\n"
                    f"USER 1001\n"
                    f"EXPOSE {self.port}\n\n"
                    f"CMD [\"node\", \"server.js\"]\n"
                )
            else:
                return (
                    f"# OpsPilot Production Multi-Stage Dockerfile for Node.js / {self.stack.framework}\n"
                    f"FROM node:20-alpine AS builder\n"
                    f"WORKDIR /app\n"
                    f"COPY package*.json ./\n"
                    f"RUN npm ci\n"
                    f"COPY . .\n"
                    f"RUN npm run build --if-present\n\n"
                    f"FROM node:20-alpine AS runner\n"
                    f"WORKDIR /app\n"
                    f"ENV NODE_ENV=production PORT={self.port}\n"
                    f"RUN addgroup -S appgroup -g 10001 && adduser -S appuser -u 10001 -G appgroup\n"
                    f"COPY package*.json ./\n"
                    f"RUN npm ci --only=production\n"
                    f"COPY --from=builder --chown=appuser:appgroup /app/dist ./dist\n"
                    f"USER 10001\n"
                    f"EXPOSE {self.port}\n"
                    f"CMD [\"node\", \"dist/index.js\"]\n"
                )

        if "go" in lang:
            return (
                f"# OpsPilot Production Multi-Stage Dockerfile for Go\n"
                f"FROM golang:1.23-alpine AS builder\n"
                f"WORKDIR /src\n"
                f"RUN apk add --no-cache git ca-certificates\n"
                f"COPY go.mod go.sum* ./\n"
                f"RUN go mod download\n"
                f"COPY . .\n"
                f"RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags=\"-s -w\" -o /bin/server .\n\n"
                f"FROM scratch\n"
                f"COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/\n"
                f"COPY --from=builder /bin/server /bin/server\n"
                f"USER 10001:10001\n"
                f"EXPOSE {self.port}\n"
                f"ENTRYPOINT [\"/bin/server\"]\n"
            )

        if "java" in lang:
            return (
                f"# OpsPilot Production Multi-Stage Dockerfile for Spring Boot / Java\n"
                f"FROM maven:3.9-eclipse-temurin-21-alpine AS builder\n"
                f"WORKDIR /app\n"
                f"COPY pom.xml .\n"
                f"RUN mvn dependency:go-offline\n"
                f"COPY src ./src\n"
                f"RUN mvn clean package -DskipTests\n\n"
                f"FROM eclipse-temurin:21-jre-alpine AS runner\n"
                f"WORKDIR /app\n"
                f"RUN addgroup -S spring && adduser -S spring -G spring\n"
                f"COPY --from=builder --chown=spring:spring /app/target/*.jar app.jar\n"
                f"USER spring\n"
                f"EXPOSE {self.port}\n"
                f"ENTRYPOINT [\"java\", \"-XX:+UseContainerSupport\", \"-XX:MaxRAMPercentage=75.0\", \"-jar\", \"app.jar\"]\n"
            )

        return (
            f"FROM alpine:3.20\n"
            f"WORKDIR /app\n"
            f"RUN adduser -D -u 10001 appuser\n"
            f"COPY . .\n"
            f"USER 10001\n"
            f"EXPOSE {self.port}\n"
            f"CMD [\"./run.sh\"]\n"
        )

    def _generate_deployment(self) -> str:
        health_path = self.stack.health_endpoint or "/health"
        cpu_req = "100m"
        mem_req = "128Mi"
        cpu_lim = "500m"
        mem_lim = "512Mi"

        if "java" in self.stack.primary_language.lower():
            mem_req = "512Mi"
            mem_lim = "1Gi"
        elif "next" in self.stack.framework.lower():
            mem_req = "256Mi"
            mem_lim = "512Mi"

        return (
            f"apiVersion: apps/v1\n"
            f"kind: Deployment\n"
            f"metadata:\n"
            f"  name: {self.app_name}\n"
            f"  namespace: {self.namespace}\n"
            f"  labels:\n"
            f"    app.kubernetes.io/name: {self.app_name}\n"
            f"    app.kubernetes.io/part-of: {self.app_name}-platform\n"
            f"    app.kubernetes.io/managed-by: opspilot\n"
            f"spec:\n"
            f"  replicas: 2\n"
            f"  strategy:\n"
            f"    type: RollingUpdate\n"
            f"    rollingUpdate:\n"
            f"      maxSurge: 1\n"
            f"      maxUnavailable: 0\n"
            f"  selector:\n"
            f"    matchLabels:\n"
            f"      app: {self.app_name}\n"
            f"  template:\n"
            f"    metadata:\n"
            f"      labels:\n"
            f"        app: {self.app_name}\n"
            f"        app.kubernetes.io/name: {self.app_name}\n"
            f"    spec:\n"
            f"      securityContext:\n"
            f"        runAsNonRoot: true\n"
            f"        runAsUser: 10001\n"
            f"        runAsGroup: 10001\n"
            f"        fsGroup: 10001\n"
            f"        seccompProfile:\n"
            f"          type: RuntimeDefault\n"
            f"      affinity:\n"
            f"        podAntiAffinity:\n"
            f"          preferredDuringSchedulingIgnoredDuringExecution:\n"
            f"            - weight: 100\n"
            f"              podAffinityTerm:\n"
            f"                labelSelector:\n"
            f"                  matchExpressions:\n"
            f"                    - key: app\n"
            f"                      operator: In\n"
            f"                      values:\n"
            f"                        - {self.app_name}\n"
            f"                topologyKey: topology.kubernetes.io/zone\n"
            f"      containers:\n"
            f"        - name: {self.app_name}\n"
            f"          image: {self.image_name}\n"
            f"          imagePullPolicy: IfNotPresent\n"
            f"          ports:\n"
            f"            - name: http\n"
            f"              containerPort: {self.port}\n"
            f"              protocol: TCP\n"
            f"          securityContext:\n"
            f"            allowPrivilegeEscalation: false\n"
            f"            readOnlyRootFilesystem: false\n"
            f"            capabilities:\n"
            f"              drop:\n"
            f"                - ALL\n"
            f"          resources:\n"
            f"            requests:\n"
            f"              cpu: {cpu_req}\n"
            f"              memory: {mem_req}\n"
            f"            limits:\n"
            f"              cpu: {cpu_lim}\n"
            f"              memory: {mem_lim}\n"
            f"          envFrom:\n"
            f"            - configMapRef:\n"
            f"                name: {self.app_name}-config\n"
            f"            - secretRef:\n"
            f"                name: {self.app_name}-secret\n"
            f"          startupProbe:\n"
            f"            httpGet:\n"
            f"              path: {health_path}\n"
            f"              port: http\n"
            f"            initialDelaySeconds: 5\n"
            f"            periodSeconds: 5\n"
            f"            failureThreshold: 12\n"
            f"          readinessProbe:\n"
            f"            httpGet:\n"
            f"              path: {health_path}\n"
            f"              port: http\n"
            f"            periodSeconds: 10\n"
            f"            timeoutSeconds: 3\n"
            f"            failureThreshold: 3\n"
            f"          livenessProbe:\n"
            f"            httpGet:\n"
            f"              path: {health_path}\n"
            f"              port: http\n"
            f"            periodSeconds: 15\n"
            f"            timeoutSeconds: 3\n"
            f"            failureThreshold: 3\n"
        )

    def _generate_service(self) -> str:
        return (
            f"apiVersion: v1\n"
            f"kind: Service\n"
            f"metadata:\n"
            f"  name: {self.app_name}\n"
            f"  namespace: {self.namespace}\n"
            f"  labels:\n"
            f"    app.kubernetes.io/name: {self.app_name}\n"
            f"spec:\n"
            f"  type: ClusterIP\n"
            f"  selector:\n"
            f"    app: {self.app_name}\n"
            f"  ports:\n"
            f"    - name: http\n"
            f"      port: 80\n"
            f"      targetPort: http\n"
            f"      protocol: TCP\n"
        )

    def _generate_configmap(self) -> str:
        lines = [
            f"apiVersion: v1",
            f"kind: ConfigMap",
            f"metadata:",
            f"  name: {self.app_name}-config",
            f"  namespace: {self.namespace}",
            f"data:",
            f"  ENVIRONMENT: \"production\"",
            f"  PORT: \"{self.port}\"",
            f"  LOG_LEVEL: \"info\"",
        ]

        for ev in self.stack.detected_env_vars:
            ev_upper = ev.upper()
            if not any(secret_kw in ev_upper for secret_kw in ["KEY", "SECRET", "PASSWORD", "TOKEN", "AUTH", "PASS"]):
                lines.append(f"  {ev}: \"production-value\"")

        return "\n".join(lines) + "\n"

    def _generate_secret(self) -> str:
        lines = [
            f"apiVersion: v1",
            f"kind: Secret",
            f"metadata:",
            f"  name: {self.app_name}-secret",
            f"  namespace: {self.namespace}",
            f"type: Opaque",
            f"stringData:",
        ]

        sensitive_found = False
        for ev in self.stack.detected_env_vars:
            ev_upper = ev.upper()
            if any(secret_kw in ev_upper for secret_kw in ["KEY", "SECRET", "PASSWORD", "TOKEN", "AUTH", "PASS", "DATABASE_URL"]):
                lines.append(f"  {ev}: \"CHANGE_ME_IN_PRODUCTION\"")
                sensitive_found = True

        if not sensitive_found:
            lines.append("  APP_SECRET_KEY: \"CHANGE_ME_IN_PRODUCTION\"")

        lines.append("  # NOTE: Replace with HashiCorp Vault or Kubernetes SealedSecrets for zero-trust production.")
        return "\n".join(lines) + "\n"

    def _generate_ingress(self) -> str:
        return (
            f"apiVersion: networking.k8s.io/v1\n"
            f"kind: Ingress\n"
            f"metadata:\n"
            f"  name: {self.app_name}-ingress\n"
            f"  namespace: {self.namespace}\n"
            f"  annotations:\n"
            f"    kubernetes.io/ingress.class: nginx\n"
            f"    cert-manager.io/cluster-issuer: letsencrypt-prod\n"
            f"    nginx.ingress.kubernetes.io/proxy-body-size: 32m\n"
            f"spec:\n"
            f"  tls:\n"
            f"    - hosts:\n"
            f"        - {self.app_name}.yourdomain.com\n"
            f"      secretName: {self.app_name}-tls-cert\n"
            f"  rules:\n"
            f"    - host: {self.app_name}.yourdomain.com\n"
            f"      http:\n"
            f"        paths:\n"
            f"          - path: /\n"
            f"            pathType: Prefix\n"
            f"            backend:\n"
            f"              service:\n"
            f"                name: {self.app_name}\n"
            f"                port:\n"
            f"                  number: 80\n"
        )

    def _generate_hpa(self) -> str:
        return (
            f"apiVersion: autoscaling/v2\n"
            f"kind: HorizontalPodAutoscaler\n"
            f"metadata:\n"
            f"  name: {self.app_name}-hpa\n"
            f"  namespace: {self.namespace}\n"
            f"spec:\n"
            f"  scaleTargetRef:\n"
            f"    apiVersion: apps/v1\n"
            f"    kind: Deployment\n"
            f"    name: {self.app_name}\n"
            f"  minReplicas: 2\n"
            f"  maxReplicas: 10\n"
            f"  metrics:\n"
            f"    - type: Resource\n"
            f"      resource:\n"
            f"        name: cpu\n"
            f"        target:\n"
            f"          type: Utilization\n"
            f"          averageUtilization: 75\n"
            f"    - type: Resource\n"
            f"      resource:\n"
            f"        name: memory\n"
            f"        target:\n"
            f"          type: Utilization\n"
            f"          averageUtilization: 80\n"
        )

    def _generate_deployment_steps(self) -> List[DeploymentStep]:
        return [
            DeploymentStep(
                step_number=1,
                title="Build and Push Container Image",
                description="Build the multi-stage Docker image using the generated Dockerfile, tag it with your registry URL, and push to container registry.",
                commands=[
                    f"docker build -t {self.image_name} -f Dockerfile .",
                    f"docker push {self.image_name}",
                ],
                verification=f"docker image inspect {self.image_name} --format '{{{{.Size}}}}'",
            ),
            DeploymentStep(
                step_number=2,
                title="Create Namespace and Config Secrets",
                description=f"Provision the target namespace '{self.namespace}' and apply sensitive production secrets before deploying workloads.",
                commands=[
                    f"kubectl create namespace {self.namespace} --dry-run=client -o yaml | kubectl apply -f -",
                    f"kubectl apply -f secret.yaml -n {self.namespace}",
                    f"kubectl apply -f configmap.yaml -n {self.namespace}",
                ],
                verification=f"kubectl get secret,configmap -n {self.namespace}",
            ),
            DeploymentStep(
                step_number=3,
                title="Deploy Workloads & Routing",
                description="Apply Service, Deployment, HorizontalPodAutoscaler, and Ingress manifests.",
                commands=[
                    f"kubectl apply -f service.yaml -n {self.namespace}",
                    f"kubectl apply -f deployment.yaml -n {self.namespace}",
                    f"kubectl apply -f hpa.yaml -n {self.namespace}",
                    f"kubectl apply -f ingress.yaml -n {self.namespace}",
                ],
                verification=f"kubectl get deployments,services,hpa -n {self.namespace}",
            ),
            DeploymentStep(
                step_number=4,
                title="Verify Rollout & High Availability",
                description="Monitor rolling deployment status and smoke-test HTTP endpoint response via local port-forwarding.",
                commands=[
                    f"kubectl rollout status deployment/{self.app_name} -n {self.namespace} --timeout=120s",
                    f"kubectl get pods -n {self.namespace} -l app={self.app_name} -o wide",
                    f"kubectl port-forward svc/{self.app_name} 8080:80 -n {self.namespace} &",
                    f"curl -I http://localhost:8080{self.stack.health_endpoint or '/health'}",
                ],
                verification="Check that all pods show Running status (Ready: 1/1) and curl returns HTTP 200 OK.",
            ),
        ]

    def _generate_recommendations(self) -> List[str]:
        recs = [
            f"Configure HorizontalPodAutoscaler (HPA) targeting 75% CPU to absorb sudden traffic surges.",
            f"Use multi-AZ topology Spread Constraints across failure zones to survive node or rack outages.",
            f"Configure StartupProbe with 12 retries (60s total grace) to prevent premature kill signals during JVM or heavy startup cycles.",
            f"Enable Prometheus metrics scraping via annotations or ServiceMonitor for Grafana dashboards.",
        ]
        if self.stack.backing_services:
            recs.append(
                f"Detected dependencies on {', '.join(self.stack.backing_services)}. Implement connection poolers (e.g., PgBouncer) and circuit-breakers."
            )
        return recs

    def _generate_security_hardening(self) -> List[str]:
        return [
            "Non-Root User Enforcement: Pod runs under UID 10001 with drop: [ALL] Linux capabilities.",
            "Immutable Infrastructure: Recommended readOnlyRootFilesystem with emptyDir tmpfs for temporary cache directories.",
            "NetworkPolicy Isolation: Restrict ingress/egress to allow only inbound traffic from the Ingress Controller and outbound to database subnets.",
            "Zero Plaintext Secrets: Integrate External Secrets Operator (ESO) with AWS Secrets Manager or HashiCorp Vault.",
            "Container Vulnerability Scanning: Run Trivy or Grype in your CI/CD pipeline prior to image registry push.",
        ]
