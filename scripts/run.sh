#!/bin/bash
# Usage: ./run.sh python sorting/quick_sort
#        ./run.sh java com.yourname.algorithms.sorting.QuickSort

LANG=$1
PROGRAM=$2

case $LANG in
    python)
        cd python
        source venv/bin/activate
        python "src/$PROGRAM.py"
        ;;
    java)
        cd java
        mvn compile exec:java -Dexec.mainClass="$PROGRAM"
        ;;
    *)
        echo "Usage: $0 {python|java} <program>"
        exit 1
        ;;
esac
