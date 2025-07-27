#!/usr/bin/env bash

# Fail on error, verbose output
set -exo pipefail

# Get screen size
size=$(adb shell dumpsys window | grep -Eo 'init=[0-9]+x[0-9]+' | head -1 | cut -d= -f 2)
if [ "$size" = "" ]; then
  w=$(adb shell dumpsys window | grep -Eo 'DisplayWidth=[0-9]+' | head -1 | cut -d= -f 2)
  h=$(adb shell dumpsys window | grep -Eo 'DisplayHeight=[0-9]+' | head -1 | cut -d= -f 2)
  size="${w}x${h}"
fi

echo "Screen size: $size"

# Create output directory
mkdir -p screenshots

# Take screenshot
timestamp=$(date +%Y%m%d_%H%M%S)
output_file="screenshots/screenshot_${timestamp}.png"

echo "Taking screenshot..."
adb shell screencap -p /sdcard/screenshot.png
adb pull /sdcard/screenshot.png "$output_file"
adb shell rm /sdcard/screenshot.png

echo "Screenshot saved to: $output_file"

# If -t flag is provided, show the image
if [[ "$*" == *"-t"* ]]; then
  if command -v display >/dev/null 2>&1; then
    echo "Displaying screenshot..."
    display "$output_file" &
  elif command -v feh >/dev/null 2>&1; then
    echo "Displaying screenshot..."
    feh "$output_file" &
  elif command -v xdg-open >/dev/null 2>&1; then
    echo "Opening screenshot..."
    xdg-open "$output_file" &
  else
    echo "No image viewer found. Screenshot saved to: $output_file"
  fi
fi 