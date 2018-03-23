#!/bin/bash

echo "download caffemodel..."
dir=agent/model
if [ ! -d $dir ]; then
  mkdir $dir
fi
curl -o ${dir}/bvlc_alexnet.caffemodel http://dl.caffe.berkeleyvision.org/bvlc_alexnet.caffemodel

curl -f -L -o ${dir}/ilsvrc_2012_mean.npy https://github.com/BVLC/caffe/raw/master/python/caffe/imagenet/ilsvrc_2012_mean.npy
