run_all_services: run_all_services_in_docker run_summarizer_service run_embedding_service run_question_answering_service

run_summarizer_service:
	poetry run -- uvicorn ai.summarizer:app --workers 1 --port 9000

run_embedding_service:
	poetry run -- uvicorn ai.embedding:app --workers 1 --port 9001

run_question_answering_service:
	poetry run -- uvicorn ai.question_answering:app --workers 1 --port 9002

run_all_services_in_docker:
	docker-compose up --build -d

run_app:
	poetry run -- python -m streamlit run app/Home.py