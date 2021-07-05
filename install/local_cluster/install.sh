
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

PATH_LIB=$DIR/../../lib

export PATH=$PATH_LIB/soft/bin/:$PATH
export LD_LIBRARY_PATH=$PATH_LIB/soft/lib/:$PATH_LIB/soft/lib64/:/usr/lib64/:/usr/lib:$LD_LIBRARY_PATH

mkdir $PATH_LIB
cd $PATH_LIB

wget http://www.mpich.org/static/downloads/3.4.2/mpich-3.4.2.tar.gz
tar -xf mpich-3.4.2.tar.gz
cd mpich-3.4.2
./configure --prefix=$PATH_LIB/soft/ --with-device=ch4:ofi
make 
make install
cd ..
rm -rdf mpich-3.4.2 mpich-3.4.2.tar.gz

wget https://gcc.gnu.org/pub/libffi/libffi-3.2.tar.gz
tar -xf libffi-3.2.tar.gz
cd libffi-3.2
./configure --prefix=$PATH_LIB/soft/
make
make install
cd ..
rm -rd libffi-3.2 libffi-3.2.tar.gz

export CFLAGS="-I/home/lionel.kusch/TVB-NEST/lib//soft/lib/libffi-3.2/include/ -L/home/lionel.kusch/TVB-NEST/lib/soft/lib64/ -lffi"

wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz
tar -xf Python-3.8.10.tar.xz
cd Python-3.8.10
./configure --enable-optimizations --enable-shared --prefix=$PATH_LIB/soft
make
make altinstall
cd ..
rm -rdf  Python-3.8.10.tar.xz Python-3.8.10

export CFLAGS=""

pip3.8 install virtualenv
virtualenv -p python3.8 --system-site-packages lib_py
source lib_py/bin/activate
pip install --upgrade pip==21.1.2
pip install nose==1.3.7
pip install numpy==1.20.3 cython==0.29.23 Pillow==8.2.0
pip install mpi4py==3.0.3
pip install scipy==1.6.3
pip install elephant==0.10.0
# for plotting function
pip install matplotlib==3.4.2
pip install networkx==2.5.1
pip install h5py==3.2.1
pip install cycler==0.10.0
pip install jupyter==1.0.0
pip install vtk==9.0.1
pip install plotly==5.1.0

git clone https://github.com/NeuralEnsemble/parameters
cd parameters
git checkout b95bac2bd17f03ce600541e435e270a1e1c5a478
python3 setup.py install
cd .. 
rm -rdf parameters

wget http://ftp.gnu.org/gnu/bison/bison-3.7.tar.gz
tar -xf bison-3.7.tar.gz
cd  bison-3.7
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rd bison-3.7 bison-3.7.tar.gz

wget http://mirror.ibcp.fr/pub/gnu/help2man/help2man-1.48.3.tar.xz
tar -xf help2man-1.48.3.tar.xz
cd help2man-1.48.3
./configure --prefix=$PATH_LIB/soft
make 
make install
cd ..
rm -rfd help2man-1.48.3 help2man-1.48.3.tar.xz

wget https://invisible-island.net/datafiles/release/ncurses.tar.gz
tar -xf ncurses.tar.gz
cd ncurses-6.2
./configure --prefix=$PATH_LIB/soft --with-shared
make 
make install
cd ..
rm -rd ncurses-6.2 ncurses.tar.gz
cd soft/include
ln -s ncurses/curses.h curses.h
ln -s ncurses/term.h term.h
cd ../../

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/soft/include/ncurses:/home/lionel.kusch/TVB-NEST/lib/soft/include/

wget https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.16.tar.gz
tar -xf libiconv-1.16.tar.gz
cd libiconv-1.16
./configure --prefix=$PATH_LIB/soft
make 
make install
cd ..
rm -rd libiconv-1.16 libiconv-1.16.tar.gz

export LDFLAGS="-I$PATH_LIB/soft/include/ -L$PATH_LIB/soft/lib"
wget http://ftp.gnu.org/gnu/texinfo/texinfo-6.7.tar.gz
tar -xf texinfo-6.7.tar.gz
cd texinfo-6.7
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rd texinfo-6.7.tar.gz texinfo-6.7

wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.71.tar.gz
tar -xf autoconf-2.71.tar.gz
cd autoconf-2.71
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rfd autoconf-2.71 autoconf-2.71.tar.gz

wget https://ftp.gnu.org/gnu/automake/automake-1.16.3.tar.gz
tar -xf automake-1.16.3.tar.gz
cd automake-1.16.3
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rfd automake-1.16.3 automake-1.16.3.tar.gz

