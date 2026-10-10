from typing import List
from fastapi import APIRouter
from app.schemas.incident import Severity
from app.schemas.scenario import DemoScenario

router = APIRouter()

DEMO_SCENARIOS: List[DemoScenario] = [
    DemoScenario(
        id="postgres-conn-refused",
        title="PostgreSQL Connection Refused",
        description="Production payment service fails to connect to database cluster on port 5432.",
        category="Database",
        environment="production",
        service_name="payment-processor",
        expected_severity=Severity.HIGH,
        raw_logs="""2026-10-10 11:14:02.102 [ERROR] [payment-processor] [thread-4] org.postgresql.util.PSQLException: Connection to db.prod.internal:5432 refused. Check that the hostname and port are correct and that the postmaster is accepting TCP/IP connections.
	at org.postgresql.core.v3.ConnectionFactoryImpl.openConnectionImpl(ConnectionFactoryImpl.java:319)
	at org.postgresql.core.ConnectionFactory.openConnection(ConnectionFactoryImpl.java:54)
	at org.postgresql.jdbc.PgConnection.<init>(PgConnection.java:242)
2026-10-10 11:14:02.104 [WARN] [payment-processor] HikariPool-1 - Connection is not available, request timed out after 30000ms.
2026-10-10 11:14:02.105 [FATAL] [payment-processor] Database connection pool exhausted. Aborting checkout transactions. Active connections: 0, Idle: 0, Pending: 84.""",
    ),
    DemoScenario(
        id="docker-startup-exit",
        title="Docker Container Exits During Startup",
        description="Containerized microservice crashes immediately upon `docker run` execution.",
        category="Docker",
        environment="staging",
        service_name="notification-worker",
        expected_severity=Severity.HIGH,
        raw_logs="""docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: exec: "/app/entrypoint.sh": permission denied: unknown.
2026-10-10T10:45:01.817291000Z standard_init_linux.go:228: exec user process caused: permission denied
2026-10-10T10:45:02.102000000Z Container notification-worker-inst-1 exited with status code 126
2026-10-10T10:45:02.115000000Z Healthcheck failed 3 consecutive times: container stopped.""",
    ),
    DemoScenario(
        id="k8s-crashloop-oom",
        title="Kubernetes CrashLoopBackOff (OOMKilled)",
        description="Analytics ingest pod exceeds cgroup memory ceiling and enters CrashLoopBackOff.",
        category="Kubernetes",
        environment="production",
        service_name="event-ingestor",
        expected_severity=Severity.CRITICAL,
        raw_logs="""2026-10-10T08:30:15Z kubelet Node worker-node-04: Task memory limit exceeded in cgroup /kubepods.slice/kubepods-burstable.slice/pod_event-ingestor-84b8d77bf-kx82j.
2026-10-10T08:30:15Z kernel: [194821.194] event-ingestor invoked oom-killer: gfp_mask=0x1100cca(GFP_HIGHUSER_MOVABLE), order=0, oom_score_adj=985
2026-10-10T08:30:15Z kernel: [194821.195] Memory cgroup out of memory: Killed process 384192 (event-ingestor) total-vm:2104524kB, anon-rss:1048128kB, file-rss:1024kB
2026-10-10T08:30:16Z kubelet Container event-ingestor in pod event-ingestor-84b8d77bf-kx82j was terminated with exit code 137 (Reason: OOMKilled).
2026-10-10T08:30:45Z kubelet Back-off restarting failed container event-ingestor in pod event-ingestor-84b8d77bf-kx82j_default(9c8e1a-42).
Status: CrashLoopBackOff (Restart Count: 6).""",
    ),
    DemoScenario(
        id="k8s-imagepull-backoff",
        title="Kubernetes ImagePullBackOff",
        description="Deployment cannot schedule pods due to missing image tag in private container registry.",
        category="Kubernetes",
        environment="production",
        service_name="customer-dashboard",
        expected_severity=Severity.HIGH,
        raw_logs="""Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  4m12s              default-scheduler  Successfully assigned default/customer-dashboard-5f968945f-m5mrp to ip-10-0-12-88
  Normal   Pulling    2m48s (x4 over 4m) kubelet            Pulling image "registry.internal.corp/frontend/customer-dashboard:v2.14.0-rc3"
  Warning  Failed     2m47s (x4 over 4m) kubelet            Failed to pull image "registry.internal.corp/frontend/customer-dashboard:v2.14.0-rc3": rpc error: code = NotFound desc = failed to pull and unpack image "registry.internal.corp/frontend/customer-dashboard:v2.14.0-rc3": failed to resolve reference: registry.internal.corp/frontend/customer-dashboard:v2.14.0-rc3: not found
  Warning  Failed     2m47s (x4 over 4m) kubelet            Error: ErrImagePull
  Normal   BackOff    2m34s (x6 over 4m) kubelet            Back-off pulling image "registry.internal.corp/frontend/customer-dashboard:v2.14.0-rc3"
  Warning  Failed     2m34s (x6 over 4m) kubelet            Error: ImagePullBackOff""",
    ),
    DemoScenario(
        id="ci-test-failure",
        title="GitHub Actions CI Test Failure",
        description="Automated regression test suite fails on PR validation pipeline.",
        category="CI/CD",
        environment="ci",
        service_name="api-gateway",
        expected_severity=Severity.MEDIUM,
        raw_logs="""Run pytest tests/ --junitxml=junit/test-results.xml
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.1.1
collected 42 items

tests/unit/test_auth.py ......                                           [ 14%]
tests/unit/test_routing.py ........F........                             [ 52%]

=================================== FAILURES ===================================
___________________________ test_rate_limiter_burst ____________________________

    def test_rate_limiter_burst():
        limiter = TokenBucketLimiter(capacity=10, refill_rate=1.0)
        for _ in range(10):
            assert limiter.acquire() is True
>       assert limiter.acquire() is False
E       AssertionError: assert True is False
E       +  where True = <bound method TokenBucketLimiter.acquire of <TokenBucketLimiter capacity=10 tokens=1.0>>()

tests/unit/test_routing.py:48: AssertionError
----------------------------- Captured stderr call -----------------------------
[ERROR] RateLimiter: Refill thread executed unexpectedly during lock window
=========================== short test summary info ============================
FAILED tests/unit/test_routing.py::test_rate_limiter_burst - AssertionError: assert True is False
1 failed, 41 passed in 4.12s
##[error]Process completed with exit code 1.""",
    ),
    DemoScenario(
        id="app-http-500",
        title="Application HTTP 500 Runtime Exception",
        description="Unhandled null reference in checkout request handler causes cascading 500 errors.",
        category="Application",
        environment="production",
        service_name="checkout-service",
        expected_severity=Severity.HIGH,
        raw_logs="""2026-10-10 14:02:11.891 [ERROR] [uvicorn.error] Exception in ASGI application
Traceback (most recent call last):
  File "/opt/venv/lib/python3.12/site-packages/starlette/middleware/errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "/app/services/checkout.py", line 87, in process_order
    user_discount = order_payload["discount_profile"]["discount_code"]
KeyError: 'discount_profile'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/api/v1/routes.py", line 142, in create_checkout_session
    result = await checkout_service.process_order(request_data)
TypeError: 'NoneType' object is not subscriptable
2026-10-10 14:02:11.895 [INFO] [access] 192.168.1.44 - "POST /api/v1/checkout HTTP/1.1" 500 Internal Server Error 45ms""",
    ),
]


@router.get(
    "/demo-scenarios",
    response_model=List[DemoScenario],
    summary="List preconfigured incident scenarios",
    description="Returns 6 realistic failure scenarios for log demonstration, training, and testing.",
)
def list_demo_scenarios() -> List[DemoScenario]:
    return DEMO_SCENARIOS
