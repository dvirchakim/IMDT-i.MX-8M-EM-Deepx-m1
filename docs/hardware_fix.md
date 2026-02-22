# DeepX DX-M1 PCIe Integration — Phase 1 Summary

This archive contains the files and scripts used to diagnose and resolve the PCIe hardware link issue for the DeepX DX-M1 NPU on the i.MX 8M-EM SBC.

## Status: SUCCESS
The NPU is now successfully detected on the PCIe bus:
`01:00.0 Processing accelerators [1200]: DEEPX Co., Ltd. DX_M1 [1ff4:0000] (rev 01)`

## Root Cause Analysis
The primary blocker was a **PCIe PHY Link Failure** caused by three configuration errors in the default Device Tree:
1.  **Inverse/Incorrect Reset Pin:** The `reset-gpio` was pointing to M.2 pin 11 (`M2B_FLIGHT_MODE`) instead of pin 5 (`M2B_PCIeRST`).
2.  **Missing Power Enable:** The M.2 B-slot power control pin (`M2B_CARD_ONOFFn`) was not being driven, leaving the card unpowered.
3.  **Mux Selection:** The `PCIe_SEL_3V3` signal was not set to select PCIe mode over USB3/SATA.

## Applied Solution (DTB v3)
We created a patched Device Tree (`imx8mp-imdt-pico-v3.dtb`) with the following changes:
-   **Reset Fix:** Updated `pcie@33800000` to use `reset-gpio = <&gpiochip6 5 GPIO_ACTIVE_LOW>`.
-   **Power Management:** Added a fixed GPIO regulator `vpcie-supply` tied to `M2B_CARD_ONOFFn` (gpiochip6 pin 4, active-low) to ensure the card powers on at boot.
-   **Mux Selection:** Added a `gpio-hog` to drive `PCIe_SEL_3V3` (gpiochip5 pin 8) HIGH at boot.

## Archive Contents
### Working DTB
-   `imx8mp-imdt-pico-v3.dtb`: **The final working binary.** Install this to the board's boot partition.

### Hardware Diagnostic & Control Scripts (Run on Board)
-   `check_pcie.sh` / `check_pcie2.sh`: Comprehensive PCIe/GPIO status checks.
-   `check_gpio.sh`: GPIO chip enumeration.
-   `card_power_on.sh`: Manual runtime power-on attempt (v2).
-   `enable_m2b.py`: Python-based power/reset sequence test.

### Patching Source Files (Host)
-   `patch_dts.py` / `patch_dts_v3.py`: Python scripts used to modify the decompiled DTS.
-   `imx8mp-imdt-pico-v3.dts`: The human-readable Device Tree Source for reference.

## Next Steps
Proceed to **Phase 2: Cross-Compiling the NPU Driver** in WSL using kernel source `6.6.52-lts-next-g186602c566f7`.
