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

Keeping the repo and `models/` directory on the Linux filesystem avoids the Windows-to-WSL filesystem bridge during model reads.

1. Put your GGUF model files under `./models`.
2. Check the model paths and tuning in `docker-compose.yml`. Settings are defined directly in this file; no `.env` file is needed.
3. Start the stack from WSL Ubuntu with live logs:

```bash
docker compose up
```

Compose downloads BeeLlama's prebuilt CUDA 13 server image if it is missing locally;
no local compilation or CUDA toolkit is required. Subsequent starts can run offline
once both service images and the model files are available locally.

The API will be reachable from the host and LAN at:

```text
http://<host-ip>:8080
```

For stricter egress blocking, add host firewall rules against the Docker network or container. Docker's `internal: true` network is the main isolation boundary in this Compose file.

## CUDA and WSL notes

The LLM service uses `ghcr.io/anbeeld/beellama.cpp:server-cuda13`, the rolling
prebuilt CUDA 13 server image. `pull_policy: missing` reuses the local image without
checking for updates, downloading it only if missing. Run `docker compose pull llm`
when you want an update, then `docker compose up` to apply it with live logs.
A running container does not update itself, and `docker compose restart` does not
pull or apply a new image.

Image pulls are performed by Docker; the model container retains its internal-only
network. Keep the NVIDIA driver compatible with the CUDA runtime in the published
image. No local Ubuntu/CUDA build-version or GPU-architecture settings are needed.

Docker does not apply CPU or RAM limits unless configured, so this Compose file
does not set `cpus`, `mem_limit`, or `deploy.resources.limits`. It requests all GPUs
with `gpus: all`.

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

If `nvcc` is missing, the CUDA toolkit is not installed in WSL. That is usually fine for this project because the prebuilt image contains the CUDA runtime. The important checks are:

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
- low memory or processor caps that may bottleneck large local LLMs

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

## Single-model server

Compose starts one `llama-server` process and immediately loads Qwen Uncensored
and its DFlash2 draft. There is no model router. The API model name remains
`qwen-uncensored`; Caddy continues to publish port 8080 with the same network isolation.

The server arguments live in `docker-compose.yml`. `models/models.ini` is retained
as input for the Pi configuration generator; the server does not read it.

`--load-mode dio` uses direct I/O when supported to avoid retaining a model-sized
Linux file cache after loading. It still needs application RAM and temporary
loading buffers. No cache-flushing helper or privileged container is required.

`--sleep-idle-seconds 900` retains the 15-minute idle timeout. Sleep releases the
models and KV cache; the next inference request reloads them using direct I/O.
Use `--sleep-idle-seconds -1` to keep the model loaded continuously.

After changing launch arguments, recreate the service without rebuilding the image:

```bash
docker compose up
```

Logs stay attached to the terminal; Ctrl+C stops the stack.

```bash
curl http://localhost:8080/v1/models
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-uncensored","messages":[{"role":"user","content":"Write a Python function."}]}'
```

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

The generated entry is `qwen-uncensored`, with the INI's
160000-token context. The draft GGUF is managed by BeeLlama, not exposed as a Pi model.
GPU, KV-cache and DFlash settings remain server-side. The model does not advertise
image input without a configured `mmproj`.

The Qwen3.8-based uncensored model exposes **off, low, medium, high, xhigh** in Pi. Selecting high sends
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
`reasoning-effort` (currently medium), restricts model cycling to this entry,
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

Select the model with `pi --provider local-llama --model qwen-uncensored --thinking medium`.
Use `/thinking` to change effort. This stack serves only `qwen-uncensored`.

# Normal usage

Start the stack with live logs in the terminal, using the downloaded images:

```bash
docker compose up
```

Press Ctrl+C to stop the stack. To also remove the containers and Docker networks,
while keeping downloaded images and `./models` files:

```bash
docker compose down
```

When you want to update, stop the attached stack with Ctrl+C, then fetch the latest
published CUDA 13 image and start again with live logs:

```bash
docker compose pull llm
docker compose up
```

Only the pull step needs registry access when the images are already on disk.
Docker downloads missing or changed layers; normal `up` runs keep using that image
until you explicitly pull an update.

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

