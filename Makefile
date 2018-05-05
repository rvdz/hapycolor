all: run

run: build
	docker run --name hapy hapycolor

build:
	docker build -t hapycolor .

stop:
	docker rm -f hapy
