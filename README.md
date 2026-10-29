# Automated Login Testing with Jenkins, Docker and Selenium

A small college DevOps lab: submit Flask login and registration forms, run 17 tests with
Selenium, and let Jenkins build the containers and publish the test result.
Allow about 3 hours, including installation and image downloads.

**Demo login:** `admin@example.com` / `admin123`. Credentials live in `app/app.py`.
This is a demonstration form, with no database, sessions or production authentication.
Flask's development server is sufficient for this local lab.

## In-place upgrade

The existing Dockerfiles, Compose services/environment/health checks, dependencies
and Jenkinsfile are unchanged. Keep using your existing Jenkins job and parameters.

- Login: email/password, show/hide password, remember-me checkbox and field validation.
- Remember-me: its checked state and email survive form submission; no cookie or
  persistent authentication is implemented.
- Forgot-password: displays fixed demo instructions; no email is sent.
- Registration: full name, email, password (minimum 8 characters), confirmation,
  exactly 10 phone digits, and required terms acceptance. Nothing is stored, so
  registration does not create a usable login. Use the configured demo login.
- Validation runs in Flask; forms use `novalidate` to make displayed messages
  consistent across browsers. Password fields are cleared after each submission.

The 17 independent Selenium cases cover seven login outcomes, password visibility,
remember-me, forgot-password navigation, and seven registration outcomes: success,
empty fields, invalid email, short password, mismatch, invalid phone and missing terms.
Every case creates and closes its own browser; none depends on registration state.

For this installation Docker is under the current user's application directory.
If `docker` is missing from this PowerShell's PATH, use:

```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:PATH"
```

To rebuild and test the upgrade without replacing the working CI setup:

```powershell
Set-Location 'C:\Users\raksh\Desktop\DevOps-Lab-Project'
docker compose --profile testing config --quiet
docker compose build app
docker compose up -d --wait --wait-timeout 180 app selenium
New-Item -ItemType Directory -Force reports | Out-Null
docker compose run --rm --volume "${PWD}/reports:/project/reports" tests
$testExit = $LASTEXITCODE
Write-Host "pytest exit code: $testExit"
```

Then open the **existing** Jenkins job, select **Build with Parameters**, keep the
same `LOCAL_PROJECT_PATH` used for Build #3, and click **Build**. For SCM jobs,
commit/push these changes first. Expect **17 passed** and 17 results in Jenkins's
Test Result view. The unchanged Jenkinsfile still prints the legacy text
`SUCCESS: all four login tests passed.`; use the actual pytest/JUnit count.
You do not need to recreate the job or paste a new pipeline script.

## Tools and workflow

| Tool | Purpose |
| --- | --- |
| Python + Flask | Serve the login page and validate submitted credentials |
| HTML + CSS | Simple form with stable element IDs |
| Selenium | Drive headless Chrome and check the displayed messages |
| pytest | Run 17 cases, return an exit code and write JUnit XML |
| Docker + Compose | Build the app image and connect the three services |
| Jenkins | Build, start, wait, test, publish reports and clean up |
| Git (optional) | Store source and let Jenkins check it out |

```text
Windows browser ---> localhost:5000 ---> app (Flask)

Jenkins ---> Docker Compose
               |-- app:5000          <--- Chrome opens this address
               |-- selenium:4444     <--- tests send WebDriver commands here
               `-- tests (pytest) ---> reports/results.xml ---> Jenkins
```

Compose provides the service names `app` and `selenium` on its private network.
Inside Chrome's container, `localhost` means Chrome's own container. Tests use the
unchanged `BASE_URL` and `SELENIUM_REMOTE_URL` supplied by your working Compose file;
the test code never constructs container names. Only Flask is published to Windows.
The app and test runner share a small Python image to avoid a second Dockerfile.

## Files

```text
DevOps-Lab-Project/
  app/
    app.py
    templates/login.html
    templates/base.html
    templates/register.html
    templates/forgot_password.html
    static/style.css
    static/login.js
  tests/test_login.py
  jenkins/Dockerfile          # optional Jenkins container with Docker CLI
  requirements.txt
  Dockerfile
  docker-compose.yml
  Jenkinsfile
  .gitignore
  .dockerignore
  README.md
  VALIDATION.md
