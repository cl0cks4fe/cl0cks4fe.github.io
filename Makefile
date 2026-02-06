.PHONY: build serve clean

build:
	python3 build.py

serve: build
	cd _site && python3 -m http.server 8000

clean:
	rm -rf _site
