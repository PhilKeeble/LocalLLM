# Local LLM Docker Compose

This repo allows you to host LLMs locally in a network restricted container so that the model can't reach the internet and send telemetry / data, but still allows you to connect to it through caddy.

This Compose stack publishes Caddy on `0.0.0.0:8080` so other devices on your network can call the model API.

The LLM container is only attached to the `llm_internal` Docker network, which is marked `internal: true`. It does not publish ports directly to the host. Caddy is attached to both networks and proxies requests to `llm:8080`.

# Install / Setup

Clone this repository directly inside your WSL Ubuntu filesystem, not under `/mnt/c/...`.

Good:

```bash
cd ~
git clone <repo-url> LocalLLM
cd LocalLLM
```

Avoid:

```bash
cd /mnt/c/Users/<you>/Documents/GitHub
git clone <repo-url> LocalLLM
```

Keeping the repo and `models/` directory on the Linux filesystem avoids the Windows-to-WSL filesystem bridge during Docker builds and model reads.

1. Put your GGUF model files under `./models`.
2. Copy `.env.example` to `.env`.
3. From inside the WSL Ubuntu distro used by Docker, run:

```bash
python3 scripts/detect_host_env.py
```

4. Copy the printed `UBUNTU_VERSION`, `CUDA_VERSION`, and `CUDA_DOCKER_ARCH` values into `.env`.
5. Edit `models/models.ini` so its model paths and tuning match your GGUF files and desired llama args.
6. Build and start the stack:

```powershell
docker compose up 
```

The API will be reachable from the host and LAN at:

```text
http://<host-ip>:8080
```

For stricter egress blocking, add host firewall rules against the Docker network or container. Docker's `internal: true` network is the main isolation boundary in this Compose file.

## CUDA and WSL notes

The LLM image is built from BeeLlama's CUDA Dockerfile:

```text
https://github.com/Anbeeld/beellama.cpp/blob/main/.devops/cuda.Dockerfile
```

The build uses the `server` target and passes:

- `UBUNTU_VERSION`
- `CUDA_VERSION`
- `CUDA_DOCKER_ARCH`
- `CUDA_BUILD_TARGET=llama-server`

Use `nvidia-smi` to check the maximum CUDA version supported by your installed NVIDIA driver. The CUDA runtime in the container should be supported by that driver. It does not have to exactly match a CUDA toolkit installed in WSL; the NVIDIA driver compatibility is the important part.

Docker does not apply CPU or RAM limits unless configured, so this Compose file deliberately does not set `cpus`, `mem_limit`, or `deploy.resources.limits`. It does request all GPUs with `gpus: all`.

`CUDA_BUILD_TARGET` is fixed to `llama-server` in Compose. The GPU-specific performance setting is `CUDA_DOCKER_ARCH`, which maps to CMake's `CMAKE_CUDA_ARCHITECTURES`.

### Checking CUDA in WSL

From inside WSL, check that the NVIDIA driver is visible:

```bash
nvidia-smi
```

If that works, Docker GPU passthrough should have the driver side available. The CUDA version shown by `nvidia-smi` is the maximum CUDA runtime API version supported by the Windows NVIDIA driver.

To check whether the full CUDA toolkit is installed inside WSL:

```bash
nvcc --version
```

If `nvcc` is missing, the CUDA toolkit is not installed in WSL. That is usually fine for this project because the Docker image builds with an NVIDIA CUDA base image. The important checks are:

```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

The second command confirms Docker containers can see the GPU.

## Checking WSL resource limits

The detection script also reports WSL memory, CPU, and `.wslconfig` findings:

```bash
python3 scripts/detect_host_env.py
```

It checks:

- RAM currently visible inside WSL from `/proc/meminfo`
- CPU threads currently visible inside WSL
- `%UserProfile%\.wslconfig`, when it can find it from WSL
- low memory or processor caps that may bottleneck Docker builds or large local LLMs

Example `.wslconfig`:

```ini
[wsl2]
memory=64GB
processors=16
swap=16GB
```

After changing `.wslconfig`, restart WSL from Windows:

```powershell
wsl --shutdown
```

Then reopen the WSL distro and run the detection script again. If Docker Desktop has its own resource limits enabled, check Docker Desktop settings as well.

## Model router

The container runs `llama-server` in router mode:

```text
--models-preset /models/models.ini
--models-max 1
```

No model is loaded directly by the Compose command. The router loads the requested model using its section in `models/models.ini`. With `--models-max 1`, only one model instance can be loaded at a time so it will automatically unload models for you if you request another.

Models sleep after 15 minutes without inference requests because the global preset contains:

```ini
sleep-idle-seconds = 900
```

Sleeping releases model and KV-cache memory. The next inference request automatically reloads the model.

The `[*]` section contains defaults inherited by every model. A named section defines a routable model:

```ini
[*]
n-gpu-layers = all
parallel = 1
flash-attn = on

[qwen-code]
model = /models/Qwen3.6-27B-NEO-CODE-HERE-2T-OT-Q5_K_S.gguf
model-draft = /models/Qwen3.6-27B-DFlash-Q4_K_M.gguf
spec-type = dflash
ctx-size = 128000
```

Add another section to make another model available. The Docker Compose file and `.env` do not need model-specific changes.

Select a model using the OpenAI-compatible `model` field:

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-code",
    "messages": [
      {"role": "user", "content": "Write a Python function."}
    ]
  }'
```

The router autoloads an unloaded model when it is requested. You can also inspect and control models directly:

```bash
curl http://localhost:8080/models
curl -X POST http://localhost:8080/models/load \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-code"}'
curl -X POST http://localhost:8080/models/unload \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-code"}'
```

After changing `models.ini`, refresh router discovery:

