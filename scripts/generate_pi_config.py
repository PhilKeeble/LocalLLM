#!/usr/bin/env python3
"""Generate Pi coding-agent configuration from models/models.ini."""

from __future__ import annotations

import argparse
import configparser
import json
import sys
from pathlib import Path
from typing import Any


FALSE_VALUES = {"0", "false", "no", "off", "none", ""}
TRUE_VALUES = {"1", "true", "yes", "on"}
THINKING_LEVEL_MAP = {
    "minimal": "low",
    "low": "low",
    "medium": "medium",
    "high": "high",
    "xhigh": "high",
}


def parse_models_ini(path: Path) -> tuple[dict[str, str], list[tuple[str, dict[str, str]]]]:
    if not path.is_file():
        raise ValueError(f"Models preset does not exist: {path}")

    text = path.read_text(encoding="utf-8")
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    parser.optionxform = str.lower

    # llama-server permits `version = 1` before the first INI section.
    parser.read_string("[__metadata__]\n" + text)

    version = parser.get("__metadata__", "version", fallback="1").strip()
    if version != "1":
        raise ValueError(f"Unsupported models.ini version: {version}")

    global_values = dict(parser.items("*")) if parser.has_section("*") else {}
    models: list[tuple[str, dict[str, str]]] = []

    for section in parser.sections():
        if section in {"__metadata__", "*"}:
            continue
        values = dict(global_values)
        values.update(dict(parser.items(section)))
        if "model" not in values and "hf-repo" not in values:
            raise ValueError(
                f"Preset [{section}] must define model or hf-repo to generate a provider model."
            )
        models.append((section, values))

    if not models:
        raise ValueError(f"No model presets found in {path}")

    return global_values, models


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    raise ValueError(f"Expected a boolean value, got: {value}")


def parse_positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"Expected an integer value, got: {value}") from exc
    if parsed <= 0:
        return default
    return parsed


def display_name(model_id: str) -> str:
    return model_id.replace("_", " ").replace("-", " ").title()


def pi_model(model_id: str, values: dict[str, str], default_max_tokens: int) -> dict[str, Any]:
    context_window = parse_positive_int(
        values.get("ctx-size") or values.get("c") or values.get("llama_arg_ctx_size"),
        128000,
    )
    reasoning = parse_bool(
        values.get("reasoning") or values.get("llama_arg_reasoning"),
        default=False,
    )
    max_tokens = min(default_max_tokens, context_window)

    model: dict[str, Any] = {
        "id": model_id,
        "name": display_name(model_id),
        "reasoning": reasoning,
        "input": ["text", "image"] if "mmproj" in values else ["text"],
        "contextWindow": context_window,
        "maxTokens": max_tokens,
        "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0,
        },
    }

    if reasoning:
        model["thinkingLevelMap"] = dict(THINKING_LEVEL_MAP)

    model_source = " ".join(
        [
            model_id,
            values.get("model", ""),
            values.get("hf-repo", ""),
        ]
    ).lower()
    if reasoning and "qwen" in model_source:
        model["compat"] = {
            "thinkingFormat": "qwen-chat-template",
            "chatTemplateKwargs": {
                "enable_thinking": {"$var": "thinking.enabled"},
                "preserve_thinking": True,
            },
        }

    return model


def generate_config(
    models: list[tuple[str, dict[str, str]]],
    base_url: str,
    provider_name: str,
    api_key_env: str,
    default_max_tokens: int,
) -> dict[str, Any]:
    return {
        "providers": {
            provider_name: {
                "baseUrl": base_url.rstrip("/"),
                "api": "openai-completions",
                "apiKey": f"${api_key_env}",
                "authHeader": False,
                "compat": {
                    "supportsDeveloperRole": True,
                    "supportsReasoningEffort": True,
                    "supportsUsageInStreaming": True,
                    "maxTokensField": "max_tokens",
                },
                "models": [
                    pi_model(model_id, values, default_max_tokens)
                    for model_id, values in models
                ],
            }
        }
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Pi configuration from a llama-server models.ini file."
    )
    parser.add_argument(
        "--models-ini",
        type=Path,
        default=Path("models/models.ini"),
        help="Path to the llama-server model preset file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("pi.json"),
        help="Output path. Defaults to pi.json.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8080/v1",
        help="OpenAI-compatible llama-server base URL.",
    )
    parser.add_argument(
        "--provider-name",
        default="local-llama",
        help="Provider identifier shown in the generated configuration.",
    )
    parser.add_argument(
        "--api-key-env",
        default="LLAMA_API_KEY",
        help="Environment variable Pi should read for the API key.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=32000,
        help="Default maximum output tokens for generated model entries.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        _, models = parse_models_ini(args.models_ini)
        if args.max_tokens <= 0:
            raise ValueError("--max-tokens must be greater than zero.")

        config = generate_config(
            models=models,
            base_url=args.base_url,
            provider_name=args.provider_name,
            api_key_env=args.api_key_env,
            default_max_tokens=args.max_tokens,
        )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    except (OSError, configparser.Error, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    model_names = ", ".join(model_id for model_id, _ in models)
    print(f"Wrote {args.output} with {len(models)} model(s): {model_names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
