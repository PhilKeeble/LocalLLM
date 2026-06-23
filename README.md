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

Generate a Pi custom-provider configuration from `models/models.ini`:

```bash
python3 scripts/generate_pi_config.py
```

This creates `pi.json`. Set the URL used by the machine running Pi when needed:

```bash
python3 scripts/generate_pi_config.py \
  --base-url https://llm.home.arpa:8080/v1
```

By default the generated provider sends a placeholder bearer token:

```json
"apiKey": "pi",
"authHeader": true
```

If Caddy or llama-server requires a real bearer token, generate the config with the literal key:

```bash
python3 scripts/generate_pi_config.py --base-url http://127.0.0.1:8080/v1 --api-key 'your-api-key'
```

Pi reads custom providers from:

```text
~/.pi/agent/models.json
```

Use the generated `pi.json` as that file, or merge its `providers.local-llama` object into an existing `models.json`. Generated model IDs match the section names in `models.ini`, such as `qwen-code`.

Useful generator options:

```bash
python3 scripts/generate_pi_config.py \
  --models-ini models/models.ini \
  --output pi.json \
  --provider-name local-llama \
  --api-key pi \
  --max-tokens 16384
```

The generated file is deliberately Pi-specific and intended as an editable starting point. It includes:

- model IDs and display names
- context windows from `ctx-size`
- configurable output-token limits
- reasoning support and model-specific thinking controls
- Qwen chat-template thinking controls
- Gemma 4 boolean chat-template thinking controls
- text or image input when `mmproj` is configured
- zero local inference costs
- llama.cpp-compatible request settings

Qwen reasoning models additionally receive `compat.thinkingFormat = "qwen-chat-template"`.
Gemma 4 reasoning models receive `compat.thinkingFormat = "chat-template"` with `chatTemplateKwargs.enable_thinking` wired to Pi's thinking toggle. Gemma 4 does not receive a `thinkingLevelMap` because llama.cpp exposes this as an on/off template setting rather than meaningful low/medium/high levels.
Pi expects `thinkingFormat` under `compat`, not at the model's top level.

After generation, edit `pi.json` directly for model-specific preferences that cannot be inferred from `models.ini`, such as a custom display name, a different `maxTokens`, or manually declaring image support.

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

