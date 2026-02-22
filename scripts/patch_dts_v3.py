#!/usr/bin/env python3
"""
Patch DTS v2 -> v3:
- PCIe_SEL_3V3 (gpiochip5=phandle TBD, line 8, active-high) added as always-on GPIO output HIGH
  to select PCIe mode on the M.2 B-slot mux.
- Use a simple 'gpio-leds' or 'gpio-hog' approach since we want it always-high at boot.
"""

DTS_IN = '/mnt/c/Users/dvir/CascadeProjects/smartshooter_imx_deepx/imx8mp-imdt-pico-v2.dts'
DTS_OUT = '/mnt/c/Users/dvir/CascadeProjects/smartshooter_imx_deepx/imx8mp-imdt-pico-v3.dts'

dts = open(DTS_IN).read()

# First, find phandle 0x65 or the actual phandle for gpiochip5 (5-0020, pca953x)
# From the DTB we know:
#   phandle 0x6a = gpiochip6 (5-0021, M2B GPIOs)
#   phandle 0x6b = regulator-3v3
#   gpiochip5 (5-0020) = PCB test points + PCIe_SEL_3V3 
# We need to find the phandle for the 5-0020 gpio expander
idx = dts.find('phandle = <0x6a>')
section = dts[max(0,idx-2000):idx]
# Find the i2c address 5-0020 controller phandle
# Actually from the gpioinfo output, gpiochip5 = 5-0020
# Let's search for the pcal6416 / pca953x at address 0x20 on i2c bus 5

# Find the phandle for gpiochip5 by looking near "M2B_CONFIG_0" (which is on gpiochip6 = 0x6a)
# and "PCIe_SEL_3V3" (which is on gpiochip5)
# From DTB decompile, we saw the gpio-line-names with M2B_* are on phandle 0x6a
# gpiochip5 should be phandle 0x6a-1 = 0x69? No, that's the HSIO PHY.
# Let's search the DTS for PCIe_SEL or TP756 (first line on gpiochip5)

import re

# Find the node containing "TP756" line name (gpiochip5 = 5-0020)
m = re.search(r'phandle = <(0x[0-9a-f]+)>;[^}]*?};\s*\n\s*};\s*\n', dts)

# Alternative: search for gpio-line-names containing PCIe_SEL_3V3 or TP756
# The gpio-line-names for gpiochip5 contains: TP756, TP757, GBE_RSTn, ..., PCIe_SEL_3V3
lines_marker = 'PCIe_SEL_3V3'
if lines_marker in dts:
    idx2 = dts.find(lines_marker)
    # Find the phandle in the surrounding node (search backwards for 'phandle = ')
    chunk = dts[max(0, idx2-3000):idx2+200]
    phandles = re.findall(r'phandle = <(0x[0-9a-f]+)>', chunk)
    if phandles:
        gpiochip5_phandle = phandles[-1]  # closest preceding phandle
        print(f'[INFO] gpiochip5 phandle likely: {gpiochip5_phandle}')
    else:
        gpiochip5_phandle = '0x68'  # fallback guess
        print(f'[WARN] could not find phandle, using guess {gpiochip5_phandle}')
else:
    gpiochip5_phandle = '0x68'
    print(f'[WARN] PCIe_SEL_3V3 not found in DTS, using guess {gpiochip5_phandle}')

print(f'Using gpiochip5 phandle: {gpiochip5_phandle}')

# Add a gpio-hog inside the gpiochip5 node to drive PCIe_SEL_3V3 HIGH
# gpio-hog: added as a child of the gpio controller node
# Find the gpiochip5 node closing brace and insert before it

# Locate the gpiochip5 node — find PCIe_SEL_3V3 label and its containing node
idx_sel = dts.find('PCIe_SEL_3V3')
# Find the closing '};\n' for this gpio node (its parent, which is the expander node)
# Walk backwards to find 'gpio@20' or similar
chunk_before = dts[max(0,idx_sel-3000):idx_sel]
# Find ending of the gpio expander node by finding the gpio-line-names property end
# then the two closing '};' (one for the gpio node, one for the i2c node)

# Simpler approach: find the exact closing of the gpio expander block
# Look for closing }; after PCIe_SEL_3V3 in the gpio-line-names context
idx_after = dts.find('};', idx_sel)  # closes gpio-line-names / the expander
idx_close = dts.find('};', idx_after + 2)  # closes gpio@20 node

# Actually the structure is:
#   gpio@20 {
#       gpio-line-names = "TP756\0...\0PCIe_SEL_3V3\0..."
#       phandle = <0xXX>
#   };
# We want to insert a gpio-hog INSIDE the gpio@20 node, before the closing };

hog_node = """
                        pcie-sel-hog {
                                gpio-hog;
                                gpios = <0x08 0x00>;
                                output-high;
                                line-name = "PCIe_SEL_3V3";
                        };
"""

# Find the gpiochip5 phandle line and the }; after it
ph_search = f'phandle = <{gpiochip5_phandle}>;'
if ph_search in dts:
    ph_idx = dts.find(ph_search)
    close_idx = dts.find('};', ph_idx)
    insert_pos = close_idx  # insert before '};' of the gpio@20 node
    dts = dts[:insert_pos] + hog_node + dts[insert_pos:]
    print(f'[OK] gpio-hog inserted before closing of gpio node (phandle {gpiochip5_phandle})')
else:
    print(f'[WARN] "{ph_search}" not found — trying alternative insertion')
    # Insert near PCIe_SEL_3V3 gpio-line-names
    nl_idx = dts.find('\\0PCIe_SEL_3V3')
    if nl_idx > 0:
        close = dts.find('};', nl_idx)
        close2 = dts.find('};', close + 2)
        dts = dts[:close2] + '\n' + hog_node + dts[close2:]
        print('[OK] gpio-hog inserted near PCIe_SEL_3V3 gpio-line-names')

open(DTS_OUT, 'w').write(dts)
print('[DONE] v3 DTS written to', DTS_OUT)

# Verify
if 'gpio-hog' in dts:
    print('[OK] gpio-hog is present in output DTS')
if 'pcie-sel-hog' in dts:
    print('[OK] pcie-sel-hog node confirmed')
