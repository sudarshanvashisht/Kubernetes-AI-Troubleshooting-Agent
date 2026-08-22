from fastapi import APIRouter
from loguru import logger
import json
from app.kubernetes.kubectl import kubectl

router = APIRouter(tags=["Clusters"])


@router.get("/clusters")
async def get_clusters():
    """Retrieve list of available Kubernetes cluster contexts from kubeconfig."""
    result = await kubectl.run("config get-contexts -o json")

    clusters = []
    current_context = None

    if result.success and result.stdout:
        try:
            data = json.loads(result.stdout)
            if isinstance(data, list):
                for item in data:
                    name = item.get("name")
                    if name:
                        clusters.append(name)
                        if item.get("current"):
                            current_context = name
            elif isinstance(data, dict):
                contexts = data.get("contexts", [])
                current_context = data.get("current-context")
                for ctx in contexts:
                    name = ctx.get("name")
                    if name:
                        clusters.append(name)
        except Exception as e:
            logger.warning(f"Failed to parse kubectl contexts json: {e}")

    # Fallback if json parsing didn't find contexts
    if not clusters:
        res_plain = await kubectl.run("config get-contexts --no-headers")
        if res_plain.success and res_plain.stdout:
            for line in res_plain.stdout.splitlines():
                parts = line.split()
                if not parts:
                    continue
                if parts[0] == "*":
                    if len(parts) > 1:
                        name = parts[1]
                        clusters.append(name)
                        current_context = name
                else:
                    name = parts[0]
                    clusters.append(name)

    # Fallback to local default context
    if not clusters:
        clusters = ["kind-tws-cluster"]
        current_context = "kind-tws-cluster"

    return {
        "clusters": clusters,
        "current_context": current_context or (clusters[0] if clusters else None),
    }
