# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

.PHONY: all clean docker

all: clean build

clean:
	rm -rf app

build:
	mkdir -p app
	electron-packager . Viewer --platform=darwin,linux,win32 --arch=x64 --version=1.4.14 --overwrite --out=app --ignore=app

compress:
	cd app && rm -f *.zip && \
	zip -9 -r Viewer-darwin-x64.zip Viewer-darwin-x64 && \
	zip -9 -r Viewer-linux-x64.zip Viewer-linux-x64 && \
	zip -9 -r Viewer-win32-x64.zip Viewer-win32-x64

deploy:
	aws s3 cp app/Viewer-darwin-x64.zip s3://sfbasoft/app/
	aws s3 cp app/Viewer-linux-x64.zip s3://sfbasoft/app/
	aws s3 cp app/Viewer-win32-x64.zip s3://sfbasoft/app/

docker:
	docker build -t dongjoon/testcluster docker
