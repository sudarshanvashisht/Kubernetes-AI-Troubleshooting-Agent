"""Kubectl command executor.

Provides a safe, structured interface for executing kubectl commands
via subprocess. All Kubernetes modules use this as the single entry
point for cluster interaction.
"""

import asyncio
import shlex
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

from app.core.config import settings


@dataclass
class KubectlResult:
    """Structured result from a kubectl command execution."""

    success: bool
    stdout: str = ""
    stderr: str = ""
    command: str = ""
    return_code: int = 0


class KubectlExecutor:
    """Executes kubectl commands safely via async subprocess."""

    def __init__(self, kubeconfig_path: Optional[str] = None):
        self.kubeconfig_path = kubeconfig_path or settings.kubeconfig_path

    async def run(self, command: str, timeout: int = 30, context: Optional[str] = None) -> KubectlResult:
        """Execute a kubectl command and return structured result.

        Args:
            command: The kubectl command to run (e.g., 'get pods -A -o json').
            timeout: Maximum seconds to wait for command completion.
            context: Optional Kubernetes context name.

        Returns:
            KubectlResult with success status, stdout, stderr, and return code.
        """
        full_command = f"kubectl --kubeconfig {self.kubeconfig_path}"
        if context:
            full_command += f" --context {context}"
        full_command += f" {command}"
        logger.info(f"Executing: {full_command}")

        try:
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            stdout_str = stdout.decode("utf-8", errors="replace").strip()
            stderr_str = stderr.decode("utf-8", errors="replace").strip()
            success = process.returncode == 0

            if not success:
                logger.warning(
                    f"kubectl command failed (rc={process.returncode}): {stderr_str}"
                )
                # If localhost fails inside Docker container, retry using kind container endpoint
                if ("127.0.0.1" in stderr_str or "connection refused" in stderr_str.lower()) and "config get-contexts" not in command:
                    logger.info("Retrying command via kind container endpoint (https://tws-cluster-control-plane:6443)...")
                    retry_cmd = f"kubectl --kubeconfig {self.kubeconfig_path}"
                    if context:
                        retry_cmd += f" --context {context}"
                    retry_cmd += f" --server https://tws-cluster-control-plane:6443 --insecure-skip-tls-verify=true {command}"
                    try:
                        p2 = await asyncio.create_subprocess_shell(
                            retry_cmd,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                        )
                        out2, err2 = await asyncio.wait_for(p2.communicate(), timeout=timeout)
                        if p2.returncode == 0:
                            return KubectlResult(
                                success=True,
                                stdout=out2.decode("utf-8", errors="replace").strip(),
                                stderr=err2.decode("utf-8", errors="replace").strip(),
                                command=retry_cmd,
                                return_code=0,
                            )
                    except Exception as retry_err:
                        logger.warning(f"Retry via kind endpoint failed: {retry_err}")
            else:
                logger.debug(f"kubectl command succeeded: {command}")

            return KubectlResult(
                success=success,
                stdout=stdout_str,
                stderr=stderr_str,
                command=full_command,
                return_code=process.returncode or 0,
            )

        except asyncio.TimeoutError:
            logger.error(f"kubectl command timed out after {timeout}s: {command}")
            return KubectlResult(
                success=False,
                stderr=f"Command timed out after {timeout} seconds",
                command=full_command,
                return_code=-1,
            )
        except Exception as e:
            logger.error(f"kubectl command error: {e}")
            return KubectlResult(
                success=False,
                stderr=str(e),
                command=full_command,
                return_code=-1,
            )


# Shared executor instance
kubectl = KubectlExecutor()
