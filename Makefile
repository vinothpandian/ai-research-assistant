run_all: run_backend run_app
	
run_backend: start_api run_ai_services

start_api:
	docker compose --profile api --profile db --profile worker up -d

stop_api:
	docker compose --profile api --profile db --profile worker down

purge_api:
	docker compose --profile api --profile db --profile worker down -v

run_app:
	poetry run -- python -m streamlit run app/Home.py

start_db:
	docker compose --profile db up -d

stop_db:
	docker compose --profile db down

purge_db:
	docker compose --profile db down --volumes

start_worker:
	docker compose --profile worker --profile db up -d

stop_worker:
	docker compose --profile worker --profile db down

start_ai:
	docker compose --profile ai up -d

stop_ai:
	docker compose --profile ai down

start_ollama:
	docker compose --profile ollama up -d

stop_ollama:
	docker compose --profile ollama down

purge_ollama:
	docker compose --profile ollama down --volumes

run_ai_services: run_summarizer_service run_embedding_service run_question_answering_service run_ollama_service

run_summarizer_service:
	poetry run -- uvicorn ai.summarizer:app --workers 1 --port 9000

run_embedding_service:
	poetry run -- uvicorn ai.embedding:app --workers 1 --port 9001

run_question_answering_service:
	poetry run -- uvicorn ai.question_answering:app --workers 1 --port 9002

run_ollama_service:
	ollama serve