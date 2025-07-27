#!/usr/bin/env bash

# Fail on error, verbose output
set -exo pipefail

# Build project
ndk-build NDK_DEBUG=1 1>&2

# Figure out which ABI and SDK the device has
abi=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')
sdk=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
pre=$(adb shell getprop ro.build.version.preview_sdk | tr -d '\r')
rel=$(adb shell getprop ro.build.version.release | tr -d '\r')

if [[ -n "$pre" && "$pre" > "0" ]]; then
  sdk=$(($sdk + 1))
fi

# PIE is only supported since SDK 16
if (($sdk >= 16)); then
  bin=minicap
else
  bin=minicap-nopie
fi

args=
if [ "$1" = "autosize" ]; then
  set +o pipefail
  size=$(adb shell dumpsys window | grep -Eo 'init=[0-9]+x[0-9]+' | head -1 | cut -d= -f 2)
  if [ "$size" = "" ]; then
    w=$(adb shell dumpsys window | grep -Eo 'DisplayWidth=[0-9]+' | head -1 | cut -d= -f 2)
    h=$(adb shell dumpsys window | grep -Eo 'DisplayHeight=[0-9]+' | head -1 | cut -d= -f 2)
    size="${w}x${h}"
  fi
  args="-P $size@$size/0"
  set -o pipefail
  shift
fi

# Create a directory for our resources
dir=/data/local/tmp/minicap-devel
# Keep compatible with older devices that don't have `mkdir -p`.
adb shell "mkdir $dir 2>/dev/null || true"

# Upload the binary
adb push libs/$abi/$bin $dir

# Upload the shared library
# Try to find the appropriate library version
lib_path=""
if [ -e jni/minicap-shared/aosp/libs/android-$rel/$abi/minicap.so ]; then
  lib_path="jni/minicap-shared/aosp/libs/android-$rel/$abi/minicap.so"
elif [ -e jni/minicap-shared/aosp/libs/android-$sdk/$abi/minicap.so ]; then
  lib_path="jni/minicap-shared/aosp/libs/android-$sdk/$abi/minicap.so"
else
  # Find the highest available version
  highest_version=0
  for version_dir in jni/minicap-shared/aosp/libs/android-*; do
    if [ -d "$version_dir" ] && [ -e "$version_dir/$abi/minicap.so" ]; then
      version_num=$(basename "$version_dir" | sed 's/android-//')
      if [ "$version_num" -gt "$highest_version" ]; then
        highest_version=$version_num
        lib_path="$version_dir/$abi/minicap.so"
      fi
    fi
  done
fi

if [ -n "$lib_path" ]; then
  echo "Using library: $lib_path"
  adb push "$lib_path" $dir
else
  echo "Error: No compatible minicap.so library found for ABI $abi"
  exit 1
fi

# Run!
echo "Starting minicap with args: $args"
adb shell "cd $dir && LD_LIBRARY_PATH=$dir ./$bin $args" "$@"

# Clean up
adb shell rm -r $dir
