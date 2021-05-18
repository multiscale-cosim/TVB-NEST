
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

mkdir ../../lib
cd ../../lib
pip3 install virtualenv
virtualenv -p python3 --system-site-packages tvb_nest_lib
source tvb_nest_lib/bin/activate
pip install --upgrade pip
pip install nose
pip install numpy cython Pillow
pip install matplotlib
pip install scipy 
pip install elephant

export PATH=$PATH:/soft/openmpi/bin/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/soft/openmpi/include
pip install mpi4py

git clone https://github.com/NeuralEnsemble/parameters
cd parameters
python3 setup.py install
cd .. 
rm -rdf parameters

wget http://ftp.gnu.org/gnu/bison/bison-3.7.tar.gz
tar -xf bison-3.7.tar.gz
cd  bison-3.7
mkdir /home/lionel.kusch/TVB-NEST/lib/bison
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/bison
make
make install
cd ..
rm -rd bison-3.7 bison-3.7.tar.gz

export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/bison/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/bison/include

wget http://mirror.ibcp.fr/pub/gnu/help2man/help2man-1.48.3.tar.xz
tar -xf help2man-1.48.3.tar.xz
cd help2man-1.48.3
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/help2man
make 
make install
cd ..
rm -rfd help2man-1.48.3 help2man-1.48.3.tar.xz

export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/help2man/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/help2man/include

wget https://invisible-island.net/datafiles/release/ncurses.tar.gz
tar -xf ncurses.tar.gz
cd ncurses-6.2
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/ncurses
make 
make install
cd ..
rm -rd ncurses-6.2 ncurses.tar.gz
cd /home/lionel.kusch/TVB-NEST/lib/ncurses/include
ln -s ncurses/curses.h curses.h
ln -s ncurses/term.h term.h


export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/ncurses/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/ncurses/include/ncurses
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/ncurses/include/

#wget https://invisible-island.net/datafiles/release/tack.tar.gz
#tar -xf tack.tar.gz
#cd tack-1.09
#./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/tack --with-curses-dir=/home/lionel.kusch/TVB-NEST/lib/ncurses/
#make
#make install
#cd ..
#rm -rfd tack-1.09 tack.tar.gz
#export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/task/bin

wget https://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.16.tar.gz
tar -xf libiconv-1.16.tar.gz
cd libiconv-1.16
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/iconv
make 
make install
cd ..
rm -rd libiconv-1.16 libiconv-1.16.tar.gz
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/iconv/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/iconv/lib


export LDFLAGS='-I/home/lionel.kusch/TVB-NEST/lib/ncurses/include/ -L/home/lionel.kusch/TVB-NEST/lib/ncurses/lib'
export LDFLAGS=$LDFLAGS' -I/home/lionel.kusch/TVB-NEST/lib/iconv/include -L/home/lionel.kusch/TVB-NEST/lib/iconv/lib'
wget http://ftp.gnu.org/gnu/texinfo/texinfo-6.7.tar.gz
tar -xf texinfo-6.7.tar.gz
cd texinfo-6.7
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/texinfo
make
make install
cd ..
rm -rd texinfo-6.7.tar.gz texinfo-6.7
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/texinfo/bin

wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.71.tar.gz
tar -xf autoconf-2.71.tar.gz
cd autoconf-2.71
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/autoconf
make
make install
cd ..
rm -rfd autoconf-2.71 autoconf-2.71.tar.gz
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/autoconf/bin

wget https://ftp.gnu.org/gnu/automake/automake-1.16.3.tar.gz
tar -xf automake-1.16.3.tar.gz
cd automake-1.16.3
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/automake
make
make install
cd ..
rm -rfd automake-1.16.3 automake-1.16.3.tar.gz
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/automake/bin

wget https://github.com/westes/flex/releases/download/flex-2.5.39/flex-2.5.39.tar.gz
tar -xf flex-2.5.39.tar.gz
cd flex-2.5.39
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/flex
make
make install
cd ..
rm -rd flex-2.5.39 flex-2.5.39.tar.gz
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/flex/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/flex/lib


git clone https://github.com/neuronsimulator/nrn.git
cd nrn
mkdir build
cd build
cmake .. \
-DNRN_ENABLE_INTERVIEWS=OFF \
-DNRN_ENABLE_MPI=OFF \
-DNRN_ENABLE_RX3D=OFF \
-DCURSES_LIBRARY=/usr/lib64/libncurses.so.6 -DCURSES_INCLUDE_PATH=/usr/include \
-DCMAKE_INSTALL_PREFIX=/home/lionel.kusch/TVB-NEST/lib/neuron
make 
make install
rm -rdf nrn
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/neuron/bin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/neuron/lib
export PYTHONPATH=$PYTHONPATH:/home/lionel.kusch/TVB-NEST/lib/neuron/lib64/python/


ln -s /usr/lib64/libncurses.so.6 /home/lionel.kusch/TVB-NEST/lib/ncurses/lib/libncurses.so.so
pip install LFPy
pip install lfpykit
pip install MEAutility
pip install LFPy


git clone --branch nest-3-lio https://github.com/lionelkusch/hybridLFPy.git
cd hybridLFPy
python3 setup.py install
cd .. 
rm -rfd hybridLFPy

pip install tvb-data tvb-gdist tvb-library==2.0.10

wget https://github.com/Kitware/CMake/releases/download/v3.20.2/cmake-3.20.2.tar.gz
tar -xf cmake-3.20.2.tar.gz
cd cmake-3.20.2
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/cmake
make
make install
cd ..
rm -rd cmake-3.20.2 cmake-3.20.2.tar.gz
export PATH=/home/lionel.kusch/TVB-NEST/lib/cmake/bin:$PATH

wget https://mirror.ibcp.fr/pub/gnu/gsl/gsl-2.6.tar.gz
tar -xf gsl-2.6.tar.gz
cd gsl-2.6
./configure --prefix=/home/lionel.kusch/TVB-NEST/lib/gsl
make
make install
cd ..
rm -rfd gsl-2.6 gsl-2.6.tar.gz
export PATH=$PATH:/home/lionel.kusch/TVB-NEST/lib/gsl/bin/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/lionel.kusch/TVB-NEST/lib/gsl/lib
export LD_RUN_PATH=$LD_RUN_PATH:/home/lionel.kusch/TVB-NEST/lib/gsl/lib


NAME_SOURCE_NEST=/home/lionel.kusch/TVB-NEST/nest-io-dev
PATH_INSTALATION=/home/lionel.kusch/TVB-NEST/lib/nest
PATH_BUILD=/home/lionel.kusch/TVB-NEST/lib/nest_build
export PATH_INSTALATION
export PATH_BUILD
export NAME_SOURCE_NEST
export NEST_DATA_PATH=$PATH_BUILD/pynest
export PYTHONPATH=$PATH_INSTALATION/lib64/python3.6/site-packages:$PYTHONPATH
export PATH=$PATH:$PATH_INSTALATION/bin
mkdir $PATH_BUILD
cd $PATH_BUILD
cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=On -Dwith-ltdl=ON -Dwith-python=ON -Dcythonize-pynest=ON 
make
make install

cd /home/lionel.kusch/TVB-NEST/example/analyse/LFPY/
nrnivmodl

cd $DIR
echo -e "source /home/lionel.kusch/TVB-NEST/lib/tvb_nest_lib/bin/activate\nexport PATH=$PATH\nexport PYTHONPATH=$PYTHONPATH:/home/lionel.kusch/TVB-NEST/" > init_run.sh

