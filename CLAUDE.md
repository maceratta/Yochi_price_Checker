# Claude Code Git Workflow Guide

## 🎯 MANDATORY STEPS FOR NEW PROJECTS

### Step 1: Detect New Project
**When I notice this is a new project, I MUST ask:**
```
🚀 New Project Detected

This appears to be a new project. Following best practices, I recommend:
1. Creating a private GitHub repository
2. Setting up version control 
3. Implementing regular commits for progress tracking

Project name suggestion: [suggest based on context]
Shall I set this up? (y/n)
```

### Step 2: Repository Creation
```bash
# Always create private repository
gh repo create [PROJECT_NAME] --private --description "[Auto-generated description]"

# Initialize locally  
git init
git remote add origin https://github.com/[username]/[PROJECT_NAME].git

# Security first - create .gitignore
cat > .gitignore << 'EOF'
# Sensitive configurations
config.json
*.env
secrets/
credentials/

# Runtime files
*.log  
*.pid
cache/
temp/

# OS and IDE
.DS_Store
.vscode/
__pycache__/
EOF
```

### Step 3: Initial Commit
```bash
git add .
git commit -m "INIT: [Project description] setup

Initial project structure:
- [List key files created]
- [Mention main functionality]
- Basic configuration and documentation

🤖 Generated with Claude Code (https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin main
```

## 🔄 ONGOING COMMIT WORKFLOW

### When to Ask User for Commit
**After completing any of these:**
1. **Feature Implementation** (new functionality working)
2. **Bug Fix** (issue resolved and tested)
3. **Configuration Changes** (settings modified)
4. **Documentation Updates** (README, comments added)
5. **File Structure Changes** (files moved, renamed, deleted)
6. **Major Refactoring** (code reorganized)
7. **Before Risky Changes** (as backup checkpoint)

### Commit Request Flow
```
🔄 COMMIT CHECKPOINT

I've completed: [Brief description of work]

Changes made:
✅ [Specific change 1] - [why/benefit]
✅ [Specific change 2] - [why/benefit] 
✅ [Specific change 3] - [why/benefit]

Files modified: [file1.py, config.template.json, README.md]

This creates a restore point you can rollback to if needed.
Shall I commit these changes? (y/n)

If no: I'll continue working and ask again after the next major change.
If yes: I'll create a detailed commit with clear rollback information.
```

### Commit Execution
```bash
git add .
git status  # Show what's being committed
git commit -m "$(cat <<'EOF'
[TYPE]: [Clear description of accomplishment]

Detailed changes:
- [Change 1]: [Context and reasoning]
- [Change 2]: [Context and reasoning]
- [Change 3]: [Context and reasoning]

Files modified: [explicit list]
Functionality: [what user can now do]
Impact: [how this improves the project]

Rollback note: [Any important considerations for reverting]

🤖 Generated with Claude Code (https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git push
```

## 📊 PROGRESS TRACKING

### Session Start Routine
1. **Check current state:** `git status`
2. **Review recent work:** `git log --oneline -3`
3. **Understand context** before making changes

### Session End Routine  
1. **Final commit** if uncommitted changes exist
2. **Push all changes** to remote
3. **Summarize session** accomplishments

### Weekly Maintenance
- **Review commit history** for patterns
- **Clean up branches** if using feature branches
- **Update documentation** if project evolved

## 🛡️ SECURITY & ROLLBACK

### Pre-Commit Security Check
**Never commit files containing:**
- API keys, passwords, tokens
- Personal email addresses or phone numbers
- Absolute file paths specific to one machine
- Database connection strings with credentials

### Rollback Strategy
**Each commit message must enable easy rollback by including:**
1. **Exact files changed** (for selective rollback)
2. **Functionality added/removed** (to understand impact)
3. **Dependencies introduced** (to check compatibility)
4. **Configuration requirements** (to restore environment)

### Emergency Rollback Commands
```bash
# View detailed commit history
git log --oneline --graph --decorate -10

# Soft rollback (keep changes in working directory)
git reset --soft [commit-hash]

# Hard rollback (lose all changes)  
git reset --hard [commit-hash]

# Cherry-pick specific changes
git cherry-pick [commit-hash]
```

## 🎯 COMMUNICATION TEMPLATES

### Repository Creation Request
```
📋 GitHub Repository Setup

I recommend creating a private repository for this project:

Repository name: "[suggested-name]"
Description: "[auto-generated based on project]"
Visibility: Private (can change later)

Benefits:
- Version control for all changes
- Easy rollback if something breaks  
- Professional development practices
- Safe collaboration when needed

Create repository? (y/n)
```

### Major Change Warning
```
⚠️ Significant Changes Ahead

I'm about to make substantial changes to:
- [System/file that will be modified]
- [What functionality will change]

I recommend committing current state as a checkpoint first.
This ensures we can rollback if anything goes wrong.

Create checkpoint commit? (y/n)
```

### End of Session Summary
```
📋 Session Complete

Accomplished:
✅ [Achievement 1]
✅ [Achievement 2] 
✅ [Achievement 3]

Commits made: [number] ([view on GitHub link])
Files modified: [count] 
Next steps: [suggestions for user]

All changes pushed to GitHub for safekeeping.
```

## ⚡ QUICK REFERENCE

```bash
# New project setup
gh repo create NAME --private
git init && git remote add origin [URL]
echo "config.json" > .gitignore

# Regular commits
git add . && git commit -m "[TYPE]: Description" && git push

# Emergency rollback  
git log --oneline && git reset --hard [hash]

# Check status
git status && git log --oneline -3
```