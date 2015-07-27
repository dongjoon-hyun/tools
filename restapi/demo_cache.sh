#!/bin/bash 

DOMAIN="tip"

# OCR
printf '\n\nOCR..\n'
OCRIMAGES_0=(3 10 13 25 28)
OCRIMAGES_1=(2 5 14 29 31)
OCRIMAGES_2=(1 35 38 43 47)
OCRIMAGES_3=(18 30 32 44 51)
OCRIMAGES_4=(4 6 19 24 27)
OCRIMAGES_5=(8 15 23 45 52)
OCRIMAGES_6=(11 21 22 50 54)
OCRIMAGES_7=(0 17 26 34 36)
OCRIMAGES_8=(61 84 110 128 134)
OCRIMAGES_9=(7 9 12 16 20)

OCRNUM=0
for i in "${OCRIMAGES_0[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_1[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_2[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_3[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_4[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_5[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_6[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_7[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_8[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done
OCRNUM=$((OCRNUM + 1))
for i in "${OCRIMAGES_9[@]}"
do
    index="$(printf "%03d" $i)"
    curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fmnist_digits,%2Fdata%2Fimage%2Fmnist%2Fjpg%2F$OCRNUM%2F00$index.jpg,False,28:28,None,3
done

# Image Tagging
printf '\n\nImage Tagging..\n'
curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fbvlc_reference_caffenet,%2Fsample%2Fcat.jpg,True,256:256,2:1:0,3
curl http://$DOMAIN:5555/api/v1/caffe.predict/%2Fmodel%2Fcaffe%2Fbvlc_reference_caffenet,%2Fsample%2Fad.png,True,256:256,2:1:0,3

