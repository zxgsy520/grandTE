SOFTWARE=$1


#Install mdust
cd ${SOFTWARE}
mkdir mdust
cd mdust 
wget -c https://github.com/lh3/mdust/archive/refs/heads/master.zip
unzip master.zip
mv mdust-master/ v1.0.0
cd v1.0.0
make

#Install reasonaTE
cd ${SOFTWARE}
mkdir reasonaTE
cd reasonaTE
mkdir v1.0.0
wget https://raw.githubusercontent.com/DerKevinRiehl/transposon_annotation_reasonaTE/main/environment_yml/transposon_annotation_tools_env.yml
conda env create --prefix=${SOFTWARE}/reasonaTE/v1.0.0/ -f transposon_annotation_tools_env.yml


