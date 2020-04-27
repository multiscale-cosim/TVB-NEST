#!/bin/bash

cp -r  ../../nest-io-dev .
sudo docker build -t local:NEST_TVB_IO_2 -f Nest_TVB_2.dockerfile .
rm -rd nest-io-dev