# Document Categorization
printf '\n\nDocument Categorization..\n'
curl http://$DOMAIN:5555/api/v1/news.nb_predict/%2Ftmp%2Fnews100,%22%EC%97%AC%EB%A6%84%20%EB%B3%B4%EC%96%91%EC%8B%9D%20%E2%80%9C%EC%98%AC%ED%95%B4%EB%8A%94%20%EC%9E%A5%EC%96%B4%EB%8F%84%20%EB%8C%80%EC%84%B8%E2%80%9D%2023%EC%9D%BC%20%EC%A4%91%EB%B3%B5%EC%9D%84%20%EC%95%9E%EB%91%90%EA%B3%A0%20%EC%97%AC%EB%A6%84%20%EB%B3%B4%EC%96%91%EC%8B%9D%EC%9C%BC%EB%A1%9C%20%EC%9E%A5%EC%96%B4%EC%99%80%20%EC%A0%84%EB%B3%B5%20%EB%93%B1%20%EB%8B%A4%EC%96%91%ED%95%9C%20%EC%9D%8C%EC%8B%9D%EC%9D%B4%20%EC%86%8C%EB%B9%84%EC%9E%90%EB%93%A4%EC%9D%84%20%EC%82%AC%EB%A1%9C%EC%9E%A1%EA%B3%A0%20%EC%9E%88%EB%8A%94%20%EA%B2%83%EC%9C%BC%EB%A1%9C%20%EB%82%98%ED%83%80%EB%82%AC%EB%8B%A4%20%20%EC%97%AC%EB%A6%84%20%EB%B3%B4%EC%96%91%EC%8B%9D%EC%9D%98%20%E2%80%98%EB%8C%80%EC%84%B8%E2%80%99%EC%9D%B8%20%EC%82%BC%EA%B3%84%ED%83%95%EC%9D%80%201%202%EC%9D%B8%20%EA%B0%80%EA%B5%AC%EA%B0%80%20%EB%8A%98%EB%A9%B4%EC%84%9C%20%EB%B0%98%20%EB%A7%88%EB%A6%AC%20%EC%83%81%ED%92%88%20%ED%8C%90%EB%A7%A4%EA%B0%80%20%EC%A6%9D%EA%B0%80%ED%95%98%EA%B3%A0%20%EC%9E%88%EB%8B%A4%20%20%EC%98%A8%EB%9D%BC%EC%9D%B8%20%EC%87%BC%ED%95%91%EC%82%AC%EC%9D%B4%ED%8A%B8%2011%EB%B2%88%EA%B0%80%20%EC%9E%90%EB%A3%8C%EB%A5%BC%20%EB%B3%B4%EB%A9%B4%20%EC%B4%88%EB%B3%B5%2013%EC%9D%BC%20%EC%9D%B4%20%EC%9E%88%EC%97%88%EB%8D%98%20%EC%A7%80%EB%82%9C%201%EC%9D%BC%EB%B6%80%ED%84%B0%2020%EC%9D%BC%EA%B9%8C%EC%A7%80%20%EC%A0%84%EB%B3%B5%EA%B3%BC%20%EC%9E%A5%EC%96%B4%20%EB%A7%A4%EC%B6%9C%EC%9D%B4%20%EC%A7%80%EB%82%9C%ED%95%B4%20%EA%B0%99%EC%9D%80%20%EA%B8%B0%EA%B0%84%EB%B3%B4%EB%8B%A4%20%EA%B0%81%EA%B0%81%20402%20%20%20232%20%20%EB%8A%98%EC%96%B4%EB%82%9C%20%EA%B2%83%EC%9C%BC%EB%A1%9C%20%EC%A7%91%EA%B3%84%EB%90%90%EB%8B%A4%20%22
curl http://$DOMAIN:5555/api/v1/news.nb_predict/%2Ftmp%2Fnews100,%22%EB%8B%B4%EB%B3%B4%20%EC%B6%A9%EB%B6%84%ED%95%B4%EB%8F%84%20%EC%9B%90%EA%B8%88%EA%B0%9A%EC%9D%84%20%EB%8A%A5%EB%A0%A5%20%EB%94%B0%EC%A0%B8%20%EB%8C%80%EC%B6%9C%EC%95%A1%20%EC%A1%B0%EC%A0%95%20%EC%A0%95%EB%B6%80%EA%B0%80%2022%EC%9D%BC%20%EB%82%B4%EB%86%93%EC%9D%80%20%E2%80%98%EA%B0%80%EA%B3%84%EB%B6%80%EC%B1%84%20%EC%A2%85%ED%95%A9%EA%B4%80%EB%A6%AC%EB%B0%A9%EC%95%88%E2%80%99%EC%9D%80%20%EB%8C%80%EC%B6%9C%EC%9E%90%EC%9D%98%20%EB%B9%9A%20%EA%B0%9A%EC%9D%84%20%EB%8A%A5%EB%A0%A5%EC%9D%84%20%EA%BC%BC%EA%BC%BC%ED%9E%88%20%EB%94%B0%EC%A7%80%EA%B3%A0%20%20%EB%8C%80%EC%B6%9C%EB%B0%9B%EC%9D%80%20%EC%8B%9C%EC%A0%90%EB%B6%80%ED%84%B0%20%EC%9B%90%EA%B8%88%EC%9D%84%20%EB%82%98%EB%88%A0%20%EA%B0%9A%EB%8F%84%EB%A1%9D%20%ED%95%B4%20%EA%B0%80%EA%B3%84%EB%B6%80%EC%B1%84%EB%A5%BC%20%EC%95%88%EC%A0%95%EC%A0%81%EC%9C%BC%EB%A1%9C%20%EA%B4%80%EB%A6%AC%ED%95%98%EA%B2%A0%EB%8B%A4%EB%8A%94%20%EA%B2%8C%20%ED%95%B5%EC%8B%AC%20%EB%82%B4%EC%9A%A9%EC%9D%B4%EB%8B%A4%20%20%EC%A0%80%EA%B8%88%EB%A6%AC%EB%82%98%20%EC%A3%BC%ED%83%9D%EB%8B%B4%EB%B3%B4%EC%9D%B8%EC%A0%95%EB%B9%84%EC%9C%A8%20LTV%20%C2%B7%EC%B4%9D%EB%B6%80%EC%B1%84%EC%83%81%ED%99%98%EB%B9%84%EC%9C%A8%20DTI%20%20%EA%B7%9C%EC%A0%9C%20%EC%99%84%ED%99%94%20%EB%93%B1%20%EA%B0%80%EA%B3%84%EB%B6%80%EC%B1%84%EB%A5%BC%20%EB%8A%98%EB%A6%B0%20%EC%9B%90%EC%9D%B8%EC%9D%84%20%EC%A7%81%EC%A0%91%20%EC%86%90%EB%B3%B4%EC%A7%80%EB%8A%94%20%EC%95%8A%EA%B3%A0%20%20%EC%9D%80%ED%96%89%EC%9D%B4%20%EB%8C%80%EC%B6%9C%20%EA%B4%80%ED%96%89%EC%9D%84%20%EA%B0%9C%EC%84%A0%ED%95%98%EB%8A%94%20%EA%B0%84%EC%A0%91%EC%A0%81%EC%9D%B8%20%EB%B0%A9%EC%8B%9D%EC%9D%84%20%ED%86%B5%ED%95%B4%20%EB%8C%80%EC%B6%9C%20%EA%B7%9C%EB%AA%A8%EB%A5%BC%20%EC%A4%84%EC%9D%B4%EA%B3%A0%20%EA%B0%80%EA%B3%84%EB%B6%80%EC%B1%84%EC%9D%98%20%EC%B7%A8%EC%95%BD%EA%B3%A0%EB%A6%AC%EB%A5%BC%20%EC%A0%9C%EA%B1%B0%ED%95%B4%20%EB%82%98%EA%B0%80%EA%B2%A0%EB%8B%A4%EB%8A%94%20%EA%B2%83%EC%9D%B4%EB%8B%A4%20%22
