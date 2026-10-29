# DevOps Lab Project: Automated Web Application Testing

## Overview

This project demonstrates a Continuous Integration (CI) workflow for automated web application testing using Jenkins, Docker, Selenium, Python, and pytest.

A simple Flask-based login application is tested automatically using Selenium WebDriver and a Chrome browser running in a Docker container. Jenkins orchestrates the testing pipeline and publishes test results, helping identify application defects before changes are considered successful.

## Objectives

- Develop a simple web application using Flask.
- Automate functional testing with Selenium and pytest.
- Containerize the application and testing environment using Docker.
- Use Docker Compose to manage application, browser, and testing services.
- Configure a Jenkins pipeline to execute automated tests.
- Generate and publish JUnit test reports through Jenkins.
- Demonstrate how a failing test can cause a CI build to fail.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application and test development |
| Flask | Web application framework |
| HTML, CSS, JavaScript | Login interface and client-side interactions |
| Selenium WebDriver | Browser automation |
| pytest | Automated test execution |
| Docker | Containerization |
| Docker Compose | Service orchestration |
| Jenkins | Continuous Integration pipeline |
| Chrome | Browser used for automated testing |
| Git and GitHub | Version control and project hosting |

## Project Architecture

The project follows this workflow:

```text
Developer
    |
    v
Jenkins Pipeline
    |
    v
Docker Compose
    |
    +----------------------+
    |                      |
    v                      v
Flask Web Application   Selenium Chrome
    |                      |
    +----------+-----------+
               |
               v
       pytest Test Runner
               |
               v
       Automated Test Cases
               |
               v
        JUnit Test Report
               |
               v
       Jenkins Build Status
```

Jenkins coordinates the workflow, Docker provides isolated services, Selenium interacts with the application through a browser, and pytest executes the test cases. The generated JUnit report is collected by Jenkins to display the testing results.

## Features

- Flask-based login interface.
- Demo login authentication.
- Registration form with input validation.
- Password-help interface.
- Password visibility toggle.
- Remember-me checkbox interaction.
- Automated browser-based functional tests.
- Dockerized application and testing environment.
- Jenkins pipeline for automated execution.
- JUnit test report generation and publication.
- Build status indicating whether the tests passed or failed.

## Demo Credentials

Use the following credentials to test the demonstration login:

- **Email:** `admin@example.com`
- **Password:** `admin123`

These are demonstration credentials, not production authentication credentials.

**Note:** Registration validation is demonstrated without persistent account storage. The password-help page does not send actual emails, and the remember-me feature does not implement persistent authentication.

## Project Structure

```text
DEVOPS_LAB_PROJECT/
│
├── app/
│   ├── app.py
│   ├── templates/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── password_help.html
│   │   └── base.html
│   └── static/
│       ├── style.css
│       └── login.js
│
├── tests/
│   └── test_login.py
│
├── jenkins/
│   └── Dockerfile
│
├── reports/
│   └── results.xml
│
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile
├── requirements.txt
├── .gitignore
├── .dockerignore
├── README.md
└── VALIDATION.md
```

The `reports/` directory may be generated during testing and may be excluded from version control depending on the repository's `.gitignore` configuration.

## Prerequisites

Install or configure the following software:

1. Git
2. Docker Desktop
3. Jenkins
4. Java Development Kit (JDK) compatible with the Jenkins installation
5. A modern web browser

Docker Desktop must be running before executing the Docker commands. Jenkins must also have access to the Docker CLI.

## Installation and Execution

### 1. Clone the repository

```bash
git clone https://github.com/RakshithSharma96/DEVOPS_LAB_PROJECT.git
cd DEVOPS_LAB_PROJECT
```

### 2. Validate the Docker Compose configuration

```bash
docker compose --profile testing config --quiet
```

If the command completes without errors, the Compose configuration is valid.

### 3. Build the application image

```bash
docker compose build app
```

### 4. Start the application and Selenium browser

```bash
docker compose up -d --build --wait --wait-timeout 180 app selenium
```

Open the application in a browser:

**http://localhost:5000**

### 5. Run the automated tests

Create the reports directory if required:

```bash
mkdir reports
```

Then execute:

```bash
docker compose run --rm tests
```

The test runner executes the pytest suite and uses Selenium to interact with the web application through the browser service.

