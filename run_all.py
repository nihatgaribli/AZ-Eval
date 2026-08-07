"""8 qaçışı ardıcıl icra edir və hər birinin nəticəsini ayrıca bildirir.

Resume defolt açıqdır, ona görə yalnız çatışmayan sətirlər hesablanır.
Bir qaçış uğursuz olsa, qalanları DAYANDIRILMIR — hansının alınmadığı sonda
xülasədə görünür, beləcə bir model çökəndə bütün gecə itmir.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (model, dil, üslub, əlavə bayraqlar)
# 4-bit yalnız 4B+ üçün — 8 GB VRAM-a fp16-da sığmır.
RUNS = [
    ("Qwen/Qwen3-1.7B", "az", "default", []),
    ("Qwen/Qwen3-1.7B", "en", "default", []),
    ("Qwen/Qwen3-VL-4B-Instruct", "az", "default", ["--load-in-4bit"]),
    ("Qwen/Qwen3-VL-4B-Instruct", "en", "default", ["--load-in-4bit"]),
    ("issai/Qolda-AVL-5B", "az", "default", ["--load-in-4bit", "--trust-remote-code"]),
    ("issai/Qolda-AVL-5B", "en", "default", ["--load-in-4bit", "--trust-remote-code"]),
    ("issai/Qolda-AVL-5B", "az", "script", ["--load-in-4bit", "--trust-remote-code"]),
    ("issai/Qolda-AVL-5B", "en", "script", ["--load-in-4bit", "--trust-remote-code"]),
]


def main() -> int:
    results: list[tuple[str, int, float]] = []

    for index, (model, language, style, extra) in enumerate(RUNS, start=1):
        label = f"{model} [{language}/{style}]"
        cmd = [
            sys.executable, "-m", "src.run_eval",
            "--model", model,
            "--language", language,
            "--prompt-style", style,
            "--max-new-tokens", "32",
            "--batch-size", "8",
            "--seed", "0",
            *extra,
        ]
        print(f"\n{'=' * 72}\n[{index}/{len(RUNS)}] {label}\n{'=' * 72}", flush=True)

        started = time.time()
        completed = subprocess.run(cmd, cwd=ROOT)
        elapsed = time.time() - started

        results.append((label, completed.returncode, elapsed))
        state = "OK" if completed.returncode == 0 else f"XƏTA ({completed.returncode})"
        print(f"\n--> {state}  {elapsed / 60:.1f} dəq  {label}", flush=True)

    print(f"\n{'=' * 72}\nXÜLASƏ\n{'=' * 72}", flush=True)
    for label, code, elapsed in results:
        state = "OK  " if code == 0 else "XƏTA"
        print(f"  {state}  {elapsed / 60:6.1f} dəq  {label}", flush=True)

    failed = sum(1 for _, code, _ in results if code != 0)
    print(f"\n{len(results) - failed}/{len(results)} uğurlu", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
