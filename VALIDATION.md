# Upgrade validation performed on 29 October 2026

## Existing setup preserved

The user reported Jenkins Build #3 succeeded with the original four tests.
Before editing, inspected the current files and the running Compose services.
Docker Desktop is installed per-user under
`$env:LOCALAPPDATA\Programs\DockerDesktop`; its CLI was missing from this shell's
PATH but the Linux engine was running. The old note saying Docker was unavailable
is superseded by this validation.

SHA-256 checks before and after the upgrade confirm these files are unchanged:

- `Dockerfile`
- `docker-compose.yml`
- `Jenkinsfile`
- `requirements.txt`
- `jenkins/Dockerfile`

Service names, health checks, test profile, environment variables, image naming
and JUnit output path have therefore been preserved exactly.

## Checks executed successfully

Used Docker Engine 29.9.2 / Compose v5.6.1 and ran:

```powershell
docker compose --profile testing config --quiet
docker compose build app
docker compose up -d --wait --wait-timeout 180 app selenium
docker compose run --rm --volume "${PWD}/reports:/project/reports" tests
```

Both app and Selenium passed their existing health checks. The complete suite ran
inside the disposable test container against the existing remote Selenium Chrome
container using the unchanged Compose environment:

```text
17 passed in 14.64s
pytest exit code: 0
```

Parsed `reports/results.xml` and verified **17 tests, zero failures, zero errors**.
The report was produced by the containerized run, not by a substitute local test.

Additional Flask test-client checks passed for the login, registration, password
help, health and JavaScript routes; each individually missing registration field;
short, long, non-digit and international-format phone inputs; and normalized login
email casing/whitespace. Python compilation of `app` and `tests` also passed.

Captured login and registration screenshots from the rebuilt Docker application in
`reports/login-page.png` and `reports/registration-page.png` and inspected the form
layout. The app and Selenium were left running for demonstration at localhost:5000.

## Jenkins follow-up

No new Jenkins build was triggered during this upgrade. The reported successful
Build #3 predates these changes. Trigger the existing job using its existing source
path (or commit/push first for SCM mode) to verify the upgraded suite in Jenkins.
Its unchanged report command writes `reports/results.xml` as before.

The unchanged Jenkinsfile's success message still says “all four login tests
passed.” This is legacy display text; the new pytest/JUnit count is 17. No pipeline
edit is needed to discover or publish the expanded test suite.