```

## Prerequisites

1. Windows 10/11 with virtualization and WSL 2 supported/enabled.
2. Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/),
   start it, and use **Linux containers**. Allocate enough memory for Chrome and
   Jenkins (about 4 GB available to Docker is a useful starting point).
3. Use the Compose V2 plugin supplied by Docker Desktop. If `--wait` is unknown,
   update Docker Desktop.
4. Internet access for the first image pulls and Python downloads.
5. For the optional local Python route: Python 3.12 and Google Chrome.
6. For native Jenkins: a supported Java runtime (Java 21 for the current LTS),
   and the Jenkins LTS WAR. The container route below includes Java.

Check Docker before starting:

```powershell
Set-Location 'C:\Users\raksh\Desktop\DevOps-Lab-Project'
docker version
docker compose version
```

`docker version` must show both Client and Server. Installing only a CLI is insufficient.
Check [Jenkins Java requirements](https://www.jenkins.io/doc/book/platform-information/support-policy-java/)
if using another Jenkins version.

## Start and stop the application

Run from the project folder in PowerShell:

```powershell
docker compose up -d --build --wait --wait-timeout 180 app selenium
docker compose ps
Start-Process 'http://localhost:5000'
```

Enter `admin@example.com` and `admin123`, then try a wrong password. Containers remain running
in the background. Image downloads may take several minutes on the first run.

Stop and remove this lab's containers and network:

```powershell
docker compose --profile testing down --remove-orphans
```

## Run the 17 tests in Docker (recommended)

After the start command above, run:

```powershell
New-Item -ItemType Directory -Force reports | Out-Null
docker compose run --rm --volume "${PWD}/reports:/project/reports" tests
$testExit = $LASTEXITCODE
Write-Host "pytest exit code: $testExit"
Get-Content .\reports\results.xml
```

The runner is disposable; `--rm` removes it. The bind mount keeps its report in
your Windows project folder. Tests use headless Chrome inside Selenium's container;
no browser window or manual interaction is required. The command also waits for
healthy dependencies; it still needs the image built by the start command.

Expected summary (times vary):

```text
test_login[valid-login] PASSED
test_login[wrong-password] PASSED
test_login[unknown-email] PASSED
... remaining login, interaction and registration cases ...
test_registration[terms-required] PASSED
==================== 17 passed in ... ====================
pytest exit code: 0
```

The full pytest output includes the test file/function names. Failed assertions
produce `FAILED`, exit code `1`, and failure details in `reports/results.xml`.
Browser/setup failures usually appear as `ERROR`; these also return nonzero.

## Run locally without Docker (optional)

This route uses your installed Chrome and Selenium Manager's matching driver.
The first run may need internet access to obtain the driver. No activation script
is necessary, avoiding PowerShell execution-policy problems.

PowerShell window 1:

```powershell
Set-Location 'C:\Users\raksh\Desktop\DevOps-Lab-Project'
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app\app.py
```

PowerShell window 2:

```powershell
Set-Location 'C:\Users\raksh\Desktop\DevOps-Lab-Project'
Remove-Item Env:SELENIUM_REMOTE_URL -ErrorAction SilentlyContinue
$env:BASE_URL = 'http://localhost:5000'
.\.venv\Scripts\python.exe -m pytest tests -v --junitxml=reports/results.xml
Write-Host "pytest exit code: $LASTEXITCODE"
```

Stop Flask with **Ctrl+C** in window 1. Stop the Docker app first if port 5000 is
already in use. Never run the local Flask server and Docker app on the same port.

## Jenkins setup: choose ONE route

The pipeline uses ordinary Docker CLI commands, so it needs **Pipeline** and
**JUnit** plugins, plus **Git** only when using SCM. Docker Pipeline plugin is not
required. Installing suggested plugins during Jenkins setup is fine.

### A. Native Windows Jenkins (simple if Java 21 is already installed)

Download the LTS `jenkins.war` from [Jenkins downloads](https://www.jenkins.io/download/).
Run Jenkins from PowerShell under your logged-in user, with Docker Desktop running:

```powershell
java -version
docker version
java -jar "$HOME\Downloads\jenkins.war" --httpPort=8080
```

Leave that window open. Visit `http://localhost:8080`, use the initial password
printed in the console (also in `$HOME\.jenkins\secrets\initialAdminPassword`),
install plugins and create an admin account. This avoids Windows service-account
Docker permissions during a short lab. A Jenkins Windows service needs its own
Docker access and updated PATH; commands working for your user do not prove that
the service can run them. Restart Jenkins after changing PATH.

### B. Jenkins in Docker (includes Java and Docker CLI)

