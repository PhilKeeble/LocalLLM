#!/usr/bin/env python3
"""Print .env values for the BeeLlama CUDA Docker build.

Run this inside the WSL Ubuntu distro that Docker Desktop is integrated with:

    python3 scripts/detect_host_env.py

The output is intended to be copied into .env.
"""

from __future__ import annotations

import argparse
import configparser
import os
import platform
import re
import subprocess
import sys
from pathlib import Path


GPU_ARCH_BY_NAME = {
    "rtx 3090": "86",
    "rtx 3080": "86",
    "rtx 3070": "86",
    "rtx 3060": "86",
    "rtx 4090": "89",
    "rtx 4080": "89",
    "rtx 4070": "89",
    "rtx 4060": "89",
    "rtx 5090": "120",
    "rtx 5080": "120",
    "rtx 5070": "120",
    "a100": "80",
    "h100": "90",
    "h200": "90",
    "l40": "89",
    "l4": "89",
}

MIN_RECOMMENDED_WSL_MEMORY_GB = 32
MIN_RECOMMENDED_WSL_CPUS = 8


def run(command: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def read_ubuntu_version() -> tuple[str | None, str | None]:
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return None, "/etc/os-release was not found. Run this inside your WSL Ubuntu distro."

    values: dict[str, str] = {}
    for line in os_release.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')

    if values.get("ID") != "ubuntu":
        return None, f"Detected {values.get('PRETTY_NAME', 'a non-Ubuntu distro')}; expected Ubuntu."

    version = values.get("VERSION_ID")
    if not version:
        return None, "Could not find VERSION_ID in /etc/os-release."

    return version, None


def read_nvidia_smi_text() -> tuple[str | None, str | None]:
    result = run(["nvidia-smi"])
    if result is None:
        return None, "nvidia-smi was not found."
    if result.returncode != 0:
        return None, result.stderr.strip() or "nvidia-smi failed."
    return result.stdout, None


def parse_cuda_version(nvidia_smi_text: str) -> str | None:
    patterns = [
        r"CUDA Version:\s*([0-9]+(?:\.[0-9]+){0,2})",
        r"CUDA UMD Version:\s*([0-9]+(?:\.[0-9]+){0,2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, nvidia_smi_text)
        if match:
            return match.group(1)
    return None


def query_gpus() -> tuple[list[tuple[str, str | None]], str | None]:
    query = run(
        [
            "nvidia-smi",
            "--query-gpu=name,compute_cap",
            "--format=csv,noheader,nounits",
        ]
    )
    if query is not None and query.returncode == 0:
        gpus: list[tuple[str, str | None]] = []
        for line in query.stdout.splitlines():
            parts = [part.strip() for part in line.split(",")]
            if not parts or not parts[0]:
                continue
            compute_cap = parts[1].replace(".", "") if len(parts) > 1 and parts[1] else None
            gpus.append((parts[0], compute_cap))
        if gpus:
            return gpus, None

    fallback = run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader,nounits"])
    if fallback is not None and fallback.returncode == 0:
        names = [line.strip() for line in fallback.stdout.splitlines() if line.strip()]
        if names:
            return [(name, None) for name in names], "nvidia-smi did not report compute_cap."

    return [], "Could not query NVIDIA GPU name or compute capability."


def infer_compute_arch(name: str) -> str | None:
    lowered = name.lower()
    for token, arch in GPU_ARCH_BY_NAME.items():
        if token in lowered:
            return arch
    return None


def choose_cuda_arch(gpus: list[tuple[str, str | None]]) -> tuple[str, list[str]]:
    warnings: list[str] = []
    detected: list[tuple[str, str]] = []

    for name, compute_cap in gpus:
        arch = compute_cap or infer_compute_arch(name)
        if arch:
            detected.append((name, arch))
        else:
            warnings.append(f"Could not infer CUDA architecture for GPU: {name}")

    unique_arches = sorted({arch for _, arch in detected})
    if not unique_arches:
        return "default", warnings

    if len(unique_arches) > 1:
        names = ", ".join(f"{name}={arch}" for name, arch in detected)
        warnings.append(
            "Multiple GPU architectures detected. Using all of them for CMAKE_CUDA_ARCHITECTURES: "
            + names
        )
        return ";".join(unique_arches), warnings

    return unique_arches[0], warnings


def running_under_wsl() -> bool:
    text = " ".join(
        [
            platform.release(),
            platform.version(),
            os.environ.get("WSL_DISTRO_NAME", ""),
        ]
    ).lower()
    return "microsoft" in text or "wsl" in text


def parse_size_to_bytes(value: str) -> int | None:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([kmgtp]?b?)?\s*", value, re.IGNORECASE)
    if not match:
        return None

    number = float(match.group(1))
    unit = (match.group(2) or "b").lower()
    multipliers = {
        "": 1,
        "b": 1,
        "k": 1024,
        "kb": 1024,
        "m": 1024**2,
        "mb": 1024**2,
        "g": 1024**3,
        "gb": 1024**3,
        "t": 1024**4,
        "tb": 1024**4,
        "p": 1024**5,
        "pb": 1024**5,
    }
    multiplier = multipliers.get(unit)
    if multiplier is None:
        return None
    return int(number * multiplier)


def bytes_to_gb(value: int) -> float:
    return value / 1024**3


def read_mem_total_bytes() -> int | None:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return None

    for line in meminfo.read_text(encoding="utf-8").splitlines():
        if line.startswith("MemTotal:"):
            parts = line.split()
            if len(parts) >= 2:
                return int(parts[1]) * 1024
    return None


def get_windows_profile_from_wsl() -> Path | None:
    if os.environ.get("USERPROFILE"):
        return Path(os.environ["USERPROFILE"])

    result = run(["cmd.exe", "/c", "echo", "%USERPROFILE%"])
    if result is None or result.returncode != 0:
        return None

    profile = result.stdout.strip().replace("\\", "/")
    match = re.fullmatch(r"([A-Za-z]):/(.*)", profile)
    if not match:
        return None

    drive = match.group(1).lower()
    rest = match.group(2)
    return Path(f"/mnt/{drive}/{rest}")


def read_wslconfig() -> tuple[Path | None, dict[str, str], str | None]:
    profile = get_windows_profile_from_wsl()
    if profile is None:
        return None, {}, "Could not locate the Windows user profile to check .wslconfig."

    config_path = profile / ".wslconfig"
    if not config_path.exists():
        return config_path, {}, ".wslconfig was not found. WSL will use defaults unless Docker Desktop applies its own limits."

    parser = configparser.ConfigParser()
    try:
        parser.read(config_path, encoding="utf-8")
    except configparser.Error as exc:
        return config_path, {}, f"Could not parse {config_path}: {exc}"

    if not parser.has_section("wsl2"):
        return config_path, {}, f"{config_path} does not have a [wsl2] section."

    return config_path, dict(parser.items("wsl2")), None


def collect_wsl_performance_notes() -> list[str]:
    notes: list[str] = []
    is_wsl = running_under_wsl()
    mem_total = read_mem_total_bytes()
    cpu_count = os.cpu_count()
    config_path, wsl2_config, config_warning = read_wslconfig()

    if mem_total is not None:
        mem_gb = bytes_to_gb(mem_total)
        notes.append(f"WSL currently exposes about {mem_gb:.1f} GiB RAM to Linux.")
        if mem_gb < MIN_RECOMMENDED_WSL_MEMORY_GB:
            notes.append(
                f"WSL RAM is below {MIN_RECOMMENDED_WSL_MEMORY_GB} GiB; large contexts/models may be memory constrained."
            )
    else:
        notes.append("Could not read WSL memory from /proc/meminfo.")

    if cpu_count is not None:
        if is_wsl:
            notes.append(f"WSL currently exposes {cpu_count} CPU thread(s) to Linux.")
        else:
            notes.append(f"This shell sees {cpu_count} CPU thread(s); run inside WSL for the effective Linux count.")
        if cpu_count < MIN_RECOMMENDED_WSL_CPUS:
            notes.append(
                f"WSL CPU count is below {MIN_RECOMMENDED_WSL_CPUS}; build and CPU-side prompt work may be constrained."
            )

    if config_warning:
        notes.append(config_warning)
    elif config_path is not None:
        notes.append(f"Found WSL config: {config_path}")

    memory_setting = wsl2_config.get("memory")
    if memory_setting:
        memory_bytes = parse_size_to_bytes(memory_setting)
        if memory_bytes is None:
            notes.append(f".wslconfig memory setting could not be parsed: {memory_setting}")
        else:
            memory_gb = bytes_to_gb(memory_bytes)
            notes.append(f".wslconfig memory cap is {memory_setting} ({memory_gb:.1f} GiB).")
            if memory_gb < MIN_RECOMMENDED_WSL_MEMORY_GB:
                notes.append(
                    f"Consider raising .wslconfig memory above {MIN_RECOMMENDED_WSL_MEMORY_GB}GB for large local LLMs."
                )
    elif wsl2_config:
        notes.append(".wslconfig does not set memory; WSL memory is dynamic unless Docker Desktop limits it.")

    processors_setting = wsl2_config.get("processors")
    if processors_setting:
        try:
            processors = int(processors_setting)
        except ValueError:
            notes.append(f".wslconfig processors setting could not be parsed: {processors_setting}")
        else:
            notes.append(f".wslconfig processors cap is {processors}.")
            if processors < MIN_RECOMMENDED_WSL_CPUS:
                notes.append(
                    f"Consider raising .wslconfig processors to at least {MIN_RECOMMENDED_WSL_CPUS}, if the host has enough cores."
                )
    elif wsl2_config:
        notes.append(".wslconfig does not set processors; WSL can use the default CPU allocation.")

    swap_setting = wsl2_config.get("swap")
    if swap_setting:
        swap_bytes = parse_size_to_bytes(swap_setting)
        if swap_bytes == 0:
            notes.append(".wslconfig swap is disabled. That can improve predictability but increases OOM risk.")
        elif swap_bytes is not None:
            notes.append(f".wslconfig swap is {swap_setting} ({bytes_to_gb(swap_bytes):.1f} GiB).")

    return notes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect Ubuntu, CUDA, and GPU architecture values for .env."
    )
    parser.add_argument(
        "--env-only",
        action="store_true",
        help="Print only KEY=value lines.",
    )
    parser.add_argument(
        "--skip-wsl-checks",
        action="store_true",
        help="Do not print WSL memory/CPU/.wslconfig notes.",
    )
    args = parser.parse_args()

    ubuntu_version, ubuntu_warning = read_ubuntu_version()
    nvidia_text, nvidia_warning = read_nvidia_smi_text()
    cuda_version = parse_cuda_version(nvidia_text) if nvidia_text else None
    gpus, gpu_warning = query_gpus()
    cuda_arch, arch_warnings = choose_cuda_arch(gpus)

    values = {
        "UBUNTU_VERSION": ubuntu_version or "22.04",
        "CUDA_VERSION": cuda_version or "12.4.1",
        "CUDA_DOCKER_ARCH": cuda_arch,
    }

    warnings = [
        warning
        for warning in [ubuntu_warning, nvidia_warning, gpu_warning]
        if warning
    ]
    warnings.extend(arch_warnings)
    if not running_under_wsl():
        warnings.append(
            "This does not look like WSL. Re-run inside the WSL Ubuntu distro used by Docker."
        )

    if not args.env_only:
        print("# Copy these values into .env")
    for key, value in values.items():
        print(f"{key}={value}")

    if warnings and not args.env_only:
        print("\n# Warnings", file=sys.stderr)
        for warning in warnings:
            print(f"- {warning}", file=sys.stderr)

    if not args.env_only and not args.skip_wsl_checks:
        print("\n# WSL performance checks", file=sys.stderr)
        for note in collect_wsl_performance_notes():
            print(f"- {note}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
