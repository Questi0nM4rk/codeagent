---
name: spec-driven
description: Spec-Driven Development methodology for large projects. Activates when designing architecture, creating specifications, or orchestrating complex multi-component implementations.
---

# Spec-Driven Development Skill

A development paradigm using well-crafted software requirement specifications as prompts for AI-assisted code generation.

## Evolution of Development Paradigms

```
Prompt Engineering (2022-23)
    ↓ Craft individual prompts

Context Engineering (2024)
    ↓ RAG, feed documents to models

Spec-Driven Development (2025)
    → Use specifications as structured prompts
    → AI generates code from specs
    → Human reviews and iterates
```

## Core Concept

**Specifications are the prompt.** Instead of ad-hoc prompts, create structured documents that:
- Define requirements precisely
- Serve as implementation guide
- Enable deterministic code generation
- Provide verification criteria

## Spec Document Types

### 1. Product Requirements Document (PRD)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<prd version="1.0">
  <metadata>
    <title>User Authentication System</title>
    <author>Product Team</author>
    <version>1.0.0</version>
    <date>2025-01-06</date>
    <status>draft|review|approved</status>
  </metadata>

  <overview>
    <problem>
      Users need secure, frictionless authentication across web and mobile.
    </problem>
    <solution>
      Multi-provider auth system with MFA support.
    </solution>
    <success-metrics>
      <metric name="login-success-rate" target="99.5%" />
      <metric name="avg-login-time" target="&lt;3s" />
    </success-metrics>
  </overview>

  <requirements>
    <functional>
      <requirement id="F001" priority="must">
        <title>Email/Password Authentication</title>
        <description>Users can register and login with email/password</description>
        <acceptance-criteria>
          <criterion>Valid email format enforced</criterion>
          <criterion>Password minimum 8 characters</criterion>
          <criterion>Password hashed with bcrypt</criterion>
        </acceptance-criteria>
      </requirement>

      <requirement id="F002" priority="should">
        <title>OAuth Integration</title>
        <description>Users can login via Google, GitHub</description>
        <acceptance-criteria>
          <criterion>OAuth 2.0 flow implemented</criterion>
          <criterion>Account linking supported</criterion>
        </acceptance-criteria>
      </requirement>
    </functional>

    <non-functional>
      <requirement id="NF001" category="security">
        <title>Token Security</title>
        <specification>JWT with RS256, 15min access, 7d refresh</specification>
      </requirement>

      <requirement id="NF002" category="performance">
        <title>Authentication Latency</title>
        <specification>p99 &lt; 500ms for login operations</specification>
      </requirement>
    </non-functional>
  </requirements>

  <constraints>
    <technical>PostgreSQL database, Node.js backend</technical>
    <regulatory>GDPR compliance required</regulatory>
    <timeline>MVP in 4 weeks</timeline>
  </constraints>
</prd>
```

### 2. Technical Specification

```xml
<?xml version="1.0" encoding="UTF-8"?>
<technical-spec version="1.0">
  <metadata>
    <title>Auth Service Technical Specification</title>
    <prd-ref>PRD-AUTH-001</prd-ref>
    <version>1.0.0</version>
  </metadata>

  <architecture>
    <overview>
      Microservice handling authentication, token management, and session storage.
    </overview>

    <components>
      <component name="AuthController">
        <responsibility>HTTP endpoints for auth operations</responsibility>
        <endpoints>
          <endpoint method="POST" path="/auth/register" />
          <endpoint method="POST" path="/auth/login" />
          <endpoint method="POST" path="/auth/refresh" />
          <endpoint method="POST" path="/auth/logout" />
        </endpoints>
      </component>

      <component name="AuthService">
        <responsibility>Business logic for authentication</responsibility>
        <dependencies>
          <dependency>UserRepository</dependency>
          <dependency>TokenService</dependency>
          <dependency>PasswordService</dependency>
        </dependencies>
      </component>

      <component name="TokenService">
        <responsibility>JWT generation and validation</responsibility>
        <configuration>
          <param name="algorithm">RS256</param>
          <param name="access-ttl">900</param>
          <param name="refresh-ttl">604800</param>
        </configuration>
      </component>
    </components>
  </architecture>

  <data-model>
    <entity name="User">
      <field name="id" type="uuid" primary="true" />
      <field name="email" type="string" unique="true" />
      <field name="password_hash" type="string" />
      <field name="created_at" type="timestamp" />
      <field name="updated_at" type="timestamp" />
    </entity>

    <entity name="RefreshToken">
      <field name="id" type="uuid" primary="true" />
      <field name="user_id" type="uuid" foreign="User.id" />
      <field name="token_hash" type="string" />
      <field name="expires_at" type="timestamp" />
      <field name="revoked" type="boolean" default="false" />
    </entity>
  </data-model>

  <api-contracts>
    <endpoint path="/auth/register" method="POST">
      <request>
        <body type="json">
          <field name="email" type="string" required="true" />
          <field name="password" type="string" required="true" />
        </body>
      </request>
      <response status="201">
        <body type="json">
          <field name="user" type="User" />
          <field name="access_token" type="string" />
          <field name="refresh_token" type="string" />
        </body>
      </response>
      <errors>
        <error status="400" code="INVALID_EMAIL" />
        <error status="400" code="WEAK_PASSWORD" />
        <error status="409" code="EMAIL_EXISTS" />
      </errors>
    </endpoint>
  </api-contracts>

  <security>
    <authentication>Bearer JWT in Authorization header</authentication>
    <password-policy>
      <min-length>8</min-length>
      <require-uppercase>true</require-uppercase>
      <require-number>true</require-number>
    </password-policy>
    <rate-limiting>
      <rule path="/auth/login" limit="5/minute" />
      <rule path="/auth/register" limit="3/minute" />
    </rate-limiting>
  </security>

  <testing>
    <unit-tests>
      <coverage-target>80%</coverage-target>
      <critical-paths>
        <path>Password hashing</path>
        <path>Token generation</path>
        <path>Token validation</path>
      </critical-paths>
    </unit-tests>
    <integration-tests>
      <scenarios>
        <scenario>Full registration flow</scenario>
        <scenario>Login with valid credentials</scenario>
        <scenario>Token refresh</scenario>
        <scenario>Invalid credential handling</scenario>
      </scenarios>
    </integration-tests>
  </testing>
