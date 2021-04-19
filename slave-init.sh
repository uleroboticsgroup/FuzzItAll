# Load WLP context variables
source $1/conf.conf
source ./HS.conf

echo "DEBUG: $0 $1 $2"

# Local script variables
_JOB=`echo $1 | sed -r 's/\/+/_/g'`
_fuzzerName="$2"

echo "DEBUG: _fuzzerName $_fuzzerName" 

# Check for master fuzzer existance
if [ -f "$FUZZ_NAME_PATH/$_JOB.name" ]; then
  echo "DEBUG: New task $_out" 
  # New slave task
  env AFL_PATH="$TLB_AFL_PATH_FUZZ" AFL_NO_AFFINITY=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1 ${TLB_AFL_PATH_FUZZ}/afl-fuzz -i $1/$corpus_path -o $1/fuzz_out -S  $_fuzzerName $1/$run

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
else
  echo "ERROR: No master fuzzer was detected."
fi