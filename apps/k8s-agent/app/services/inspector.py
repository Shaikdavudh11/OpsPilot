import os
import re
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional, Set

try:
    from app.schemas.k8s import DetectedStack
except (ImportError, ModuleNotFoundError):
    from ..schemas.k8s import DetectedStack


IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".next",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
    "vendor",
}


class RepoInspector:
    """Scans and analyzes a software repository to extract technology stack, ports, env vars, and architecture."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()

    @classmethod
    def clone_github_repo(cls, repo_url: str, branch: Optional[str] = "main") -> Tuple["RepoInspector", str]:
        """Clones a remote repository to a temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="opspilot_k8s_repo_")
        
        clean_url = repo_url.strip()
        if not clean_url.endswith(".git") and "github.com" in clean_url:
            clean_url = clean_url.rstrip("/") + ".git"

        cmd = ["git", "clone", "--depth", "1"]
        if branch:
            cmd.extend(["-b", branch])
        cmd.extend([clean_url, temp_dir])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode != 0:
                cmd_fallback = ["git", "clone", "--depth", "1", clean_url, temp_dir]
                res_fallback = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=30)
                if res_fallback.returncode != 0:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    raise ValueError(f"Failed to clone repository: {res_fallback.stderr or res.stderr}")
        except subprocess.TimeoutExpired:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError("Git clone timed out after 30 seconds.")
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError(f"Git clone error: {str(e)}")

        return cls(temp_dir), temp_dir

    def scan(self) -> DetectedStack:
        """Runs full repository inspection and returns detected stack info."""
        if not self.root_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.root_path}")

        files_found: List[str] = []
        total_scanned = 0

        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.root_path)
                files_found.append(rel_path)
                total_scanned += 1
                if total_scanned > 800:
                    break
            if total_scanned > 800:
                break

        language, framework, build_tool, package_files = self._detect_language_and_framework(files_found)
        detected_ports, recommended_port = self._detect_ports(files_found, framework, language)
        env_vars = self._detect_env_vars(files_found)
        backing_services = self._detect_backing_services(files_found)

        has_dockerfile = any(
            f.lower() == "dockerfile" or f.lower().startswith("dockerfile.")
            for f in files_found
        )
        has_existing_k8s = any(
            f.startswith("k8s/")
            or f.startswith("kubernetes/")
            or f.startswith("helm/")
            or f.endswith(".k8s.yaml")
            or f.endswith("Chart.yaml")
            for f in files_found
        )

        health_endpoint = self._detect_health_endpoint(files_found, framework)

        return DetectedStack(
            primary_language=language,
            framework=framework,
            build_tool=build_tool,
            detected_ports=detected_ports,
            recommended_port=recommended_port,
            has_dockerfile=has_dockerfile,
            has_existing_k8s=has_existing_k8s,
            detected_env_vars=env_vars,
            backing_services=backing_services,
            health_endpoint=health_endpoint,
            package_files_found=package_files,
            total_files_scanned=total_scanned,
        )

    def _detect_language_and_framework(self, files: List[str]) -> Tuple[str, str, Optional[str], List[str]]:
        pkg_files = []
        file_set = set(files)

        if any(f in file_set for f in ["requirements.txt", "Pipfile", "pyproject.toml", "setup.py"]):
            pkg_files.extend([f for f in ["requirements.txt", "Pipfile", "pyproject.toml", "setup.py"] if f in file_set])
            framework = "Python App"
            build_tool = "pip"
            if "pyproject.toml" in file_set:
                build_tool = "poetry/flit/uv"
            
            req_content = self._read_first_available(["requirements.txt", "pyproject.toml", "Pipfile"])
            if "fastapi" in req_content.lower():
                framework = "FastAPI"
            elif "flask" in req_content.lower():
                framework = "Flask"
            elif "django" in req_content.lower():
                framework = "Django"
            elif "celery" in req_content.lower():
                framework = "Celery Worker"

            return "Python", framework, build_tool, pkg_files

        if "package.json" in file_set:
            pkg_files.append("package.json")
            build_tool = "npm"
            if "pnpm-lock.yaml" in file_set:
                build_tool = "pnpm"
            elif "yarn.lock" in file_set:
                build_tool = "yarn"
            elif "bun.lockb" in file_set:
                build_tool = "bun"

            content = self._read_file("package.json")
            is_ts = "tsconfig.json" in file_set or any(f.endswith(".ts") or f.endswith(".tsx") for f in files)
            lang = "TypeScript" if is_ts else "JavaScript / Node.js"

            framework = "Node.js Application"
            if "next" in content:
                framework = "Next.js"
            elif "express" in content:
                framework = "Express.js"
            elif "@nestjs" in content:
                framework = "NestJS"
            elif "remix" in content:
                framework = "Remix"
            elif "fastify" in content:
                framework = "Fastify"

            return lang, framework, build_tool, pkg_files

        if "go.mod" in file_set:
            pkg_files.append("go.mod")
            mod_content = self._read_file("go.mod")
            framework = "Go Microservice"
            if "gin-gonic" in mod_content:
                framework = "Gin"
            elif "gofiber" in mod_content:
                framework = "Fiber"
            elif "labstack/echo" in mod_content:
                framework = "Echo"
            return "Go", framework, "go build", pkg_files

        if "pom.xml" in file_set:
            pkg_files.append("pom.xml")
            pom_content = self._read_file("pom.xml")
            framework = "Spring Boot" if "spring-boot" in pom_content else "Java Application"
            return "Java", framework, "Maven", pkg_files
        if "build.gradle" in file_set or "build.gradle.kts" in file_set:
            pkg_files.append("build.gradle")
            framework = "Spring Boot / Gradle"
            return "Java / Kotlin", framework, "Gradle", pkg_files

        if "Cargo.toml" in file_set:
            pkg_files.append("Cargo.toml")
            cargo_content = self._read_file("Cargo.toml")
            framework = "Rust Microservice"
            if "actix-web" in cargo_content:
                framework = "Actix Web"
            elif "axum" in cargo_content:
                framework = "Axum"
            return "Rust", framework, "cargo", pkg_files

        if "Gemfile" in file_set:
            pkg_files.append("Gemfile")
            gem_content = self._read_file("Gemfile")
            framework = "Ruby on Rails" if "rails" in gem_content else "Ruby App"
            return "Ruby", framework, "bundler", pkg_files

        return "Generic Container", "Standard Web Service", "docker", pkg_files

    def _detect_ports(self, files: List[str], framework: str, language: str) -> Tuple[List[int], int]:
        ports: Set[int] = set()
        port_pattern = re.compile(r"(?:PORT|port|Port)\s*[:=]\s*(\d{2,5})|listen\((\d{2,5})\)|EXPOSE\s+(\d{2,5})")

        target_candidates = [
            f for f in files
            if any(f.endswith(ext) for ext in [".json", ".env", ".env.example", ".yml", ".yaml", ".py", ".js", ".ts", ".go", "Dockerfile"])
            and not any(f.startswith(d) for d in ["tests", "docs", "test"])
        ][:30]

        for rel in target_candidates:
            content = self._read_file(rel)
            for match in port_pattern.finditer(content):
                for group in match.groups():
                    if group:
                        p = int(group)
                        if 80 <= p <= 65535 and p not in {5432, 3306, 6379, 27017, 9092}:
                            ports.add(p)

        default_port = 8080
        if framework == "Next.js":
            default_port = 3000
        elif framework in ["FastAPI", "Flask", "Django"]:
            default_port = 8000
        elif framework == "Express.js" or framework == "NestJS":
            default_port = 3000
        elif framework == "Spring Boot":
            default_port = 8080
        elif language == "Go":
            default_port = 8080

        sorted_ports = sorted(list(ports))
        rec_port = sorted_ports[0] if sorted_ports else default_port
        return sorted_ports, rec_port

    def _detect_env_vars(self, files: List[str]) -> List[str]:
        env_vars: Set[str] = set()

        env_files = [f for f in files if f in [".env.example", ".env", "docker-compose.yml", "docker-compose.yaml"]]
        for ef in env_files:
            content = self._read_file(ef)
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    if re.match(r"^[A-Z0-9_]{3,40}$", key):
                        env_vars.add(key)

        source_files = [
            f for f in files
            if any(f.endswith(ext) for ext in [".py", ".ts", ".js", ".go"])
            and not any(f.startswith(d) for d in ["tests", "docs"])
        ][:25]

        source_pattern = re.compile(r"process\.env\.([A-Z0-9_]+)|os\.(?:environ|getenv)\([\"']([A-Z0-9_]+)[\"']|os\.Getenv\([\"']([A-Z0-9_]+)[\"']")
        for sf in source_files:
            content = self._read_file(sf)
            for match in source_pattern.finditer(content):
                for g in match.groups():
                    if g and g not in {"PATH", "HOME", "USER", "SHELL"}:
                        env_vars.add(g)

        return sorted(list(env_vars))[:20]

    def _detect_backing_services(self, files: List[str]) -> List[str]:
        services: Set[str] = set()
        
        content_sample = ""
        sample_files = [
            f for f in files
            if f in ["package.json", "requirements.txt", "pyproject.toml", "go.mod", "docker-compose.yml", "pom.xml"]
        ]
        for sf in sample_files:
            content_sample += " " + self._read_file(sf).lower()

        if any(kw in content_sample for kw in ["postgres", "psycopg", "pg", "sqlalchemy"]):
            services.add("PostgreSQL")
        if any(kw in content_sample for kw in ["redis", "ioredis", "celery"]):
            services.add("Redis")
        if any(kw in content_sample for kw in ["mongodb", "mongoose", "pymongo"]):
            services.add("MongoDB")
        if any(kw in content_sample for kw in ["mysql", "pymysql", "mysql2"]):
            services.add("MySQL")
        if any(kw in content_sample for kw in ["kafka", "confluent-kafka"]):
            services.add("Kafka")
        if any(kw in content_sample for kw in ["rabbitmq", "amqp", "pika"]):
            services.add("RabbitMQ")

        return sorted(list(services))

    def _detect_health_endpoint(self, files: List[str], framework: str) -> str:
        source_files = [
            f for f in files
            if any(f.endswith(ext) for ext in [".py", ".ts", ".js", ".go"])
            and not any(f.startswith(d) for d in ["tests", "docs"])
        ][:20]

        patterns = [r"['\"](/healthz?)['\"]", r"['\"](/api/health)['\"]", r"['\"](/ping)['\"]", r"['\"](/ready)['\"]", r"['\"](/live)['\"]"]
        for sf in source_files:
            content = self._read_file(sf)
            for pat in patterns:
                match = re.search(pat, content)
                if match:
                    return match.group(1)

        if framework == "FastAPI" or framework == "Flask":
            return "/health"
        if framework == "Next.js":
            return "/"
        return "/health"

    def _read_file(self, rel_path: str, max_bytes: int = 15000) -> str:
        full_path = self.root_path / rel_path
        if not full_path.exists() or not full_path.is_file():
            return ""
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read(max_bytes)
        except Exception:
            return ""

    def _read_first_available(self, candidates: List[str]) -> str:
        for c in candidates:
            c_text = self._read_file(c)
            if c_text:
                return c_text
        return ""
