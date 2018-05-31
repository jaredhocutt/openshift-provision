#!/usr/bin/env bash

set -e

USER_UID=$(id --user)

if [[ $USER_UID == 0 ]]; then
  echo "Do not run this container as root."
  echo
  echo "It is recommended to pass the following option when starting the container:"
  echo "    --user \$(id -u \$USER)"
  echo
  echo "Example:"
  echo "    docker run -it --rm --user \$(id -u \$USER) --volume \$(pwd):/app:z openshift-provision"

  exit 1
fi

useradd --uid $(id --user) --gid $(id --group) --shell $(which bash) --home-dir /app --no-create-home provision

if [[ $# == 0 ]]; then
  if [[ -t 0 ]]; then
    echo "Starting shell..."
    echo

    exec "bash"
  else
    echo "An interactive shell was not detected."
    echo
    echo "By default, this container starts a bash shell, be sure you are passing '-it' to your run command."

    exit 1
  fi
else
  exec "$@"
fi
