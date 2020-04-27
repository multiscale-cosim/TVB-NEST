FROM alpine:3.11

COPY ./nest-io-dev /home/nest-io-dev

RUN apk update;\
    apk add git file g++ gcc gfortran make gdb strace wget

# Install mpich
RUN wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz;\
    tar xf mpich-3.1.4.tar.gz;\
    cd mpich-3.1.4;\
    ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr;\
    make -j$(nproc);\
    make install

# Nest
RUN apk add cmake readline-dev ncurses-dev gsl-dev curl python3;\
    apk add python3-dev py3-numpy-dev py3-scipy cython;\
    cd /root;\
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
    python3 get-pip.py;\
    rm get-pip.py;\
    pip install --upgrade pip;\
    apk add freetype-dev;\
    pip install matplotlib;\
    pip install elephant;\
    pip install mpi4py

# install TVB
RUN apk add llvm8-dev llvm8;\
    export LLVM_CONFIG=/usr/bin/llvm8-config;\
    pip install tvb-data tvb-gdist tvb-library

RUN cd /home/;\
    NAME_SOURCE_NEST=/home/nest-io-dev;\
    PATH_INSTALATION=/usr/lib/nest/;\
    PATH_BUILD=/home/nest-build;\
    export PATH_INSTALATION;\
    export PATH_BUILD;\
    export NAME_SOURCE_NEST;\
    export NEST_DATA_PATH=$PATH_BUILD/pynest;\
    mkdir $PATH_BUILD;\
    cd $PATH_BUILD;\
    cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-python=3;\
    make -j$(nproc);\
    make install
    #make test ;\

ENV PYTHONPATH /usr/lib/nest/lib64/python3.8/site-packages/:/home/:$PYTHONPATH
