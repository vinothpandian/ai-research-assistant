run_all_services: run_all_services_in_docker run_summarizer_service run_embedding_service run_question_answering_service

run_summarizer_service:
	poetry run -- uvicorn ai.summarizer:app --workers 1 --port 9000

run_embedding_service:
	poetry run -- uvicorn ai.embedding:app --workers 1 --port 9001

run_question_answering_service:
	poetry run -- uvicorn ai.question_answering:app --workers 1 --port 9002

install_all_dependencies:
	poetry install --with core,dev,app,ai,api,core-api,workers

run_all_services_in_docker:
	docker-compose up --build -d