The stock Jenkins image does **not** automatically include the Docker CLI or
Compose. The included `jenkins/Dockerfile` adds both, plus Buildx. Run from this
project's PowerShell folder:

```powershell
docker build -t login-lab-jenkins -f jenkins/Dockerfile .
docker run -d --name login-lab-jenkins --user root -p 127.0.0.1:8080:8080 --mount type=volume,source=login-lab-jenkins-home,target=/var/jenkins_home --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock --mount "type=bind,source=${PWD},target=/lab-source,readonly" login-lab-jenkins
docker exec login-lab-jenkins docker version
docker exec login-lab-jenkins docker compose version
docker exec login-lab-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Use Docker Desktop's Linux-container engine. Its Unix socket lets this container
control the same engine as Windows Docker commands; no nested daemon or TCP port
2375 is needed. Running as root avoids socket group-permission setup for this local
lab. Socket access grants control over Docker and mounted files: use this only for
your trusted local lab. Do not expose this Jenkins instance publicly.

Open `http://localhost:8080` and complete setup. Source is available inside Jenkins
at `/lab-source`, not at a Windows `C:\...` path. Jenkins copies source into its own
workspace; reports are copied out of the runner with `docker cp`. This avoids the
common problem where a sibling container cannot bind-mount Jenkins's internal
workspace path from Docker Desktop's host filesystem.

Stop Jenkins separately when finished (keeps setup in its named volume):

```powershell
docker stop login-lab-jenkins
docker rm login-lab-jenkins
```

Repeat the `docker run` command to restart with the same settings. The Compose
cleanup command does not remove the Jenkins container or its named home volume.

## Create and trigger the pipeline without GitHub

1. Jenkins: **New Item** → name `login-lab` → **Pipeline** → **OK**.
2. Under **Pipeline**, choose **Pipeline script**.
3. Paste the entire workspace `Jenkinsfile` into the script box.
4. Save and click **Build Now** once. The first run registers the parameter and
   may fail with “Source missing”; this is expected before you supply the path.
5. Click **Build with Parameters**. For `LOCAL_PROJECT_PATH`, enter:
   - Native Windows Jenkins: `C:\Users\raksh\Desktop\DevOps-Lab-Project`
   - Container Jenkins from route B: `/lab-source`
6. Click **Build** → build number → **Console Output**.
7. Expect stages **Source**, **Build image**, **Start and wait**, **Selenium tests**,
   then `SUCCESS: all four login tests passed.`
8. Open the build's **Test Result** and **Artifacts → reports/results.xml**.

Use a source folder separate from the Jenkins workspace. If source is already in
the agent's workspace, leave the parameter blank. Changes to the Jenkinsfile in
script mode must also be pasted into the job configuration.

With Git: commit/push the files, choose **Pipeline script from SCM → Git**, enter
the repository URL/branch and script path `Jenkinsfile`. Leave `LOCAL_PROJECT_PATH`
blank. Jenkins checks out SCM itself. No GitHub account is needed for local mode.

CI uses a separate Compose project for each build and an automatically allocated
host port, so your manual localhost:5000 demo can stay running. The pipeline waits
for both health checks, preserves pytest's failure exit code, collects XML before
removing the test runner, and cleans containers even if a stage fails. A startup
failure before pytest runs has no test XML; use Console Output and service logs.

## Show a controlled failure, then recover

1. First obtain a passing build.
2. In `app/app.py`, temporarily change `DEMO_PASSWORD="admin123"` to
   `DEMO_PASSWORD="changed-for-demo"`.
3. Rebuild through Jenkins. The valid-login test still submits `admin123`, so it
   fails. Console Output shows `FAILED`, the build shows **FAILURE**, and the XML
   report contains the failed assertion. Containers are still cleaned up.
4. Restore `admin123` and rebuild: all 17 tests pass again.

In SCM mode, commit/push each change before building. In local-path mode, Jenkins
copies your current files on every build. For a manual Docker failure demo, repeat
the start command with `--build`, then run the Docker test command again.

## Common errors