</technical-spec>
```

### 3. Component Spec (Implementation-Ready)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component-spec version="1.0">
  <metadata>
    <name>TokenService</name>
    <tech-spec-ref>TECH-AUTH-001</tech-spec-ref>
    <language>typescript</language>
  </metadata>

  <interface>
    <method name="generateAccessToken">
      <param name="userId" type="string" />
      <param name="claims" type="Record&lt;string, unknown&gt;" optional="true" />
      <returns type="string" description="JWT access token" />
    </method>

    <method name="generateRefreshToken">
      <param name="userId" type="string" />
      <returns type="string" description="Opaque refresh token" />
    </method>

    <method name="verifyAccessToken">
      <param name="token" type="string" />
      <returns type="TokenPayload | null" />
      <throws type="TokenExpiredError" />
      <throws type="InvalidTokenError" />
    </method>

    <method name="revokeRefreshToken">
      <param name="token" type="string" />
      <returns type="void" />
    </method>
  </interface>

  <implementation-notes>
    <note>Use jose library for JWT operations</note>
    <note>Store refresh token hash, not plain token</note>
    <note>Include 'iat', 'exp', 'sub' standard claims</note>
  </implementation-notes>

  <test-cases>
    <test name="generates valid JWT with correct claims">
      <given>Valid user ID</given>
      <when>generateAccessToken called</when>
      <then>Returns JWT with sub=userId, exp in 15min</then>
    </test>

    <test name="rejects expired token">
      <given>Token generated 16 minutes ago</given>
      <when>verifyAccessToken called</when>
      <then>Throws TokenExpiredError</then>
    </test>

    <test name="rejects tampered token">
      <given>Token with modified payload</given>
      <when>verifyAccessToken called</when>
      <then>Throws InvalidTokenError</then>
    </test>
  </test-cases>
</component-spec>
```

## Workflow

### Phase 1: Requirements Gathering
```
1. Stakeholder interviews
2. Write PRD
3. Review with stakeholders
4. Approval gate
```

### Phase 2: Technical Design
```
1. Architect reviews PRD
2. Write Technical Spec
3. Peer review
4. Approval gate
```

### Phase 3: Component Breakdown
```
1. Identify components from Tech Spec
2. Write Component Specs
3. Define interfaces and contracts
4. TDD test cases
```

### Phase 4: Implementation
```
For each Component Spec:
1. Generate tests from spec
2. Run tests (RED)
3. Generate implementation
4. Run tests (GREEN)
5. Review against spec
6. Refactor if needed
```

### Phase 5: Integration
```
1. Integrate components
2. Run integration tests
3. Verify against Tech Spec
4. Validate against PRD
```

## Using Specs with AI

### Spec as Prompt

```markdown
## Implementation Request

Using the following component specification, implement the TokenService:

[paste component-spec XML]

Requirements:
1. Follow TDD - write tests first
2. Use TypeScript
3. Follow the interface exactly
4. Implement all test cases from spec
```

### Verification Prompt

```markdown
## Verification Request

Given this implementation:
[paste code]

And this specification:
[paste spec]

Verify:
1. All interface methods implemented
2. All test cases covered
3. All implementation notes followed
4. No deviations from spec
```

## Benefits

1. **Deterministic** - Same spec → Same code
2. **Reviewable** - Specs are human-readable
3. **Traceable** - PRD → Tech Spec → Component → Code
4. **Testable** - Test cases in spec
5. **Versionable** - Specs in version control
6. **AI-friendly** - Structured input for generation

## Anti-Patterns

❌ **Incomplete specs** - Missing edge cases, error handling
❌ **Spec drift** - Code diverges from spec without updating
❌ **Over-specification** - Specifying implementation details
❌ **Under-specification** - Ambiguous requirements
❌ **Spec without tests** - No verification criteria
