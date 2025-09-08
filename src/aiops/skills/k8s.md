---
name: k8s
intents:
  - kubernetes
priority: 8
tags: ["k8s","kubectl","helm"]
---

# K8S GUIDANCE
- Use kubectl context checks before applying manifests.
- Prefer declarative helm charts with --wait and readiness checks.