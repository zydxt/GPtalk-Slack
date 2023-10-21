build: plain-pack
	(cd dist/lambda ; zip -r ../lambda.zip . -x '*.pyc')

python-build: clean
	poetry build

plain-pack: python-build
	poetry run pip install -t dist/lambda dist/*.whl

clean:
	rm -rf dist
