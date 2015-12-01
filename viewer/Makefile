all: clean build

clean:
	rm -rf app

build:
	mkdir app
	electron-packager . Viewer --platform=darwin,linux,win32 --arch=x64 --version=0.35.1 --overwrite --out=app --ignore=app

docker:
	docker build -t dongjoon/testclusters docker
