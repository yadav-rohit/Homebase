#!/bin/bash
# run.sh


detect_system() {
   # Detect OS
   if [[ "$(uname)" == "Darwin" ]]; then
       # Detect Apple Silicon
       if [[ "$(uname -m)" == "arm64" ]]; then
           echo "apple"
       else
           echo "cpu"
       fi
   else
       # Check for NVIDIA GPU
       if command -v nvidia-smi &> /dev/null; then
           echo "nvidia"
       # Check for AMD GPU
       elif command -v rocm-smi &> /dev/null; then
           echo "amd"
       else
           echo "cpu"
       fi
   fi
}


# Detect system type
SYSTEM_TYPE=$(detect_system)


# Set appropriate profile
case $SYSTEM_TYPE in
   "apple")
       echo "Detected Apple Silicon - using Metal acceleration"
       docker-compose --profile apple up -d
       ;;
   "nvidia")
       echo "Detected NVIDIA GPU - using CUDA acceleration"
       docker-compose --profile nvidia up
       ;;
   "amd")
       echo "Detected AMD GPU - using ROCm acceleration"
       docker-compose --profile amd up
       ;;
   *)
       echo "No GPU detected - using CPU only"
       docker-compose --profile cpu up
       ;;
esac
