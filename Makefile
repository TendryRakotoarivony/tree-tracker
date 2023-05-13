include .env
# export $(shell sed 's/=.*//' .env)

AWS_REGION ?= us-east-1
AWS_ECR ?= ""
IMAGE_NAME ?= "tree-tracker"
CONTAINER_NAME ?= "tree-tracker"
VERSION ?= "latest"
TAG = ${IMAGE_NAME}:${VERSION}

run: ## Run streamlit app locally
	streamlit run Home.py

docker-build: ## Build docker image for local development
	docker build --build-arg AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} --build-arg AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} --build-arg AWS_DEFAULT_REGION=${AWS_REGION} -t ${TAG} .

docker-run: ## Run docker image locally
	docker run --rm --name ${CONTAINER_NAME} -p 8501:8501 -t ${TAG}

docker-deploy: ## Rebuild docker image with a new tag and push to ECR
	docker build --build-arg AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} --build-arg AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} --build-arg AWS_DEFAULT_REGION=${AWS_REGION} -t ${TAG} .
	
	aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ECR}
	
	docker tag ${TAG} ${AWS_ECR}/${TAG}
	
	docker push ${AWS_ECR}/${TAG}
	
	eb deploy
.PHONY: rebuild


help: ## Show this help
	@echo ${TAG}
	@echo "\nSpecify a command. The choices are:\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[0;36m%-12s\033[m %s\n", $$1, $$2}'
	@echo ""

.PHONY: help
