---
name: spec-driven
description: Spec-Driven Development for complex projects. Activates when designing architecture, creating specifications, or implementing from requirements. Specs are the prompt.
---

# Spec-Driven Development Skill

Development methodology using structured specifications as AI prompts. Specs define what to build, tests verify it.

## The Iron Law

```text
NO IMPLEMENTATION WITHOUT A SPECIFICATION FIRST
Specifications are the prompt. PRD → Tech Spec → Component Spec → Code.
```

## Core Principle

> "Specifications are the prompt. If it's not in the spec, don't build it."

## When to Use

**Always:**
- Multi-component systems (3+ components)
- API design (endpoints, contracts)
- Database schema design
- Architectural decisions
- Features with business requirements

**Exceptions (ask human partner):**
- Single-file utilities (just use TDD)
- Exploratory prototypes
- Bug fixes (use systematic-debugging instead)

## Spec Hierarchy

```text
BDD Scenarios (Business Behavior)
    ↓
PRD (What & Why)
    ↓
Technical Spec (How - Architecture)
    ↓
Component Spec (How - Implementation)
    ↓
Code (TDD from Component Spec)
```

### BDD Integration

BDD scenarios (Gherkin format) are the starting point for specs:

```text
BDD Scenario           →    Component Spec Test Case    →    Unit Test
────────────────────────────────────────────────────────────────────────
Given [precondition]   →    <given>setup state</given>  →    // Arrange
When [action]          →    <when>invoke method</when>  →    // Act
Then [expectation]     →    <then>verify result</then>  →    // Assert
```

**Workflow:**
1. `/plan` creates BDD scenarios (Phase 0)
2. Architect converts scenarios to component spec `<test-cases>`
3. Implementer generates tests from `<test-cases>` (TDD RED phase)
4. Implementation makes tests pass (TDD GREEN phase)

| Document | Owner | Focus | AI Role |
|----------|-------|-------|---------|
| PRD | Product | Requirements | Review, suggest gaps |
| Tech Spec | Architect | Architecture | Generate from PRD |
| Component Spec | Developer | Interfaces | Generate from Tech Spec |
| Code | Developer | Implementation | Generate from Component Spec |

## Workflow

### Step 1: Write PRD (or receive from human)

Define: Problem, Solution, Success Metrics, Requirements.

### Step 2: Generate Technical Spec

From PRD, generate architecture: components, data model, API contracts.

### Step 3: Generate Component Specs

For each component: interfaces, methods, test cases.

### Step 4: TDD Implementation

For each component spec:
1. Generate tests from spec
2. RED - tests fail
3. Generate implementation
4. GREEN - tests pass
5. Verify against spec

## Spec Formats

### PRD Structure

```xml
<prd version="1.0">
  <metadata>
    <title>Feature Name</title>
    <version>1.0.0</version>
    <status>draft|review|approved</status>
  </metadata>

  <overview>
    <problem>Why this is needed</problem>
    <solution>High-level approach</solution>
    <success-metrics>
      <metric name="metric-name" target="value" />
    </success-metrics>
  </overview>

  <requirements>
    <functional>
      <requirement id="F001" priority="must|should|could">
        <title>Requirement Title</title>
        <description>What it does</description>
        <acceptance-criteria>
          <criterion>Testable condition</criterion>
        </acceptance-criteria>
      </requirement>
    </functional>
    <non-functional>
      <requirement id="NF001" category="security|performance|scalability">
        <title>NFR Title</title>
        <specification>Measurable target</specification>
      </requirement>
    </non-functional>
  </requirements>

  <constraints>
    <technical>Technology constraints</technical>
    <regulatory>Compliance requirements</regulatory>
  </constraints>
</prd>
```

### Technical Spec Structure

```xml
<technical-spec version="1.0">
  <metadata>
    <title>System Technical Specification</title>
    <prd-ref>PRD-XXX-001</prd-ref>
  </metadata>

  <architecture>
    <components>
      <component name="ComponentName">
        <responsibility>What it does</responsibility>
        <dependencies>
          <dependency>OtherComponent</dependency>
        </dependencies>
      </component>
    </components>
  </architecture>

  <data-model>
    <entity name="EntityName">
      <field name="id" type="uuid" primary="true" />
      <field name="name" type="string" />
    </entity>
  </data-model>

  <api-contracts>
    <endpoint path="/api/resource" method="POST">
      <request><body type="json">...</body></request>
      <response status="201"><body>...</body></response>
      <errors>
        <error status="400" code="ERROR_CODE" />
      </errors>
    </endpoint>
  </api-contracts>
</technical-spec>
```

### Component Spec Structure

