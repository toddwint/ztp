# This is a Makefile

git_id := toddwint
#repo_name := $(basename $(notdir "$(shell "pwd")"))
repo_name != basename "$${PWD}"
version := $(shell date -u +"%Y.%m.%d-%H.%M.%S")
#version := $(file < ./version)

.PHONY: all
all: check_requirements docs build

.PHONY: echo_all
echo_all:
	@echo "git_id: $(git_id)"
	@echo "repo_name: $(repo_name)"
	@echo "version: $(version)"

.PHONY: check_requirements
check_requirements:
	@command -v git
	@command -v docker

.ONESHELL:
.PHONY: docs
docs: check_requirements
	cd ./build/docs
	make
	make move

.PHONY: build
build: check_requirements
	docker rmi $(git_id)/$(repo_name)
	cd ./build
	./build.sh
	
.PHONY: multiplatform_buildx
multiplatform_buildx: check_requirements
	docker rmi $(git_id)/$(repo_name)
	cd ./build
	./multiplatform_buildx.sh

.PHONY: remove
remove: 
	-@rm ./build/docs/output/*

.PHONY: git-release-push
git-release-push:
	gh release create \
		"${version}" \
		--latest \
		--notes-file release_notes.md \
		--generate-notes \
		--title "${version}" \
