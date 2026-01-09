# CodeAgent Test Sandbox
# Arch Linux base with all dependencies for testing install.sh
# Uses Docker-in-Docker (dind) for real Docker operations
# Build: docker build -t codeagent-sandbox .
# Run:   docker compose run --rm test

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

# Install Docker CLI (connects to dind, not local daemon)
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
            openssh \
        && break || sleep 5; \
    done

# Install keyring tools (optional, may not be needed in minimal test)
RUN pacman -S --noconfirm --needed libsecret || true

# Clean up package cache
RUN pacman -Scc --noconfirm || true

# Create test user (non-root for realistic testing)
RUN useradd -m -s /bin/bash testuser && \
    echo "testuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    usermod -aG docker testuser

# Switch to testuser for remaining setup
USER testuser
WORKDIR /home/testuser

# Install Claude Code CLI (from Anthropic's official installer)
RUN curl -fsSL https://claude.ai/install.sh | bash || echo "Claude CLI install attempted"

# Install uv (Python package manager - required for code-execution MCP)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh || echo "uv install attempted"

# Create expected directories
RUN mkdir -p /home/testuser/.local/bin \
    /home/testuser/.claude \
    /home/testuser/.config \
    /home/testuser/.ssh

# Set up SSH for GitHub access (keys will be mounted read-only at runtime)
# Add GitHub to known_hosts to avoid interactive prompt
RUN ssh-keyscan -t ed25519,rsa github.com >> /home/testuser/.ssh/known_hosts 2>/dev/null || true && \
    chmod 700 /home/testuser/.ssh && \
    chmod 644 /home/testuser/.ssh/known_hosts 2>/dev/null || true

# Add tools to PATH
RUN echo 'export PATH="/home/testuser/.local/bin:/home/testuser/.cargo/bin:$PATH"' >> ~/.bashrc && \
    echo 'export HOME=/home/testuser' >> ~/.bashrc && \
    echo 'export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new"' >> ~/.bashrc

# Copy source code (for build context, runtime uses volume mount)
COPY --chown=testuser:testuser . /home/testuser/codeagent-source

# Set environment
ENV HOME=/home/testuser
ENV PATH="/home/testuser/.local/bin:/home/testuser/.cargo/bin:$PATH"
ENV TERM=xterm-256color

# Default command runs test suite
CMD ["/home/testuser/codeagent-source/tests/sandbox/run-tests.sh"]
