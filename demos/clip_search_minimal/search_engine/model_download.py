"""One bounded, explicit setup step for the pinned model checkpoint."""
import hashlib
import math
from pathlib import Path
import tempfile
import time
import urllib.error
import urllib.request

from search_engine.model_artifacts import MAX_CHECKPOINT_BYTES, ModelSetupError, ModelSpec, VIT_B_32, verify_checkpoint
from search_engine.settings import MODEL_DIR

DOWNLOAD_TIMEOUT_SECONDS = 15
DOWNLOAD_DEADLINE_SECONDS = 300


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ModelSetupError('Checkpoint download redirects are not permitted.')


def run_download_model(model_dir: Path = MODEL_DIR, *, spec: ModelSpec = VIT_B_32,
                       timeout: float = DOWNLOAD_TIMEOUT_SECONDS,
                       deadline: float = DOWNLOAD_DEADLINE_SECONDS) -> Path:
    """Publish only a size-bounded, SHA-256-verified HTTPS checkpoint; no retries."""
    if (not math.isfinite(timeout) or timeout <= 0 or not math.isfinite(deadline) or deadline <= 0
            or Path(spec.filename).name != spec.filename or not spec.url.startswith('https://')):
        raise ValueError('Invalid checkpoint download configuration.')
    model_dir = model_dir.resolve()
    model_dir.mkdir(parents=True, exist_ok=True)
    target = model_dir / spec.filename
    if target.exists():
        try:
            verify_checkpoint(target, spec)
            return target
        except ModelSetupError:
            pass  # Replace a damaged cache only after the replacement is verified.
    temporary: Path | None = None
    started = time.monotonic()
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with tempfile.NamedTemporaryFile(dir=model_dir, prefix='.checkpoint-', delete=False) as destination:
            temporary = Path(destination.name)
            with opener.open(spec.url, timeout=min(timeout, deadline)) as response:
                digest, total = hashlib.sha256(), 0
                while True:
                    if time.monotonic() - started >= deadline:
                        raise ModelSetupError('Checkpoint download exceeded its deadline.')
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_CHECKPOINT_BYTES:
                        raise ModelSetupError('Checkpoint download exceeded its size limit.')
                    digest.update(chunk)
                    destination.write(chunk)
                if digest.hexdigest() != spec.sha256:
                    raise ModelSetupError('Downloaded checkpoint failed SHA-256 verification.')
        temporary.replace(target)
        return target
    except (OSError, urllib.error.URLError) as exc:
        raise ModelSetupError('Checkpoint download failed or timed out. Retry the setup command.') from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
