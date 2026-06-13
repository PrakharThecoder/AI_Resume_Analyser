# Deploying AI Resume Analyzer on NVIDIA Jetson Orin Nano

This guide outlines how to deploy the AI Resume Analyzer on an NVIDIA Jetson Orin Nano, optimizing for its unified memory architecture (4GB/8GB RAM).

## Prerequisites
1. **JetPack SDK**: Ensure JetPack 5.x or 6.x is installed.
2. **NVIDIA Container Toolkit**: Required to pass GPU access to Docker containers.
   ```bash
   sudo apt-get install -y nvidia-container-toolkit
   sudo nvidia-ctk runtime configure --runtime=docker
   sudo systemctl restart docker
   ```
3. **Docker & Docker Compose**: Should be installed and running.

## RAM Optimization Strategies implemented

The application includes specific optimizations for the Jetson Orin Nano:
1. **Lazy Model Loading**: The `OLLAMA_KEEP_ALIVE=0` environment variable is used. This tells Ollama to instantly unload the LLM from memory after the inference request is completed. Since the Jetson uses unified memory, this prevents the model from hogging system RAM while waiting for the next request.
2. **Parsed Resume Caching**: When parsing a resume, the application first checks the local SQLite database. If it's already parsed, it bypasses the heavy processing.
3. **Connection Pooling**: The backend uses a global asynchronous HTTP client to keep a persistent connection pool, speeding up subsequent requests without recreating TLS handshakes.

## Deployment Instructions

To start the full stack (Frontend, Backend, and Ollama) optimized for Jetson:

```bash
docker-compose -f docker-compose.jetson.yml up -d --build
```

### Pulling a Quantized Model
For Jetson Orin Nano (especially the 4GB version), it's highly recommended to use quantized models to fit within the memory limits. We recommend using `llama3.2:1b`.

1. Access the Ollama container shell:
   ```bash
   docker exec -it <project_name>_ollama_1 bash
   ```
2. Pull the model:
   ```bash
   ollama pull llama3.2:1b
   ```

### Monitoring Memory Usage
You can monitor RAM and GPU usage natively on Jetson using:
```bash
tegrastats
```
Pay close attention to the `RAM` metric when a resume is being analyzed. You should see RAM spike during generation and immediately drop once it finishes.