```xml
<component-spec version="1.0">
  <metadata>
    <name>ComponentName</name>
    <tech-spec-ref>TECH-XXX-001</tech-spec-ref>
    <language>typescript</language>
  </metadata>

  <interface>
    <method name="methodName">
      <param name="paramName" type="ParamType" />
      <returns type="ReturnType" />
      <throws type="ErrorType" />
    </method>
  </interface>

  <test-cases>
    <test name="describes expected behavior">
      <given>Initial state</given>
      <when>Action taken</when>
      <then>Expected result</then>
    </test>
  </test-cases>
</component-spec>
```

## Examples

<Good>
```xml
<component-spec version="1.0">
  <metadata>
    <name>PasswordService</name>
    <language>typescript</language>
  </metadata>

  <interface>
    <method name="hash">
      <param name="password" type="string" />
      <returns type="Promise&lt;string&gt;" description="bcrypt hash" />
    </method>
    <method name="verify">
      <param name="password" type="string" />
      <param name="hash" type="string" />
      <returns type="Promise&lt;boolean&gt;" />
    </method>
  </interface>

  <test-cases>
    <test name="hash returns different output for same input">
      <given>Same password</given>
      <when>hash called twice</when>
      <then>Returns different hashes (salt)</then>
    </test>
    <test name="verify returns true for correct password">
      <given>Password and its hash</given>
      <when>verify called</when>
      <then>Returns true</then>
    </test>
    <test name="verify returns false for wrong password">
      <given>Wrong password and hash</given>
      <when>verify called</when>
      <then>Returns false</then>
    </test>
  </test-cases>
</component-spec>
```
- Complete interface definition
- Test cases in Given/When/Then format
- Covers success and failure cases
- Clear types and return values
</Good>

<Bad>
```markdown
## PasswordService

This service handles password hashing. It should:
- Hash passwords
- Verify passwords
- Be secure

Just use bcrypt or something similar.
```
- No interface definition
- No test cases
- Vague requirements ("be secure")
- No acceptance criteria
- Implementation suggestion without spec
</Bad>

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too small for a spec" | If it has requirements, it needs a spec. Use simpler format. |
| "Requirements will change" | Specs are versioned. Update them, don't abandon them. |
| "I know what to build" | Write it down. Memory fails. Specs document decisions. |
| "Specs slow me down" | Ambiguous requirements slow you down more. Spec once, build right. |
| "AI will figure it out" | AI generates from its training, not your requirements. Spec is the prompt. |
| "We'll document after" | After never comes. Spec-first or no spec at all. |

## Red Flags - STOP and Start Over

These indicate you're building without spec:

- Writing code before defining interfaces
- Implementing features not in requirements
- "I'll add this while I'm here"
- No test cases before implementation
- Changing behavior without updating spec
- "The spec is in my head"
- Building based on verbal description only

**If you catch yourself doing these, STOP. Write the spec first.**

## Verification Checklist

Before implementing from a spec:

- [ ] PRD has clear problem statement and success metrics
- [ ] All requirements have acceptance criteria
- [ ] Tech spec traces back to PRD requirements
- [ ] Component specs have interface definitions
- [ ] Every method has parameter and return types
- [ ] Test cases cover success and failure paths
- [ ] Test cases are in Given/When/Then format
- [ ] Spec is approved before implementation starts

## Spec Quality Checks

| Check | Pass Criteria |
|-------|---------------|
| Completeness | All requirements have acceptance criteria |
| Testability | Every criterion can be verified with a test |
| Traceability | PRD → Tech → Component chain is clear |
| Consistency | No conflicting requirements |
| Clarity | No ambiguous language ("should", "might", "etc.") |

## When Stuck

| Problem | Solution |
|---------|----------|
| Requirements unclear | Ask stakeholder. Don't assume. |
| Conflicting requirements | Escalate to PRD owner for resolution. |
| Can't define interface | Break component into smaller parts. |
| Too many test cases | Group related cases. Prioritize must-haves. |
| Spec too long | Split into sub-components with own specs. |
| Implementation deviates | Update spec first, then implement. |

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Incomplete spec | Missing edge cases | Add acceptance criteria for all paths |
| Spec drift | Code diverges from spec | Update spec when requirements change |
| Over-specification | Specifying implementation | Specify behavior, not code |
| Under-specification | Ambiguous requirements | Add specific acceptance criteria |
| Spec without tests | No verification | Write test cases in spec |

## Using Specs with AI

### Generation Prompt

```markdown
Using this component specification, implement [ComponentName]:

[paste component-spec XML]

Requirements:
1. Follow TDD - write tests first from <test-cases>
2. Implement interface exactly as specified
3. Use [language] with [framework]
4. Do not add methods not in spec
```

### Verification Prompt

```markdown
Verify this implementation against spec:

**Implementation:**
[paste code]

**Specification:**
[paste spec]

Check:
1. All interface methods implemented correctly
2. All test cases from spec covered
3. No extra functionality added
4. Types match spec exactly
```

## Related Skills

- `tdd` - Implements code from component specs using test-first
- `architect` - Generates technical specs from PRDs
- `researcher` - Gathers context for writing specs
