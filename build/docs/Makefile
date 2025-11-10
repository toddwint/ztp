# This is a Makefile

make_dir := .
project_dir := ../..

md_dir := ./markdown
output_dir := ./output

md_files := $(sort $(wildcard ${md_dir}/*.md))
output_files := $(wildcard ${output_dir}/*)

html_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.html,${md_files})
docx_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.docx,${md_files})
epub_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.epub,${md_files})
pdf_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.pdf,${md_files})
tex_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.tex,${md_files})
rtf_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.rtf,${md_files})
typ_files := $(patsubst ${md_dir}/%.md,${output_dir}/%.typ,${md_files})

.PHONY: all
all: check_requirements html pdf
	
.PHONY: test
test: $(md_files)
	@$(foreach f,${^},echo "prerequisite: $(f), target: $@";)

.PHONY: echo_all
echo_all:
	@echo "make_dir: $(make_dir)"
	@echo "project_dir: $(project_dir)"
	@echo "md_dir: $(md_dir)"
	@echo "output_dir: $(output_dir)"
	@echo "md_files: $(md_files)"
	@echo "html_files: $(html_files)"
	@echo "docx_files: $(docx_files)"
	@echo "epub_files: $(epub_files)"
	@echo "pdf_files: $(pdf_files)"
	@echo "tex_files: $(tex_files)"
	@echo "rtf_files: $(rtf_files)"
	@echo "typ_files: $(typ_files)"
	@echo "output_files: $(output_files)"

.PHONY: check_requirements
check_requirements:
	@command -v pandoc
	@command -v envsubst

define merge-markdown
-@rm --verbose --force ${@}
sed -Ei 's/^(date: ).*/\1'$$(date -Id)'/' ${<}
sed --separate '$$s/$$/\n\n/' ${^} > ${@}.tmp
envsubst '$$script $$module' < ${@}.tmp > ${@}
-@rm --force --verbose ${@}.tmp
endef

ext = $(subst .,,$(suffix $(1)))

define run-pandoc
pandoc --data-dir "${make_dir}" --defaults "$(call ext,${@})" "${^}" -o "${@}"
endef

.PHONY: html
html: $(html_files)

$(html_files) : ${output_dir}/%.html : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: pdf
pdf: $(pdf_files)

$(pdf_files) : ${output_dir}/%.pdf : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: tex
tex: $(tex_files)

$(tex_files) : ${output_dir}/%.tex : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: docx
docx: $(docx_files)

$(docx_files) : ${output_dir}/%.docx : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: rtf
rtf: $(rtf_files)

$(rtf_files) : ${output_dir}/%.rtf : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: epub
epub: $(epub_files)

$(epub_files) : ${output_dir}/%.epub : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: typ
typ: $(typ_files)

$(typ_files) : ${output_dir}/%.typ : ${md_dir}/%.md
	$(run-pandoc)

.PHONY: touch
touch: 
	touch $(md_files)

.PHONY: clean
clean: 
	-@rm --verbose $(output_files)

.PHONY: copy
copy:
	-@cp --verbose $(output_files) "${project_dir}"
	-@cp --verbose $(md_files) "${project_dir}"
	sed -Ei 's#(figures/)#build/docs/\1#' "${project_dir}/README.md"

.PHONY: move
move:
	-@mv --verbose $(output_files) "${project_dir}"
	-@cp --verbose $(md_files) "${project_dir}"
	sed -Ei 's#(figures/)#build/docs/\1#' "${project_dir}/README.md"
