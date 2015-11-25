all: clean build

clean:
	rm -rf Viewer-*-x64

build:
	electron-packager . Viewer --platform=darwin,linux --arch=x64 --version=0.35.1 --overwrite
