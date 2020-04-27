#!/bin/bash

cp -r  ../../nest-io-dev .
sudo docker build -t local:NEST_TVB_IO -f Nest_TVB.dockerfile .
rm -rd nest-io-dev
