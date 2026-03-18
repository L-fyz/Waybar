#!/bin/bash

device=$(bluetoothctl devices Connected | awk '{print $2}')

if [ -z "$device" ]; then
  echo '{"text": "󰂲 ", "class": "disconnected", "alt": "disconnected"}'
  exit 0
fi

name=$(bluetoothctl info "$device" 2>/dev/null | grep "Name:" | cut -d' ' -f2-)
charge=$(bt-battery -b "$device" 2>/dev/null | grep percentage | cut -d' ' -f2)

if [ -z "$charge" ]; then
  echo "{\"text\": \"󰂯\", \"class\": \"connected\", \"alt\": \"connected\"}"
elif [ "$charge" -gt 25 ]; then
  echo "{\"text\": \"󰂯 ${charge}%\", \"class\": \"high\", \"alt\": \"high\"}"
else
  echo "{\"text\": \"󰂯 ${charge}%\", \"class\": \"low\", \"alt\": \"low\"}"
fi
