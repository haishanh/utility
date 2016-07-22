#!/bin/bash
# haishanh

# a roughly written script help deploying
# contents to github pages
# actually not restrict to github pages

GIT=${GIT:-git}
BNAME=$(basename $0)

die()
{
  echo "$@"
  exit 1
}

setup()
{
  local d="${1}"
  mkdir -p $d || die "Not able to create dir $d"
  cd $d
  echo "placeholder" > placeholder
  $GIT init
  $GIT add -A .
  $GIT commit -m "First commit"
  cd -
}

push()
{
  cd $DEPLOYDIR
  $GIT add -A .
  now=$(date +"%Y/%m/%d %H:%M")
  $GIT commit -m "Update $now" 
  $GIT push -u $REMOTE HEAD:$BRANCH --force
  cd -
}

empty()
{
  cd $DEPLOYDIR

  # remove every indexed entries recursively
  $GIT rm -r .

  cd -
}

get_remote()
{
  REMOTE=$($GIT remote -v | grep "push" | grep "github.com" | awk '{print $2}')
}

guess_branch()
{
  [ ! -z ${BRANCH} ] && return

  if git branch | grep "gh-pages"; then
    BRANCH="gh-pages"
  else
    usage_exit "Branch not set"
  fi
}

usage_exit()
{
  [ ! -z "${1}" ] && printf "\e[0;31mError: ${*}\e[0m"; echo; echo

  cat <<EOF
Usage:

  $BNAME -d DIR [-r REMOTE] [-b BRANCH] -h

  Push contents in DIR to branch BRANCH of repository REMOTE 

    -d DIR 
        Specify the directory
        where files in it will be deployed

    -r REMOTE
        Specify the remote repository
        If omitted, $BNAME will try to guess
        from the remote info of current local repo

    -b BRANCH
        Specify the remote branch 
        If omitted, $BNAME will use "gh-pages" if
        if present in current local repo

    -h
        Show this help message

Examples:

  $BNAME -d dist -r origin -b gh-pages
  $BNAME -d dist -r git@github.com:abc/xyz.git -b gh-pages
  $BNAME -d dist -b gh-pages

EOF

  exit 0
}

### MAIN ###


while getopts :hd:r:b: arg; do
  case ${arg} in
    h)
      usage_exit
      ;;
    d)
      DIR="${OPTARG}"
      ;;
    r)
      REMOTE="${OPTARG}"
      ;;
    b)
      BRANCH="${OPTARG}"
      ;;
    \?)
      usage_exit "Oops, unkonw arg..."
      ;;
  esac
done

[ -z "${DIR}" ] && usage_exit
[ ! -d $DIR ] && usage_exit "Directory $DIR is not exist"

[ -z "${REMOTE}" ] && get_remote
[ -z "${REMOTE}" ] && usage_exit "Remote repositry url needs to be specified"

guess_branch

cur=$(pwd)
prj=$(basename $cur)
DEPLOYDIR="/tmp/.deploy/$prj"

# if deploy directory is not exist, setup
[ ! -d $DEPLOYDIR ] && setup $DEPLOYDIR

# clean deploy directory
empty

# copy files to be deployed to the deploy dir
cp -r $DIR/* $DEPLOYDIR
cp $DIR/.gitignore $DEPLOYDIR > /dev/null 2>&1

# push
push
