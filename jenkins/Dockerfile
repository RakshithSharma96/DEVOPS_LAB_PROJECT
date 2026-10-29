# Optional: Jenkins with Docker CLI, Compose and Buildx; uses Docker Desktop's engine.
FROM docker:29-cli AS dockercli
FROM jenkins/jenkins:lts-jdk21
USER root
COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=dockercli /usr/local/libexec/docker/cli-plugins/ /usr/local/lib/docker/cli-plugins/
# Start this local lab container as root to access the mounted Docker socket.
# Do not use this socket/root setup for an untrusted or public Jenkins server.
