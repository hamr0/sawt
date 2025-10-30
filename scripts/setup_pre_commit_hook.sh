#!/bin/bash
#
# Setup script for pre-commit test hook
# Run this script to install the pre-commit hook
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
HOOK_FILE="$HOOKS_DIR/pre-commit"

echo "========================================="
echo "Arabic TTS Pre-commit Hook Setup"
echo "========================================="
echo

# Check if .git directory exists
if [ ! -d "$PROJECT_ROOT/.git" ]; then
    echo "❌ Error: Not a git repository"
    echo "   Please run this script from within the git repository"
    exit 1
fi

# Create hooks directory if it doesn't exist
if [ ! -d "$HOOKS_DIR" ]; then
    echo "Creating hooks directory..."
    mkdir -p "$HOOKS_DIR"
fi

# Create pre-commit hook
echo "Installing pre-commit hook..."

cat > "$HOOK_FILE" << 'EOF'
#!/bin/bash
#
# Pre-commit hook for Arabic TTS project
# Runs test suite before allowing commits
# Prevents commits if tests fail
#

echo "🧪 Running pre-commit tests..."
echo

# Change to project root
cd "$(git rev-parse --show-toplevel)" || exit 1

# Run pytest with quiet output
python3 -m pytest tests/ -q --tb=short

# Capture exit code
TEST_EXIT_CODE=$?

echo

# Check if tests passed
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed! Proceeding with commit."
    echo
    exit 0
else
    echo "❌ Tests failed! Commit aborted."
    echo
    echo "Please fix failing tests before committing."
    echo "To skip this check (not recommended), use: git commit --no-verify"
    echo
    exit 1
fi
EOF

# Make hook executable
chmod +x "$HOOK_FILE"

echo "✅ Pre-commit hook installed successfully!"
echo
echo "Location: $HOOK_FILE"
echo
echo "The hook will:"
echo "  • Run all tests before each commit"
echo "  • Prevent commits if tests fail"
echo "  • Can be bypassed with: git commit --no-verify"
echo
echo "To test the hook, try making a commit:"
echo "  git commit -m \"test commit\""
echo
echo "========================================="
