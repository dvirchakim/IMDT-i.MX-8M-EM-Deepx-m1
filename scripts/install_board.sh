#!/bin/sh
# Minimal installation script for DeepX NPU on i.MX 8M-EM SBC

# 1. Install libraries
echo 'Installing libraries...'
cp -a lib/* /usr/lib/
ldconfig

# 2. Install binaries
echo 'Installing binaries...'
cp bin/* /usr/bin/
chmod +x /usr/bin/dxrt-cli /usr/bin/dxtop /usr/bin/dxbenchmark /usr/bin/dxrtd

# 3. Install drivers
echo 'Installing drivers...'
# Ensure directory exists
MOD_DIR="/lib/modules/$(uname -r)/extra"
mkdir -p "$MOD_DIR"
cp drivers/*.ko "$MOD_DIR"/
depmod -a

# 4. Load drivers
echo 'Loading drivers...'
modprobe dx_dma 2>/dev/null || insmod drivers/dx_dma.ko
modprobe dxrt_driver 2>/dev/null || insmod drivers/dxrt_driver.ko

# 5. Verify
echo 'Verifying...'
lsmod | grep dx
lspci -nnk -d 1ff4:0000

echo 'DeepX NPU software stack installed!'
