File='periodArgs.txt'
while IFS="," read -r TYPE PERIOD CERT
do
    ./makeCondor.sh ${TYPE} ${PERIOD} ${CERT}
done < ${File}