```bash
curl 'http://localhost:8080/models?reload=1'
```

The container listens on `8080` internally. Caddy publishes that as host/LAN port `8080`.

## Coding agent configuration

Reviewed against Pi's current main (package version 0.85.1) on 2026-09-18:
[model configuration](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/models.md)
and [settings](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/settings.md).

```bash
python3 scripts/generate_pi_config.py --settings-output pi-settings.json
```

The default input and `pi.json` output resolve relative to this repository, even
when running from `scripts/`. Explicit paths resolve relative to your working directory.
Regenerate after editing `models/models.ini`; Pi does not read the INI itself.

Merge `pi.json`'s `providers.local-llama` into `~/.pi/agent/models.json`.
Merge the optional `pi-settings.json` into `~/.pi/agent/settings.json` (or your
project's `.pi/settings.json`). Do not replace unrelated existing settings.
Restart Pi after installing the files.

The generated entries are `qwen3.8` and `qwen-uncensored`, both with the INI's
160000-token context. The draft GGUF is managed by BeeLlama, not exposed as a Pi model.
GPU, KV-cache and DFlash settings remain server-side. Neither model advertises
image input without a configured `mmproj`.

Qwen3.8 exposes **off, low, medium, high, xhigh** in Pi. Selecting high sends
xhigh because Qwen3.8 does not support high natively; models with the standard
mapping keep high as high. Unsupported minimal and max levels are hidden using
null entries. Generic `chat-template` compatibility
passes both `enable_thinking` and the selected `reasoning_effort` through
`chat_template_kwargs`; the old mapping incorrectly mapped xhigh to high.
`preserve_thinking` remains enabled for history. The uncensored model uses the
same template assumptions; validate its tool calls and thinking toggle in Pi.

Sampling (`temperature`, `top_k`, `top_p`, `min_p`) is copied from the INI into
`samplingParams`. These values override Pi's request defaults. Streaming usage
is enabled for token accounting; store and developer-role fields are disabled.
The output limit remains **64000 tokens including thinking**, configurable with
`--max-tokens`.

The optional settings fragment sets each model's initial thinking level from
`reasoning-effort` (currently xhigh), restricts model cycling to these two entries,
and enables automatic compaction. Each model reserves its output limit plus
4096 tokens of margin: **68096 reserved**, with **20000 recent tokens retained**.
At 160000 context, this puts the compaction threshold around **91904 tokens**.
This is deliberately conservative for long reasoning: it trades usable history
for output headroom. A large newly pasted prompt or tool result can still exceed
that margin. Use `/compact` before unusually large inputs. Compaction summarizes
history and cannot guarantee preservation of every detail.

The server's context limit and Pi's compaction threshold serve different purposes;
waiting for the server to exhaust context is not the desired compaction workflow.
The settings fragment does not set a thinking-token budget: effort levels remain
model instructions, and xhigh is not a fixed token cap.

Useful options:

```bash
python3 scripts/generate_pi_config.py \
  --base-url http://127.0.0.1:8080/v1 \
  --provider-name local-llama \
  --max-tokens 64000 \
  --output pi.json \
  --settings-output pi-settings.json
```

Use the host's LAN address if Pi runs on another machine. The supplied Caddy
configuration serves HTTP, so use HTTPS only if you separately configured TLS.
The placeholder API key is `pi`. `--api-key '$LOCAL_LLM_API_KEY'` writes an explicit
Pi environment-variable reference; set that variable wherever Pi runs if auth is
configured. A literal key can also be supplied.

Other optional Pi settings worth considering:

- `showCacheMissNotices: true` for cache and compaction diagnostics.
- `retry.provider.timeoutMs: 3600000` if long thinking requests hit a total request timeout;
  `httpIdleTimeoutMs` is separate and concerns periods without incoming data.
- On Windows, `defaultTools: ["read", "powershell", "edit", "write"]` for native shell use.
  Leave the normal bash tools for WSL.
- `pi --offline` disables startup network operations while keeping the configured
  local inference endpoint usable. This is separate from Docker network isolation.

Select the normal model with `pi --provider local-llama --model qwen3.8 --thinking xhigh`.
Use `/thinking` to change effort and `/model` to switch models. Switching models
will cause BeeLlama to unload the other model because the router allows one at a time.

# Normal usage

Start the stack in the background:

```bash
docker compose up -d
```

Stop and remove the containers and Docker networks, while keeping the built images and `./models` files:

```bash
docker compose down
```

Rebuild the LLM image when you change build args, CUDA version, Ubuntu version, or want to pick up a newer BeeLlama source version:

```bash
docker compose up -d --build
```

Force a fresh rebuild without cached Docker layers:

```bash
docker compose build --no-cache llm
docker compose up -d
```

Avoid this unless you intentionally want to delete named Docker volumes:

```bash
docker compose down -v
```

## Checking network isolation

Open a shell inside the running LLM container:

```bash
docker compose exec llm /bin/bash
```

If Bash is not available:

```bash
docker compose exec llm /bin/sh
```

From inside the container, the local llama-server health check should work:

```bash
curl -f http://localhost:8080/health
```

External network checks should fail because the `llm` service is only attached to the `internal: true` Docker network:

```bash
curl -I https://example.com
curl -I https://1.1.1.1
ping -c 3 1.1.1.1
```

Depending on the image, `ping` may not be installed or may be blocked by container capabilities. A failed `curl` to an external address is the more useful check.

From the host, inspect the networks attached to the LLM container:

```bash
docker compose ps
docker inspect $(docker compose ps -q llm) --format '{{json .NetworkSettings.Networks}}'
```

The `llm` container should only be attached to the internal network. The `caddy` container should be attached to both the public ingress network and the internal LLM network.