wget https://github.com/westes/flex/releases/download/flex-2.5.39/flex-2.5.39.tar.gz
tar -xf flex-2.5.39.tar.gz
cd flex-2.5.39
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rd flex-2.5.39 flex-2.5.39.tar.gz


git clone https://github.com/neuronsimulator/nrn.git
cd nrn
git checkout 8.0.0
mkdir build
cd build
cmake .. \
-DNRN_ENABLE_INTERVIEWS=OFF \
-DNRN_ENABLE_MPI=OFF \
-DNRN_ENABLE_RX3D=OFF \
-DPYTHON_EXECUTABLE=$PATH_LIB/lib_py/bin/python3.8 \
-DCURSES_LIBRARY=/usr/lib64/libncurses.so.6 -DCURSES_INCLUDE_PATH=/usr/include \
-DCMAKE_INSTALL_PREFIX=$PATH_LIB/soft
make 
make install
cd ../../
rm -rdf nrn
export PYTHONPATH=$PYTHONPATH:$PATH_LIB/soft/lib64/python/

pip install lfpykit==0.3
pip install MEAutility==1.4.9
pip install LFPy==2.2.1

git clone --branch nest-3-lio https://github.com/lionelkusch/hybridLFPy.git
cd hybridLFPy
python3 setup.py install
cd .. 
rm -rfd hybridLFPy

pip install tvb-data==2.0 tvb-gdist==2.1.0 tvb-library==2.0.10

wget https://github.com/Kitware/CMake/releases/download/v3.20.2/cmake-3.20.2.tar.gz
tar -xf cmake-3.20.2.tar.gz
cd cmake-3.20.2
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rd cmake-3.20.2 cmake-3.20.2.tar.gz

wget https://mirror.ibcp.fr/pub/gnu/gsl/gsl-2.6.tar.gz
tar -xf gsl-2.6.tar.gz
cd gsl-2.6
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rfd gsl-2.6 gsl-2.6.tar.gz
export LD_RUN_PATH=$LD_RUN_PATH:/home/lionel.kusch/TVB-NEST/lib/soft/lib

wget https://boostorg.jfrog.io/artifactory/main/release/1.76.0/source/boost_1_76_0.tar.gz
tar -xf boost_1_76_0.tar.gz
cd boost_1_76_0
./bootstrap.sh --prefix=$PATH_LIB/soft
./b2 --prefix=$PATH_LIB/soft
./b2 headers
./b2 stage threading=multi link=shared
./b2 install threading=multi link=shared
cd ..
rm -rd boost_1_76_0.tar.gz boost_1_76_0

wget https://doxygen.nl/files/doxygen-1.9.1.src.tar.gz
tar -xf doxygen-1.9.1.src.tar.gz
cd doxygen-1.9.1
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX:PATH=$PATH_LIB/soft
make
make install
cd ../../
rm -rd doxygen-1.9.1 doxygen-1.9.1.src.tar.gz

wget https://ftpmirror.gnu.org/libtool/libtool-2.4.6.tar.gz
tar -xf libtool-2.4.6.tar.gz
cd libtool-2.4.6
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rfd libtool-2.4.6.tar.gz libtool-2.4.6

wget ftp://ftp.cwru.edu/pub/bash/readline-8.1.tar.gz
tar -xf readline-8.1.tar.gz
cd readline-8.1
./configure --prefix=$PATH_LIB/soft
make
make install
cd ..
rm -rfd readline-8.1.tar.gz readline-8.1


NAME_SOURCE_NEST=$PATH_LIB/../../nest-io-dev
PATH_INSTALATION=$PATH_LIB/soft
PATH_BUILD=$PATH_LIB/nest_build
export PATH_INSTALATION
export PATH_BUILD
export NAME_SOURCE_NEST
export NEST_DATA_PATH=$PATH_BUILD/pynest
export PYTHONPATH=$PATH_INSTALATION/lib64/python3.8/site-packages:$PYTHONPATH
mkdir $PATH_BUILD
cd $PATH_BUILD
/home/lionel.kusch/TVB-NEST/lib/soft/bin/cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=ON -Dwith-ltdl=ON -Dwith-python=ON -Dcythonize-pynest=ON 
make
make install
cd ..
rm -rd $PATH_BUILD

cd $PATH_LIB/../../example/analyse/LFPY/
nrnivmodl

cd $DIR
echo -e "source $PATH_LIB/lib_py/bin/activate\nexport PATH=$PATH\nexport PYTHONPATH=$PYTHONPATH:$PATH_LIB/../..\nexport LD_LIBRARY_PATH=$LD_LIBRARY_PATH" > init_run.sh