| Symptom | Fix |
| --- | --- |
| `docker` not recognized | Install Docker Desktop, reopen PowerShell/Jenkins so PATH refreshes. |
| Cannot connect to Docker daemon | Start Desktop, wait for the engine, use Linux containers; run `docker version`. |
| `--wait` unknown | Update Docker Desktop/Compose V2. |
| Port 5000 already allocated | Stop local Flask or the earlier Compose project. Alternatively set `$env:APP_PORT='5001'` before starting and browse port 5001. |
| Selenium unhealthy or Chrome crashes | Allocate more memory; keep `shm_size: 2gb`; inspect `docker compose logs selenium`. |
| Chrome cannot reach app | Keep the working Compose `BASE_URL`; inside Chrome, localhost refers to its own container. |
| Local Chrome driver download fails | Check internet/proxy access or use the Docker test route. |
| Jenkins: `docker: not found` | Stock Jenkins lacks the CLI; use the supplied Jenkins Dockerfile or native Jenkins with Desktop on PATH. |
| Jenkins: socket permission denied | For the provided lab container use `--user root` and the socket mount; check `docker exec ... docker version`. |
| Jenkins: source missing | Set the correct agent-visible local source path; Windows paths do not work inside Linux Jenkins. |
| Jenkins: no such DSL method `junit` | Install the JUnit plugin under Manage Jenkins → Plugins. |
| Report missing | Read Console Output: pytest may not have started; verify startup health and Docker access. |
| Old page after editing | Rebuild the image with the start command; image contents do not change just because source changed. |
| Jenkins won't start with Java 17 | Use the supported runtime for your Jenkins release; current LTS requires Java 21 or later. |

Use `docker compose logs app selenium` for service logs. In CI, logs are printed
automatically before cleanup.

## Suggested 3-hour plan

| Time | Task |
| --- | --- |
| 0–40 min | Install/check tools, start app and try login manually |
| 40–80 min | Run the 17 Docker Selenium tests and inspect XML |
| 80–140 min | Start Jenkins, configure the job and obtain a passing build |
| 140–180 min | Demonstrate a failure/recovery and rehearse explanation/viva |

## 60-second explanation

“My project automates functional testing of a Flask login page. The application
compares submitted credentials with two demonstration values in its configuration.
Docker packages the application, and Docker Compose connects Flask, Selenium Chrome,
and a disposable pytest runner. Selenium runs 17 cases covering login credentials,
empty inputs, email format, browser controls and registration validation. It uses stable
HTML IDs and waits explicitly for the result. Jenkins builds the image, starts the
services, waits until they are healthy, and runs the tests. Pytest returns zero on
success and nonzero on failure, so Jenkins displays the build result. Jenkins also
publishes the JUnit test report and removes the containers. I can show a passing
build, deliberately change a credential to make a test fail, then restore it.”

## Likely viva questions

| Question | Short answer |
| --- | --- |
| What is CI? | Automatically building and testing changes to catch problems early. |
| What does Jenkins do here? | Orchestrates the build, readiness, tests, reporting and cleanup. |
| What is an image versus a container? | An image is a packaged template; a container is an instance of it. |
| Why Compose? | One file defines the services, networking and health checks. |
| Why Selenium? | It tests the form in a real browser, including rendering and user interaction. |
| What does pytest add? | Case execution, assertions, readable results, exit codes and XML reports. |
| What is headless Chrome? | Chrome running without a visible browser window. |
| Why explicit waits? | They wait for a condition up to a limit instead of assuming a fixed delay. |
| Why stable IDs? | IDs give the tests simple, reliable element locators. |
| Why not localhost inside Chrome? | It refers to Chrome's container; Compose resolves the app service name. |
| How does Jenkins know tests failed? | The Docker runner propagates pytest's nonzero exit code. |
| What is JUnit XML? | A test-result format Jenkins reads to show test counts and failures. |
| What happens after failure? | The post block copies reports and removes containers and the network. |
| Is this secure real authentication? | No; it intentionally uses demo credentials without sessions or a database. |

## Lab-record conclusion

Implemented Flask login and registration pages and automated 17 functional cases with Selenium
and pytest. Docker Compose defines the application, browser and test environment.
The Jenkins pipeline builds and tests the project, publishes results, and cleans up
resources. This demonstrates a basic continuous integration workflow.

See `VALIDATION.md` for checks actually run in this workspace and checks still
requiring Docker/Jenkins. A successful local run alone does not verify the CI setup.

## References

- [Docker Compose readiness and startup](https://docs.docker.com/reference/cli/docker/compose/up/)
- [Official Selenium container usage and health checks](https://github.com/SeleniumHQ/docker-selenium)
- [Jenkins test reports and artifacts](https://www.jenkins.io/doc/pipeline/tour/tests-and-artifacts/)
- [Jenkins Windows installation](https://www.jenkins.io/doc/book/installing/windows/)
