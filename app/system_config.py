import platform
import os
import subprocess


class SystemConfig:
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.gpu_type = self._detect_gpu()
        self.config = self._get_optimal_config()

    def _detect_gpu(self):
        """Detect GPU type"""
        if self.system == "Darwin":  # macOS
            if "arm" in platform.processor() or "arm" in platform.processor() or "arm" in platform.processor():
                return "Apple Silicon"
        elif self.system == "Linux":
            try:
                # Check for NVIDIA GPU
                nvidia_output = subprocess.run(
                    ['nvidia-smi'], capture_output=True, text=True)
                if nvidia_output.returncode == 0:
                    return "NVIDIA"

                # Check for AMD GPU
                amd_output = subprocess.run(
                    ['rocm-smi'], capture_output=True, text=True)
                if amd_output.returncode == 0:
                    return "AMD"
            except FileNotFoundError:
                pass
        return "CPU"

    def _get_optimal_config(self):
        """Get optimal configuration based on system type"""
        base_config = {
            "num_thread": 4,
            "context_size": 4096,
            "batch_size": 8,
            "parallel_requests": 1
        }
        metal_devices = {
            "num_thread": 4,
            "context_size": 4096,
            "batch_size": 8,
            "parallel_requests": 1
        }

        # Apple Silicon (M1/M2/M3) configurations
        m_series_configs = {
            "M1": {
                "num_thread": 8,
                "context_size": 8192,
                "batch_size": 16,
                "parallel_requests": 2,
                "metal_device": "mps",
            },
            "M2": {
                "num_thread": 10,
                "context_size": 16384,
                "batch_size": 32,
                "parallel_requests": 3,
                "metal_device": "mps",
            },
            "M3": {
                "num_thread": 12,
                "context_size": 32768,
                "batch_size": 48,
                "parallel_requests": 4,
                "metal_device": "mps",
            }
        }

        # GPU configurations
        gpu_configs = {
            "NVIDIA": {
                "num_thread": 8,
                "context_size": 16384,
                "batch_size": 32,
                "parallel_requests": 4,
                "num_gpu": 99,
                "gpu_layers": "auto",
                "cuda_device": "cuda"
            },
            "AMD": {
                "num_thread": 8,
                "context_size": 8192,
                "batch_size": 16,
                "parallel_requests": 2,
                "gpu_layers": "auto",
                "rocm_device": "hip"
            }
        }

        # Detect specific configuration
        if self.system == "Darwin" and "Apple Silicon" == self.gpu_type:
            processor = platform.processor()
            if "arm" in processor:
                return {**base_config, **m_series_configs["M3"]}
            elif "M2" in processor:
                return {**base_config, **m_series_configs["M2"]}
            elif "M1" in processor:
                return {**base_config, **m_series_configs["M1"]}
        elif self.gpu_type in gpu_configs:
            return {**base_config, **gpu_configs[self.gpu_type]}

        # Default Intel/AMD CPU configuration
        return {
            **base_config,
            "num_thread": os.cpu_count() or 4,
            "context_size": 4096,
            "batch_size": 8,
            "parallel_requests": 1
        }

    def get_ollama_options(self):
        """Get Ollama-specific configuration options"""
        options = {
            "num_thread": self.config["num_thread"],
            "num_ctx": self.config["context_size"],
            "batch_size": self.config["batch_size"],
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "top_k": 40,
        }

        # Add GPU-specific options
        if self.gpu_type == "NVIDIA":
            options.update({
                "num_gpu": self.config["num_gpu"],
                "gpu_layers": self.config["gpu_layers"],
            })
        elif self.gpu_type == "AMD":
            options.update({
                "gpu_layers": self.config["gpu_layers"],
            })
        elif self.gpu_type == "Apple Silicon":
            options.update({
                "metal_device": self.config["metal_device"],
            })

        return options