### 6. View test results

The test output is displayed in the terminal. The JUnit XML report is generated at:

```text
reports/results.xml
```

The exact report location depends on the volume configuration in Docker Compose.

### 7. Stop the containers

After testing, stop and remove the Compose services:

```bash
docker compose down
```

## Jenkins Continuous Integration

Jenkins automates the testing workflow using the project's `Jenkinsfile`.

### Pipeline workflow

1. Start a Jenkins build.
2. Read the project files from the configured local project directory.
3. Build the required Docker image.
4. Start the Flask application and Selenium browser.
5. Execute the pytest test suite in the test container.
6. Collect the JUnit XML test report.
7. Publish the test results in Jenkins.
8. Mark the build as successful or failed according to the pipeline outcome.
9. Clean up the Docker services.

### Jenkins configuration

Create a Jenkins Pipeline job named:

```text
DevOps-Login-Testing
```

Configure the job to use the pipeline script from the project's `Jenkinsfile`.

If the Jenkins job uses the `LOCAL_PROJECT_PATH` parameter, set it to the absolute path of the project directory on the machine running Jenkins. For example:

```text
C:\Users\raksh\Desktop\DevOps-Lab-Project
```

Ensure that the Jenkins process can access Docker and that the Docker CLI is available in its environment.

Run **Build with Parameters** to execute the pipeline.

After the build finishes, inspect the Console Output and the published Test Result report.

**Note:** This configuration uses a manually triggered pipeline. Automatic builds on every GitHub push require additional source-control integration or webhook configuration.

## Automated Test Cases

The project contains 17 automated tests covering the login application and its related form interactions.

The test suite covers scenarios such as:

- Successful login with valid demo credentials.
- Rejection of invalid credentials.
- Handling of empty login fields.
- Form validation.
- Registration form behavior.
- Password-help form behavior.
- Password visibility interaction.
- Remember-me checkbox interaction.
- Navigation and basic interface behavior.

The exact test coverage is defined in `tests/test_login.py`.

### Test execution result

During validation, the project completed a run with **17 tests passed** using Docker Compose and Selenium Chrome.

A successful test run indicates that the tested behaviors matched the expected results for that execution. It does not prove that every possible defect has been eliminated.

## Failure Testing and Recovery

The pipeline can also be demonstrated by temporarily introducing a controlled defect into the login logic.

1. Run the application with the original implementation and confirm that the tests pass.
2. Temporarily change the login behavior so that valid credentials are rejected.
3. Run the Jenkins pipeline again and inspect the failed test and build status.
4. Restore the original implementation.
5. Run the pipeline again and confirm that the tests pass.

This demonstrates regression detection and how a CI pipeline helps identify defects before changes are accepted.

Do not leave the intentional defect in the final submitted version.

## Advantages

- Reduces repetitive manual testing.
- Improves repeatability of functional tests.
- Provides an isolated environment through Docker.
- Detects regressions through automated test execution.
- Makes test results easier to review using Jenkins reports.
- Demonstrates the integration of development, testing, and CI tools.
- Helps students understand practical DevOps workflows.

## Limitations

- The application is a demonstration project rather than a production authentication system.
- User registration does not persist accounts in a database.
- Password-help functionality does not send real emails.
- The remember-me interaction does not provide persistent authentication.
- The pipeline is manually triggered unless additional GitHub integration is configured.
- The test suite covers the implemented scenarios and cannot guarantee the absence of all defects.

## Future Enhancements

- Integrate GitHub webhooks for automatic builds on code changes.
- Add database-backed user registration and authentication.
- Implement secure password hashing and session management.
- Add email delivery for password recovery.
- Expand tests to cover security, accessibility, and cross-browser behavior.
- Introduce code quality and security scanning tools.
- Add deployment stages to the Jenkins pipeline.
- Store test reports and build artifacts for long-term analysis.

## Conclusion

This project demonstrates an automated web application testing pipeline using Flask, Selenium, pytest, Docker, Docker Compose, and Jenkins. The application provides a controlled environment for functional testing, while the CI pipeline automates test execution and publishes results through JUnit reports.

The project illustrates the practical role of containerization, browser automation, and Continuous Integration in improving software testing reliability and detecting regressions early in the development process.
