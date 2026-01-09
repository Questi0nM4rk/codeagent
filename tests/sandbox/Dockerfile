# CodeAgent Test Sandbox
# Arch Linux base with all dependencies for testing install.sh
# Build: docker build -t codeagent-sandbox .
# Run:   docker run --rm -it codeagent-sandbox

FROM archlinux:latest

# Prevent interactive prompts
ENV PACMAN_NOCONFIRM=1

# Configure faster mirrors and update keyring first (most common failure point)
RUN echo 'Server = https://geo.mirror.pkgbuild.com/$repo/os/$arch' > /etc/pacman.d/mirrorlist && \
    echo 'Server = https://mirror.rackspace.com/archlinux/$repo/os/$arch' >> /etc/pacman.d/mirrorlist && \
    echo 'Server = https://mirrors.kernel.org/archlinux/$repo/os/$arch' >> /etc/pacman.d/mirrorlist && \
    pacman -Sy --noconfirm archlinux-keyring && \
    pacman -Su --noconfirm

# Install core requirements (with retry)
RUN for i in 1 2 3; do \
        pacman -S --noconfirm --needed \
            bash \
            git \
            python \
            python-pip \
            python-virtualenv \
            nodejs \
            npm \
        && break || sleep 5; \
    done

# Install Docker (separate layer for better caching)
RUN for i in 1 2 3; do \
        pacman -S --noconfirm --needed \
            docker \
            docker-compose \
        && break || sleep 5; \
    done

# Install shell tools and utilities
RUN for i in 1 2 3; do \
        pacman -S --noconfirm --needed \
            shellcheck \
            shfmt \
            curl \
            wget \
            jq \
            tree \
            which \
            sudo \
        && break || sleep 5; \
    done

# Install keyring tools (optional, may not be needed in minimal test)
RUN pacman -S --noconfirm --needed libsecret || true

# Clean up package cache
RUN pacman -Scc --noconfirm || true

# Create test user (non-root for realistic testing)
RUN useradd -m -s /bin/bash testuser && \
    echo "testuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Install Claude Code CLI as testuser (from Anthropic's official installer)
# https://claude.ai/code
USER testuser
RUN curl -fsSL https://claude.ai/install.sh | bash || echo "Claude CLI install attempted"
USER root

# Create mock docker socket (for testing without actual Docker daemon)
RUN mkdir -p /var/run && \
    touch /var/run/docker.sock

# Create mock docker commands that simulate success
RUN mkdir -p /usr/local/bin/mocks

# Mock docker command
RUN cat > /usr/local/bin/mocks/docker << 'MOCK_DOCKER'
#!/bin/bash
# Mock docker for testing (no actual Docker daemon)
case "$1" in
    compose)
        case "$2" in
            version) echo "Docker Compose version v2.24.0" ;;
            up) echo "Creating containers... done" ;;
            down) echo "Stopping containers... done" ;;
            ps) echo "NAME STATUS" ;;
            *) echo "mock: docker compose $*" ;;
        esac
        ;;
    ps)
        # Return empty or mock container list
        echo "CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES"
        ;;
    inspect)
        # Mock healthy container
        if [[ "$*" == *"Health"* ]]; then
            echo "healthy"
        else
            echo "{}"
        fi
        ;;
    *)
        echo "mock: docker $*"
        ;;
esac
exit 0
MOCK_DOCKER
RUN chmod +x /usr/local/bin/mocks/docker

# Mock docker-compose command
RUN ln -s /usr/local/bin/mocks/docker /usr/local/bin/mocks/docker-compose

# Switch to test user
USER testuser
WORKDIR /home/testuser

# Create expected directories
RUN mkdir -p /home/testuser/.local/bin \
    /home/testuser/.claude \
    /home/testuser/.config

# Add local bin to PATH and set up shell
RUN echo 'export PATH="/home/testuser/.local/bin:/usr/local/bin/mocks:$PATH"' >> ~/.bashrc && \
    echo 'export HOME=/home/testuser' >> ~/.bashrc

# Copy source code (done at runtime via volume mount or COPY)
# For isolated testing, we copy at build time:
COPY --chown=testuser:testuser . /home/testuser/codeagent-source

# Set environment
ENV HOME=/home/testuser
ENV PATH="/home/testuser/.local/bin:/usr/local/bin/mocks:$PATH"
ENV TERM=xterm-256color

# Default command runs test suite
CMD ["/home/testuser/codeagent-source/tests/sandbox/run-tests.sh"]
