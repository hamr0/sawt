# Pre-commit Hook Documentation

**Project:** Arabic TTS MVP Phase 1  
**Hook Type:** Test runner  
**Purpose:** Prevent commits with failing tests  
**Status:** Active

---

## Overview

The pre-commit hook automatically runs the full test suite before each commit. If any tests fail, the commit is aborted, ensuring the main branch always has passing tests.

---

## Installation

### Automatic Setup (Recommended)

Run the setup script:
```bash
cd /home/hamr/Documents/PycharmProjects/ArabicTTS
./scripts/setup_pre_commit_hook.sh
```

### Manual Setup

1. Copy the hook file:
```bash
cp scripts/setup_pre_commit_hook.sh .git/hooks/pre-commit
```

2. Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## How It Works

### When You Commit

```bash
git commit -m "feat: add new feature"
```

**The hook automatically:**
1. Detects the commit attempt
2. Runs `pytest tests/ -q --tb=short`
3. Checks test results
4. **If tests pass:** ✅ Commit proceeds normally
5. **If tests fail:** ❌ Commit is aborted with error message

### Example Output (Success)

```
🧪 Running pre-commit tests...

........................................................................ [ 21%]
........................................................................ [ 43%]
........................................................................ [ 65%]
........................................................................ [ 87%]
.........................................                                [100%]
329 passed, 1 warning in 30.74s

✅ All tests passed! Proceeding with commit.

[master 1234567] feat: add new feature
 1 file changed, 10 insertions(+)
```

### Example Output (Failure)

```
🧪 Running pre-commit tests...

.......F..............................................................  [ 21%]
...
FAILED tests/unit/test_syllabifier.py::TestCVPatterns::test_single_cv_syllable

❌ Tests failed! Commit aborted.

Please fix failing tests before committing.
To skip this check (not recommended), use: git commit --no-verify
```

---

## Bypassing the Hook

### When to Bypass

You may want to bypass the hook in these cases:
- Emergency hotfix
- Work-in-progress commit
- Known test failures being addressed

### How to Bypass

Use the `--no-verify` flag:
```bash
git commit --no-verify -m "WIP: work in progress"
```

**⚠️ Warning:** Bypassing the hook can introduce failing tests into the repository. Use sparingly!

---

## Hook Configuration

### Hook Location
```
.git/hooks/pre-commit
```

### Hook Contents
```bash
#!/bin/bash
# Pre-commit hook for Arabic TTS project

echo "🧪 Running pre-commit tests..."
cd "$(git rev-parse --show-toplevel)" || exit 1
python3 -m pytest tests/ -q --tb=short
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Tests failed!"
    exit 1
fi
```

---

## Customization

### Running Subset of Tests

To run only critical tests, modify the hook:
```bash
# Only unit tests
python3 -m pytest tests/unit/ -q --tb=short

# Only fast tests (skip performance tests)
python3 -m pytest tests/ -q --tb=short -m "not slow"

# Critical tests only
python3 -m pytest tests/unit/test_syllabifier.py tests/integration/ -q
```

### Adding Additional Checks

You can add more checks to the hook:
```bash
# Run linter
echo "Running flake8..."
python3 -m flake8 src/

# Check code formatting
echo "Checking code format..."
python3 -m black --check src/

# Run type checker
echo "Running mypy..."
python3 -m mypy src/
```

---

## Troubleshooting

### Hook Not Running

**Problem:** Hook doesn't execute when committing

**Solutions:**
1. Check hook is executable:
   ```bash
   ls -la .git/hooks/pre-commit
   # Should show: -rwxrwxr-x
   ```

2. Make executable if needed:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. Verify hook location:
   ```bash
   ls .git/hooks/pre-commit
   # Should exist
   ```

### Tests Taking Too Long

**Problem:** Pre-commit tests are slow

**Solutions:**
1. Run only fast tests:
   ```bash
   # Modify hook to skip slow tests
   python3 -m pytest tests/ -q --tb=short -x  # Stop on first failure
   ```

2. Run subset of tests:
   ```bash
   # Only smoke + critical unit tests
   python3 -m pytest tests/smoke/ tests/unit/test_syllabifier.py -q
   ```

3. Use parallel test execution:
   ```bash
   # Install pytest-xdist
   pip install pytest-xdist
   
   # Modify hook
   python3 -m pytest tests/ -q -n auto  # Use all CPU cores
   ```

### Hook Fails But Tests Pass Locally

**Problem:** Hook fails, but running tests manually succeeds

**Solutions:**
1. Check working directory:
   ```bash
   # Hook should cd to repo root
   cd "$(git rev-parse --show-toplevel)"
   ```

2. Check Python environment:
   ```bash
   # Verify correct Python version
   which python3
   python3 --version
   ```

3. Check dependencies:
   ```bash
   # Install missing packages
   pip3 install -r requirements.txt
   ```

---

## Disabling the Hook

### Temporary Disable

Rename the hook:
```bash
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
```

Re-enable:
```bash
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

### Permanent Disable

Delete the hook:
```bash
rm .git/hooks/pre-commit
```

---

## Best Practices

### For Developers

1. **Run tests before committing** - Even with hook, run tests manually first
2. **Keep tests fast** - Fast tests encourage frequent commits
3. **Fix failing tests immediately** - Don't let tests stay broken
4. **Don't bypass the hook habitually** - Defeats its purpose
5. **Update hook documentation** - When modifying hook behavior

### For Team Leads

1. **Enforce hook usage** - Require all developers to install hook
2. **Monitor bypasses** - Track commits with `--no-verify`
3. **Keep tests reliable** - Flaky tests lead to hook bypasses
4. **Review hook regularly** - Ensure it's not too slow or strict
5. **Document exceptions** - When bypassing is acceptable

---

## Statistics

### Current Configuration

| Metric | Value |
|--------|-------|
| **Total Tests** | 329 |
| **Average Runtime** | ~30 seconds |
| **Success Rate** | 100% (when all tests pass) |
| **Bypass Rate** | Track with: `git log --all --grep="no-verify"` |

---

## Integration with CI/CD

The pre-commit hook complements, but doesn't replace, CI/CD testing:

```
Developer Machine          GitHub                  CI/CD
────────────────          ──────                  ─────
                                                  
Write code                                        
    ↓                                            
Run tests manually                               
    ↓                                            
git commit ──→ Pre-commit hook runs tests        
    ↓              ↓                             
    │         Tests pass?                        
    │              ↓                             
    │            Yes ──→ Commit succeeds         
    │                        ↓                   
    │                   git push ──→ CI/CD runs  
    │                                 tests again
    │                                     ↓      
    │                                Tests pass? 
    │                                     ↓      
    │                                   Yes ──→  
    │                                   Deploy   
    ↓                                            
Tests fail ──→ Fix code ──→ Try again            
```

---

## Future Enhancements

### Planned Improvements

1. **Selective testing** - Only test files changed in commit
2. **Parallel execution** - Speed up with pytest-xdist
3. **Pre-push hook** - Additional checks before push
4. **Commit message validation** - Enforce conventional commits
5. **Code coverage check** - Ensure new code is tested
6. **Performance regression check** - Alert on slow code

---

## References

- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Framework](https://pre-commit.com/) (alternative approach)

---

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Maintained By:** Arabic TTS Development Team
