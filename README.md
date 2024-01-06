# AI Research Assistant

---

# Setup

## Requirements

* Install `poetry` version 1.4.2
* Install `python` version 3.11.4

> Tip: You can use `asdf` ([link](https://asdf-vm.com/)) to manage your python and poetry versions.

## Install dependencies

Run `poetry install` to install the dependencies. This will create a poetry virtual environment and
install the dependencies in it. You can activate the virtual environment by running `poetry shell`.

# Development

## Configuration

You can configure the application by editing the copying the `config/dev.config.yaml` to `config.yaml` in
the root directory and filling in the values.

### Huggingface

* Change the type field of summarizer, embedding, qa in `config.yaml` to `huggingface`.

### Ollama

* Install `ollama` from [here](https://ollama.ai/). Only available for Linux and Mac.
* Change the type field of summarizer, embedding, qa in `config.yaml` to `ollama`.
* Set the correct

### OpenAI

* Set the key field of openai in `config.yaml` with
  an [OpenAI API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-api-key).
* Change the type field of summarizer, embedding, qa in `config.yaml` to `openai`.

### Mixed

* You can mix and match the different types of summarizer, embedding, qa by setting the type field
  can be one of `huggingface`, `ollama`, `openai`. Make sure the embedding dimension and the distance are
  set correctly in `config.yaml`.

# Deployment

* Install `docker` version 20.10+ and run the docker daemon.
* Copy the `config/prod.config.yaml` to `config.yaml` and update the values based on the
  [configuration](#configuration) section.

### Running the AI services
* Run AI server if you're using huggingface with the following command. It'll take a while to download and run the models.
  ```shell
  make run_ray
  ```
* You can check the status of the ray cluster at `http://localhost:8265`.
* Run Ollama API service if you're using ollama with the following command:
  ```shell
  make run_ollama_service
  ```
* If you're using openai, you don't need to do anything other than setting the key in `config.yaml` and
  updating the type field to `openai`.

### Running the application

Run the application with the following command:

  ```shell
  make run_all 
  ```

It'll run the application at `http://localhost:8501`.