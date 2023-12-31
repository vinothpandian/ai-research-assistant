run_all: run_backend run_app
	
run_backend: run_api run_ai_services

run_app:
	streamlit run app/Home.py

run_api:
	docker compose --profile app --profile api --profile db up -d

docker_api:
	docker compose --profile api --profile db $(filter-out $@,$(MAKECMDGOALS))

docker_db:
	docker compose --profile db $(filter-out $@,$(MAKECMDGOALS))

docker_ai:
	docker compose -f ai.docker-compose.yaml $(filter-out $@,$(MAKECMDGOALS))

run_ai_services: run_summarizer_service run_embedding_service run_question_answering_service run_ollama_service

run_summarizer_service:
	poetry run -- uvicorn ai.summarizer:app --workers 1 --port 9000

run_embedding_service:
	poetry run -- uvicorn ai.embedding:app --workers 1 --port 9001

run_question_answering_service:
	poetry run -- uvicorn ai.question_answering:app --workers 1 --port 9002

run_ollama_service:
	ollama serve

%:
	@: