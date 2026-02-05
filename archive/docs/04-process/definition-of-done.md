# Definition of Done

Criteria that must be met before work is considered complete.

---

## Code Changes

### Before Committing

- [ ] All existing tests pass (`pytest tests/ -v`)
- [ ] New functionality has test coverage
- [ ] No security vulnerabilities introduced
- [ ] Code follows existing patterns in codebase

### Before Merging

- [ ] Pre-commit hook passes (runs full test suite)
- [ ] No regressions in accuracy metrics
- [ ] Documentation updated if API changed

---

## Feature Implementation

### Minimum Criteria

- [ ] Feature works for happy path
- [ ] Error cases handled gracefully
- [ ] Tests written and passing
- [ ] Works with all supported dialects (if applicable)

### Quality Criteria

- [ ] Processing speed not significantly degraded
- [ ] Memory usage reasonable
- [ ] No silent failures (errors logged/reported)

---

## Bug Fixes

- [ ] Root cause identified and documented
- [ ] Fix addresses root cause (not just symptoms)
- [ ] Regression test added
- [ ] Bug logged in `03-logs/bug-log.md`

---

## Documentation

### When Required

- API changes → Update relevant docs
- New features → Add to feature docs
- Architecture changes → Update system-state.md
- Decisions made → Log in decisions-log.md

### Quality Criteria

- Clear and concise
- Code examples where helpful
- Links to related docs

---

## Release Checklist

- [ ] All tests passing (329/329)
- [ ] Accuracy metrics maintained (>90% syl, >90% IPA)
- [ ] Performance benchmarks met (>10 words/sec)
- [ ] CHANGELOG updated
- [ ] Version bumped if applicable
- [ ] Documentation current

---

## Quick Reference

| Work Type | Must Have | Should Have |
|-----------|-----------|-------------|
| Code change | Tests pass | Docs updated |
| Bug fix | Root cause, regression test | Bug log entry |
| Feature | Tests, error handling | Feature docs |
| Refactor | All tests pass | No behavior change |
