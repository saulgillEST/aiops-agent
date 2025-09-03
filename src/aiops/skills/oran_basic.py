def plan_install_oran(cluster="kind-nephio", namespace="oran-system"):
    return {
        "clarify": None,
        "actions": [
            {"run":"helm","cmd":"helm repo add oran https://example/oran-helm || true"},
            {"run":"helm","cmd":"helm repo update"},
            {"run":"kubectl","cmd":f"kubectl create ns {namespace} || true"},
            {"run":"helm","cmd":f"helm upgrade --install oran-core oran/core --namespace {namespace} --version 5.x.x --wait"},
            {"run":"kubectl","cmd":f"kubectl -n {namespace} get pods"},
        ],
        "summary": f"Install O-RAN components in {cluster}/{namespace}"
    }
