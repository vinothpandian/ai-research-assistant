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