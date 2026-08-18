# Content Completeness Rubric

The structural_check.py script only catches what's mechanically checkable
(frontmatter, length, examples-present, etc). It cannot tell you whether a
"legacy modernization" skill actually handles rollback plans, or whether a
"testing skill" covers flaky-test triage. That judgment requires reading the
skill with domain knowledge of what a skill of *this type* should cover --
that's what this reference is for.

Score this half out of 100 as well, then combine per the weighting in
SKILL.md. Use whole-number deductions per gap found, not a formula --
this is judgment, not arithmetic.

## Step 1: Infer the skill's "job"

Before judging gaps, state in one or two sentences what this skill's job is
and who relies on it (e.g. "generates BIAN-aligned agent skill contracts for
a banking domain -- used by architects standing up new AgentForge modules").
Everything below is graded against that job, not against skills in general.
A narrow, single-purpose skill done completely should score *higher* than a
broad skill with holes -- don't penalize narrowness itself.

## Step 2: Check these dimensions (each is a source of possible gaps)

### Workflow completeness
Does the skill cover the full lifecycle of its task, not just the happy
path? For a generation/build skill: does it also cover validation of its
own output? For a multi-step pipeline: are all steps present, or does it
stop short and leave the user to figure out the last mile?

### Edge cases and failure modes
Does it name the edge cases specific to its domain (e.g. for a data-migration
skill: partial failures, schema drift, duplicate keys; for a testing skill:
flaky tests, environment-dependent failures)? A skill that only describes
the clean-input case has a gap here.

### Error handling and recovery guidance
When something goes wrong mid-task, does the skill tell Claude what to do
(retry, roll back, ask the user, log and continue)? Silence here means
Claude improvises inconsistently across runs.

### Verification / self-check step
Does the skill tell Claude how to confirm its own output is correct before
handing it back (tests, schema validation, a checklist, re-reading against
requirements)? Skills that generate code, contracts, or structured artifacts
should almost always have this.

### Domain best-practice alignment
Compare the skill's approach against known best practice for that domain
(you likely have relevant knowledge -- e.g. BIAN service domain conventions,
Pydantic v2 patterns, DDD decomposition principles, OWASP-style secure
coding, standard test pyramid coverage). Flag where the skill's instructions
diverge from or omit an important convention a practitioner would expect.
If you're unsure whether something is current best practice, say so rather
than asserting it, and consider a web search for fast-moving domains.

### Dependency and prerequisite clarity
If the skill assumes tools, libraries, credentials, prior skills, or file
formats, are they stated? An unstated dependency is a gap because it causes
silent failures downstream.

### Consistency of terminology and output contracts
If the skill defines a data contract (JSON schema, file naming, an
AgentContext object, etc.), is it used consistently, and does it match
what a downstream consumer (another skill, a human reviewer) would expect?

### Scope boundary clarity
Does the skill say what it does *not* do, or where it hands off to another
skill/process? Missing boundaries cause overreach or duplicated effort in
libraries with many related skills (very relevant for large skill packages
built as a chain, e.g. multi-skill pipelines).

## Step 3: For batch/library mode, also check across skills

- **Chain integrity**: if skills are meant to feed each other (shared
  context schema, sequential pipeline), do the input/output contracts
  actually line up end to end, or is there a missing bridge skill?
- **Coverage holes**: given the stated purpose of the library as a whole,
  is there an obvious missing skill a practitioner would expect (e.g. a
  test-generation library with no fixtures/mocking skill; a migration
  library with skills for three of four legacy stacks it claims to cover)?
- **Redundancy**: structural_check.py already flags description-text
  overlap mechanically; use your reading of the actual instructions to
  confirm whether it's true duplication or legitimately different scope.

## Step 4: Write each gap as an actionable finding

For every gap, produce:
- **What's missing** (one line, concrete -- not "could be more thorough")
- **Why it matters** (what breaks or degrades without it, for that skill's
  actual job -- not a generic platitude)
- **Severity**: `critical` (skill will produce wrong/unsafe output without
  this), `major` (skill will underperform or need frequent correction),
  `minor` (polish, would help but skill is usable without it)
- **Concrete fix**: specific enough to act on -- name the section to add,
  the edge case to name, the script to bundle -- not "add more detail"

Do not manufacture gaps to pad the list. A tightly-scoped, complete skill
can legitimately have zero or one content gaps -- say so.
