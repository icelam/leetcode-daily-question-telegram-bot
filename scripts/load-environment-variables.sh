# For exporting environment variables from .env files via Makefile

LOCAL_ENV_FILE=.env.local
ENV_FILE=.env

if test -f "$LOCAL_ENV_FILE" ; then
  export $(grep -v '^#' $LOCAL_ENV_FILE | xargs)
else
  export $(grep -v '^#' $ENV_FILE | xargs)
fi
