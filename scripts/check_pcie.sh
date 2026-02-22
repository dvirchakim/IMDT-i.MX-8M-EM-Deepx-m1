#!/bin/sh
echo '=== gpiochip details ==='
for chip in /sys/class/gpio/gpiochip*; do
  base=$(cat $chip/base)
  ngpio=$(cat $chip/ngpio)
  label=$(cat $chip/label)
  echo "chip=$chip base=$base ngpio=$ngpio label=$label"
done

echo '=== pca953x devices ==='
ls /sys/bus/i2c/devices/5-0020/ 2>/dev/null | head -10
cat /sys/bus/i2c/devices/5-0020/name 2>/dev/null
cat /sys/bus/i2c/devices/5-0021/name 2>/dev/null

echo '=== PCIe PHY node ==='
cat /proc/device-tree/soc@0/hsio-blk-ctrl@32f10000/pcie-phy/compatible 2>/dev/null || echo NO_PHY_NODE
ls /proc/device-tree/soc@0/hsio-blk-ctrl@32f10000/ 2>/dev/null | head -20

echo '=== PCIe phy status ==='
cat /proc/device-tree/soc@0/pcie-phy@32f00000/status 2>/dev/null || echo NO_STANDALONE_PHY

echo '=== All standalone phy nodes ==='
ls /proc/device-tree/soc@0/ | grep -i phy

echo '=== dmesg phy ==='
dmesg | grep -i 'pcie.*phy\|phy.*pcie\|serdes\|clock.*pcie' | head -20

echo '=== PCIE_AUX clock ==='
cat /sys/kernel/debug/clk/pcie_aux/clk_enable_count 2>/dev/null || echo NO_CLK_DEBUG
