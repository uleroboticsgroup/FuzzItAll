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
    _fuzzerName=$2
    echo ${_fuzzerName} > $FUZZ_NAME_PATH/$_JOB.name

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