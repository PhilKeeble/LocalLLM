# Local LLM Docker Compose

This repository runs a local model server and Markdown knowledge service behind Caddy. Caddy publishes HTTP on `0.0.0.0:8080`; the model and knowledge containers expose ports only on Docker's internal network.

Requests beneath `/kb/*` go to the knowledge service. All other requests go to the model's OpenAI-compatible API. The route has no authentication or TLS, so expose it only on a trusted network unless you add those controls.

## Requirements

- Docker with Compose support.
- An NVIDIA GPU, a compatible host driver, and NVIDIA container support.
- The GGUF model files named in `docker-compose.yml`, stored under `models/`.

For WSL, keeping the repository and model files in the Linux filesystem generally avoids the Windows-to-WSL filesystem bridge during model loading.

## Start and stop

From the repository root, start the stack with attached logs:

```sh
docker compose up
```

Compose builds the knowledge image and pulls missing service images. The API is then available at `http://localhost:8080` and, subject to the host firewall, at `http://<host-ip>:8080` on the LAN.

Check the model and knowledge endpoints:

```sh
curl http://localhost:8080/v1/models
curl http://localhost:8080/kb/status
```

Press Ctrl+C to stop an attached stack. To remove its containers and networks while retaining images, model files, and the knowledge index volume:

```sh
docker compose down
```

Do not add `-v` unless you intend to delete the persistent knowledge index and its historical revisions.

To fetch a newer published model-server image and recreate the stack:

```sh
docker compose pull llm
docker compose up
```

`docker compose restart` does not pull a new image or apply changes to Compose launch arguments.

## Model server

`docker-compose.yml` starts one BeeLlama server with the target model, DFlash draft model, chat template, GPU offload, context, sampling, cache, and idle-sleep settings defined directly in the service command. The public API model name is `qwen-uncensored`.

Edit the Compose command when model filenames or server tuning change, then run `docker compose up` to recreate the affected service. The `models/` mount is read-only. The `--sleep-idle-seconds 900` setting unloads model resources after 15 idle minutes; the next inference request reloads them.

Example request:

```sh
curl http://localhost:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen-uncensored","messages":[{"role":"user","content":"Write a Python function."}]}'
```

## Pi configuration

[`pi.json`](pi.json) contains the matching local provider and model definition. [`pi-settings.json`](pi-settings.json) contains the model selection, default thinking level, and compaction settings. Merge the relevant objects into Pi's configuration without replacing unrelated providers or settings, then restart Pi.

The checked-in model entry uses a 212,992-token context window, a 32,000-token output limit, text input, and the sampling values configured by the server. It maps Pi's `high` and `xhigh` levels to the model's `xhigh` reasoning level and leaves `minimal` and `max` unset. The settings reserve 32,000 tokens for output and retain 32,000 recent tokens during compaction.

Use the host's LAN address in `baseUrl` when Pi runs on another machine. The placeholder API key is present for client compatibility; the supplied Caddy route does not authenticate it.

## Knowledge service

The `kb` service indexes UTF-8 Markdown beneath `knowledge/` and persists its SQLite index in the `kb_index` volume. The library contains four kinds of material: focused vulnerability profiles, technical references, reusable investigation playbooks, and scoped notes. The service provides read-only search and citation access; update the host Markdown after external review.

See [the knowledge-service API](kb/README.md) for indexing and retrieval behavior and [the library guide](kb/LIBRARY.md) for content structure and quality requirements. Markdown changes are detected without rebuilding the image; service-code or dependency changes require a rebuild.

## GPU and WSL checks

In WSL, confirm that the Windows NVIDIA driver is visible:

```sh
nvidia-smi
```

The prebuilt model-server image supplies its runtime, so a local CUDA toolkit and `nvcc` are not required. If the stack cannot access the GPU, check Docker's NVIDIA container support and the service logs.

Docker does not impose CPU or memory limits unless configured. This Compose file requests all GPUs and sets no CPU or memory limit. WSL and Docker Desktop limits can still constrain the stack.

## Network isolation

The `llm` and `kb` services are attached only to `llm_internal`, which is declared `internal: true`. Caddy joins both that network and the ingress network and is the only service that publishes a host port. This prevents the model and knowledge containers from obtaining ordinary external network routing through Docker; it does not restrict the Caddy container or the host.

Inspect the effective attachments on a running stack:

```sh
docker compose ps
docker inspect $(docker compose ps -q llm) --format '{{json .NetworkSettings.Networks}}'
docker inspect $(docker compose ps -q kb) --format '{{json .NetworkSettings.Networks}}'
docker inspect $(docker compose ps -q caddy) --format '{{json .NetworkSettings.Networks}}'
```

The model and knowledge containers should show only the internal network. Caddy should show both networks. Add host firewall controls when the Docker boundary alone is insufficient for the deployment.
