# Contributing to Smart Resource Allocation

## Team Workflow

### Branches
- main — Production-ready code
- feature/backend — Backend work
- feature/frontend — Frontend work
- feature/auth-database — Firebase work
- feature/devops — DevOps work

### How to Contribute

1. Pull latest main:
git checkout main
git pull origin main

2. Switch branch:
git checkout feature/your-branch
git merge main

3. Commit:
git add <files>
git commit -m "feat: message"

4. Push:
git push origin feature/your-branch

### Rules
- Never push to main
- Always use PR
- Never upload .env or keys