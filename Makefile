run_all: run_backend run_app

dev_all: dev_api run_app
	
run_backend: run_api

run_app:
	streamlit run app/Home.py

dev_api:
	docker compose -f dev.docker-compose.yaml --profile app --profile api --profile db up --build -d

dev_docker:
	docker compose -f dev.docker-compose.yaml --profile api --profile db $(filter-out $@,$(MAKECMDGOALS))

run_api:
	docker compose --profile app --profile api --profile db up --build -d

docker_api:
	docker compose --profile api --profile db $(filter-out $@,$(MAKECMDGOALS))

docker_db:
	docker compose --profile db $(filter-out $@,$(MAKECMDGOALS))

run_ai_services: run_ray run_ollama_service

run_ray:
	serve run ai/ray.yaml

run_ollama_service:
	ollama serve

ruff:
	ruff check --fix .

%:
	@: