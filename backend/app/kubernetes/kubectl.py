"""Kubectl command executor (hardened).

Executes kubectl via asyncio subprocess WITHOUT a shell. All inputs are
validated and passed as argv elements. No string interpolation into a shell.
"""

import asyncio
import os
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from loguru import logger

from app.core.config import settings

NAMESPACE_RE = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")
CONTEXT_RE = re.compile(r"^[A-Za-z0-9._:/@-]+$")

ALLOWED_VERBS = {"get", "logs", "describe", "config"}
# For `config`, only `get-contexts` is allowed.
ALLOWED_SUBCOMMANDS = {"get-contexts"}

MAX_NAMESPACE_LEN = 63
MAX_CONTEXT_LEN = 253


class ValidationError(ValueError):
    pass


def validate_namespace(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    if len(value) > MAX_NAMESPACE_LEN:
        raise ValidationError("namespace too long")
    if not NAMESPACE_RE.match(value):
        raise ValidationError("invalid namespace")
    return value


def validate_context(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    if len(value) > MAX_CONTEXT_LEN:
        raise ValidationError("context too long")
    if not CONTEXT_RE.match(value):
        raise ValidationError("invalid context")
    if ".." in value or value.startswith("/"):
        raise ValidationError("invalid context")
    return value


def resolve_kubeconfig(path_str: str) -> str:
    p = Path(path_str).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise ValidationError("kubeconfig does not exist or is not a file")
    if settings.kubeconfig_allowlist_dir:
        allow = Path(settings.kubeconfig_allowlist_dir).expanduser().resolve()
        try:
            p.relative_to(allow)
        except ValueError:
            raise ValidationError("kubeconfig outside allowlisted directory")
    return str(p)


@dataclass
class KubectlResult:
    success: bool
    stdout: str = ""
    stderr: str = ""
    command: List[str] = None
    return_code: int = 0

    def __post_init__(self):
        if self.command is None:
            self.command = []


class KubectlExecutor:
    def __init__(self, kubeconfig_path: Optional[str] = None, max_concurrent: int = 5):
        self.kubeconfig_path = resolve_kubeconfig(kubeconfig_path or settings.kubeconfig_path)
        self._sem = asyncio.Semaphore(max_concurrent or settings.kubectl_semaphore_size)

    async def run(self, args: List[str], timeout: int = 30, context: Optional[str] = None, namespace: Optional[str] = None) -> KubectlResult:
        # args: list of strings, never a shell string
        if not isinstance(args, list) or not all(isinstance(a, str) for a in args):
            raise ValidationError("args must be a list of strings")
        if not args:
            raise ValidationError("empty command")

        # validate verb
        verb = args[0]
        if verb not in ALLOWED_VERBS:
            raise ValidationError(f"verb not allowed: {verb}")
        if verb == "config":
            if len(args) < 2 or args[1] not in ALLOWED_SUBCOMMANDS:
                raise ValidationError("config subcommand not allowed")
        # validate namespace/context
        ns = validate_namespace(namespace)
        ctx = validate_context(context)

        # build argv
        argv = ["kubectl", f"--kubeconfig={self.kubeconfig_path}"]
        if ctx:
            argv.append(f"--context={ctx}")
        if ns:
            argv.append(f"--namespace={ns}")
        argv.extend(args)

        # resolve context against known contexts? only for config get-contexts we skip
        # (done at API layer for investigate)

        async with self._sem:
            return await self._exec(argv, timeout)

    async def _exec(self, argv: List[str], timeout: int) -> KubectlResult:
        logger.info(f"Executing (argv): {argv}")
        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                try:
                    await proc.wait()
                except Exception:
                    pass
                return KubectlResult(success=False, stdout="", stderr=f"Command timed out after {timeout} seconds", command=argv, return_code=-1)

            stdout_str = stdout.decode("utf-8", errors="replace").strip()
            stderr_str = stderr.decode("utf-8", errors="replace").strip()
            success = proc.returncode == 0
            if not success:
                logger.warning(f"kubectl failed (rc={proc.returncode}): {stderr_str}")
            return KubectlResult(success=success, stdout=stdout_str, stderr=stderr_str, command=argv, return_code=proc.returncode or 0)
        except Exception as e:
            logger.error(f"kubectl exec error: {e}")
            if proc is not None:
                try:
                    proc.kill()
                except Exception:
                    pass
            return KubectlResult(success=False, stderr=str(e), command=argv, return_code=-1)


# shared instance
kubectl = KubectlExecutor()
