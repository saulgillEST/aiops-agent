def plan_install(cluster="kind-nephio", namespace="nephio-system"):
    actions = [
        {"run":"bash", "cmd":"command -v kind >/dev/null || go install sigs.k8s.io/kind@v0.23.0"},
        {"run":"bash", "cmd":f"kind get clusters | grep -q '^{cluster}$' || kind create cluster --name {cluster}"},
        {"run":"helm", "cmd":"helm repo add nephio https://nephio-helm.storage.googleapis.com || true"},
        {"run":"helm", "cmd":"helm repo update"},
        {"run":"kubectl", "cmd":f"kubectl create ns {namespace} || true"},
        {"run":"helm", "cmd":f"helm upgrade --install nephio-core nephio/core --namespace {namespace} --version 5.x.x --wait"},
        {"run":"kubectl", "cmd":f"kubectl -n {namespace} get pods"},
    ]
    return {"clarify": None, "actions": actions, "summary": f"Install Nephio R5 in {cluster}/{namespace}"}
