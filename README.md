# DeepX DX-M1 Integration for IMDT i.MX 8M Plus SBC

This repository contains the necessary firmware patches, drivers, and runtime libraries to enable and run the **DeepX DX-M1 NPU** on the **IMD-TEC i.MX 8M Plus (Pico/EM)** Single Board Computer.

## 🚀 Overview
The DeepX DX-M1 is a high-performance AI accelerator. On the IMDT i.MX 8M Plus SBC, the M.2 B-key slot (often used for PCIe) requires specific Device Tree configurations for power management, mode selection, and reset signaling to properly enumerate the card.

This project provides:
- **Binary Device Tree (DTB)** with full hardware fixes.
- **Cross-compiled Linux Drivers** for Kernel 6.6.52.
- **DeepX Runtime (DXRT)** libraries and CLI tools for AArch64.
- **Automated Installation Scripts**.

---

## 🛠️ Hardware Fixes (The "PCIe Link Failure" Solution)
The default IMDT Device Tree fails to link with the DX-M1 due to:
1. **Incorrect Reset Pin**: M.2 Pin 5 (`M2B_PCIeRST`) was not correctly mapped.
2. **Missing Power Control**: M.2 B-slot power (`M2B_CARD_ONOFFn`) was not enabled.
3. **Mux Selection**: The lane was not explicitly set to PCIe mode over USB3/SATA.

**Solution**: This repo provides `imx8mp-imdt-pico-v3.dtb` which resolves these issues at boot time.

---

## 📂 Repository Structure
- `firmware/`: Final working `.dtb` and `.dts` files.
- `sdk/`: `deepx_deploy_aarch64.tar.gz` - The full driver/runtime bundle.
- `scripts/`: Diagnostic tools and the `install_board.sh` script.
- `docs/`: Technical deep-dive into the hardware fixes.

---

## ⚡ Quick Start

### 1. Hardware Enablement (DTB Flash)
1. Copy `firmware/imx8mp-imdt-pico-v3.dtb` to the board's boot partition (e.g., `/run/media/boot.../`).
2. Overwrite the default `imx8mp-imdt-pico.dtb` (backup existing first).
3. Reboot the board.
4. Verify detection with `lspci`. You should see:
   `01:00.0 Processing accelerators: DEEPX Co., Ltd. DX_M1 [1ff4:0000]`

### 2. Software Installation
1. Transfer `sdk/deepx_deploy_aarch64.tar.gz` to the board's `/tmp`.
2. Extract and run the installer:
   ```bash
   cd /tmp
   tar -xzf deepx_deploy_aarch64.tar.gz
   cd deploy_package
   sh scripts/install_board.sh
   ```

---

## 🏎️ Performance Benchmark (YOLOv8n)
We performed a headless dry run using the `dxbenchmark` tool on the board.

| Metric | Result |
|---|---|
| **Model** | YOLOv8n (DeepX Optimized) |
| **Throughput** | **~19.5 FPS** |
| **Inference Latency** | **11-13 ms** (NPU core) |
| **Thermal Profile** | **55°C** (Stable under load) |

### How to Run:
```bash
# 1. Start the runtime daemon
dxrtd &

# 2. Run the benchmark tool
dxbenchmark --dir /tmp/ --loops 100 --verbose
```

---

## 🏗️ Building from Source (Cross-Compilation)
If you need to rebuild the drivers for a different kernel:
1. Use **WSL2 (Ubuntu 22.04)**.
2. Install the cross-compiler: `sudo apt install crossbuild-essential-arm64`.
3. Clone [linux-imdt](https://github.com/imd-tec/linux-imdt) (Branch: `imdt-6.6.y`).
4. Build using the DeepX [dx-all-suite](https://github.com/deepx-ai/dx-all-suite).

---

## 📄 License
This documentation and the provided scripts are released under the MIT License. Driver and Runtime binaries are subject to DeepX AI's respective licenses.
