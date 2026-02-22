#!/bin/sh
echo '=== gpioinfo avail ==='
which gpioinfo gpioset gpiofind gpioget 2>/dev/null || echo "no libgpiod tools"

echo '=== gpiochip info via sysfs ==='
ls /sys/class/gpio/

echo '=== gpiochip names via /dev ==='
ls /dev/gpiochip*

echo '=== pca6416 chip at 5-0020 gpio chip ==='
ls /sys/bus/i2c/devices/5-0020/gpiochip*/ 2>/dev/null | head -20
readlink /sys/bus/i2c/devices/5-0020/gpiochip* 2>/dev/null

echo '=== gpio chip base for 5-0020 ==='
cat /sys/bus/i2c/devices/5-0020/gpio/*/base 2>/dev/null || echo NO_OLD_SYSFS
cat /sys/bus/i2c/devices/5-0020/gpiochip*/base 2>/dev/null || echo NO_GPIOCHIP_BASE

echo '=== gpio chip base for 5-0021 ==='
cat /sys/bus/i2c/devices/5-0021/gpio/*/base 2>/dev/null || echo NO_OLD_SYSFS
cat /sys/bus/i2c/devices/5-0021/gpiochip*/base 2>/dev/null || echo NO_GPIOCHIP_BASE

echo '=== dmesg gpio expander ==='
dmesg | grep -i 'pcal\|pca953\|pcal6416\|gpio.*5-002'

echo '=== M2B GPIO expander chip number ==='
cat /sys/bus/i2c/devices/5-0020/gpio/gpiochip*/base 2>/dev/null
cat /sys/bus/i2c/devices/5-0021/gpio/gpiochip*/base 2>/dev/null

echo '=== /sys/bus/i2c/devices/5-0020/gpio/ ==='
ls /sys/bus/i2c/devices/5-0020/gpio/ 2>/dev/null
ls /sys/bus/i2c/devices/5-0021/gpio/ 2>/dev/null
