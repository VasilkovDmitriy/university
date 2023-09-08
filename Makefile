build:
	docker-compose -f docker-compose-local.yaml build

up:
	docker-compose -f docker-compose-local.yaml up -d

down:
	docker-compose -f docker-compose-local.yaml down && docker network prune --force

build-dev:
	docker build -f DevDockerfile . -t university-dev-image

up-dev:
	docker run --rm -t -d -v ${HOME}/projects/university/:/app --name university-dev-container university-dev-image

down-dev:
	docker stop university-dev-container
