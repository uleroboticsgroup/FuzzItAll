# Load WLP context variables
source $1/conf.conf
source ./HS.conf
echo "DEBUG: $0 $1"

# Local script variables
_JOB=`echo $1 | sed -r 's/\/+/_/g'`

# Set master fuzzer Name
if [ -f "$FUZZ_NAME_PATH/$_JOB.name" ]; then
   # Recover previous name 
    _fuzzerName="$(cat $FUZZ_NAME_PATH/$_JOB.name)"  
fi

# Obtaine previos master fuzzer state
_JB_MF_ID="$(cat $FUZZ_NAME_PATH/$_JOB.name | cut -c3-)"
_JB_MF_STATE="$(squeue --noheader | grep $_JB_MF_ID)"

if [ -z "$_JB_MF_STATE" ]; then 
  _MF_IS_ALIVE=0
  rm $_JOB.name -rf
else
 _MF_IS_ALIVE=1
fi

#echo "DEBUG: _JB_MF_ID=$_JB_MF_ID"
#echo "DEBUG: _JOB=$_JOB"
#echo "DEBUG: _JB_MF_STATE=$_JB_MF_STATE"
#echo "DEBUG: _MF_IS_ALIVE=$_MF_IS_ALIVE"
#echo "DEBUG: _fuzzerName=$_fuzzerName"

if (($_MF_IS_ALIVE)); then
    echo "ERROR: A master fuzzer $_fuzzerName was detected."
else
    if [ -n "$_fuzzerName" ]; then 
      _oldFuzzerName=$_fuzzerName
    fi

    # Use a new  fuzzerName
    _fuzzerName="MF${_JOB}"
    echo ${_fuzzerName} > $FUZZ_NAME_PATH/$_JOB.name

    echo "DEBUG: _fuzzerName=$_fuzzerName _oldFuzzerName=$_oldFuzzerName"

    # Get basedir
    _PWD=$(pwd)

    if [ -d "$_JOB-out" ]; then
      # TODO: Comprobar bug sinconizacion de directorios AFL++ vs scayle: PROGRAM ABORT : Resume attempted but old output directory not found
      echo "DEBUG: Recover task $_JOB-out" 
     # Recover task 
      env AFL_PATH="$TLB_AFL_PATH_FUZZ" AFL_NO_AFFINITY=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 ${TLB_AFL_PATH_FUZZ}/afl-fuzz -i - -o $1/fuzz_out -M $_fuzzerName $1/$run
    else
      echo "DEBUG: New task $_JOB-out" 
      # New task
      env AFL_PATH="$TLB_AFL_PATH_FUZZ" AFL_NO_AFFINITY=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 ${TLB_AFL_PATH_FUZZ}/afl-fuzz -i $1/$corpus_path -o $1/fuzz_out -M  $_fuzzerName $1/$run

    fi

  # TODO: Comprobar coredumps no sature o pete algo
  # [-] Hmm, your system is configured to send core dump notifications to an      
  #     external utility. This will cause issues: there will be an extended delay 
  #     between stumbling upon a crash and having this information relayed to the 
  #     fuzzer via the standard waitpid() API.                                    
  #     If you're just testing, set 'AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1'.    
  #                                                                               
  #     To avoid having crashes misinterpreted as timeouts, please log in as root 
  #     and temporarily modify /proc/sys/kernel/core_pattern, like so:            
  #                                                                               
  #     echo core >/proc/sys/kernel/core_pattern
fi