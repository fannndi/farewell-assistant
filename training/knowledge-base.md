# Training Knowledge Base

Generated: 2026-06-19 22:38:56
Test cases: 50
Duration: 279.2s

## Accuracy Metrics

Overall: 68%
- Intent: 54%
- Domain: 44%
- Complexity: 76%
- Hold: 98%

## Domain Detection Keywords

mobile: flutter, dart, kotlin, android, ios, swift, react native, firebase, push notification, screen, app
web: api, crud, auth, react, vue, next, django, fastapi, express, endpoint
infra: docker, kubernetes, deploy, ci/cd, pipeline, config, setup
automation: powershell, script, task, schedule, windows, registry

## Chains

build_web: 8 steps - orch-add-feature → api-design → backend-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow
build_mobile: 7 steps - orch-add-feature → dart-flutter-patterns → database-migrations → tdd-workflow → security-review → verification-loop → git-workflow
build_infra: 7 steps - orch-add-feature → deployment-patterns → docker-patterns → kubernetes-patterns → database-migrations → verification-loop → git-workflow
fix_bug: 5 steps - search-first → orch-fix-defect → ai-regression-testing → verification-loop → git-workflow
review_code: 5 steps - coding-standards → error-handling → security-review → codehealth-mcp → verification-loop
deploy: 4 steps - production-audit → deployment-patterns → canary-watch → git-workflow
