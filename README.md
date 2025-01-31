Homebase
Homebase is a testing application designed to locally test and run large language models (LLMs) in separate Docker containers using Ollama. This setup allows for efficient management and execution of different models without cluttering your main environment.

How to Use Homebase
Step 1: Create a Docker Container
Navigate to the Repository Directory: Open your terminal and change to the directory where you cloned the repository:

```bash
cd {directory where you have cloned the repo}
```
Make the Script Executable: Grant execute permissions to the run.sh script:

```bash
chmod +x ./run.sh
```

Run the Script: Execute the run.sh script. It will automatically detect your system type and set up the Docker container accordingly.

Note: For the current version, you may need to update the device type in the docker-compose file.
Example configuration in the docker-compose.yml:

```yaml
streamlit:
  build: .
  ports:
    - "8501:8501"
  environment:
    OLLAMA_HOST: "http://ollama-nvidia:11434" # Adjust this to point to the appropriate service name
  restart: unless-stopped
  depends_on:
    - ollama-nvidia # or the appropriate Ollama service based on your profile
  networks:
    - ollama_network
```

Step 2: Add Models to the Application
To add a model to your application, run the following command, replacing {your-ollama-image-name} with the name of your Ollama image:

```bash
docker exec -it {your-ollama-image-name} ollama pull deepseek-r1:7b
```

Step 3: Run the Application Containers Individually
If you need to run the application containers individually after setup, use the following command:

```bash
docker run -d -p 8501:8501 --env OLLAMA_HOST="http://ollama-nvidia:11434" --restart unless-stopped --link ollama-nvidia --network chatbot_ollama_network chatbot-streamlit-think
```

Important Note
This setup works well for small models. However, for larger models, such as llama:7b or deepseek-r1:7b, you will need to ensure that your system has sufficient memory to handle them.
