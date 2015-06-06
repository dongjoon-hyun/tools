#/bin/bash

if [ $# -eq 0 ]; then
        echo 'Command is missing.'
        exit
fi
for i in {95..97} {101..130}
do
        echo 50.1.100.$i
        ssh -i ~/.ssh/GPU.pem -o LogLevel=Error -t root@50.1.100.$i $@ 2> /dev/null
done
