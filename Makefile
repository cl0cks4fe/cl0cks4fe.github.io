.PHONY: build serve clean

build:
	python3 build.py

serve: build
	cd _site && python3 -m http.server 8000

new:
	@date=$$(date +%Y-%m-%d); \
	title="$${TITLE:-untitled}"; \
	slug=$$(echo "$$title" | tr ' ' '_'); \
	file="posts/$$date-$$slug.md"; \
	echo "---\ntitle: $$title\ndate: $$date\n---\n" > "$$file"; \
	echo "Created $$file"

clean:
	rm -rf _site
