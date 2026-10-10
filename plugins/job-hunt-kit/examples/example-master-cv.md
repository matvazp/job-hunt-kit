# Master CV — Alex Sample (FICTIONAL EXAMPLE)

> [!info] How to use this document
> Single source of truth for every tailored CV, cover letter and fit assessment. Tailoring may
> rephrase, reorder, shorten and translate into a posting's vocabulary, but never invent a tool,
> metric, title, date or result that isn't written here.
>
> **Framing notes.** "CV-safe" lines are the short forms to use on a CV; "fuller story" lines are
> context for cover letters and interviews.

## Contact

- Location: Utrecht, Netherlands (moved from Porto in 2022)
- Email / phone / website / LinkedIn: see `job-hunt.yaml`

## Reusable profile paragraphs

- **Embedded / firmware roles:** Embedded systems engineer with six years of firmware and board
  bring-up for battery-powered sensor products, from first prototype to certified volume
  production.
- **Hardware product roles:** Electronics engineer who owns low-power IoT products end to end
  (schematic, layout, firmware, test and certification) and works closely with mechanical and
  manufacturing partners.
- **Test & validation roles:** Engineer who builds automated hardware-in-the-loop test systems in
  Python and uses them to keep embedded products shippable on every merge.

## Key strengths

- End-to-end product ownership: took two products from prototype to volume production
- Low-power design: 4× battery-life improvement on a shipped product
- Clear documentation: wrote the firmware architecture docs used to onboard 3 engineers
- Calm under deadlines: led the CE re-certification sprint in 2023
- Cross-team collaborator: daily work with mechanical, cloud and manufacturing teams
- Data-driven debugging: power profiling and field-telemetry analysis

## Professional experience

### Senior Embedded Engineer — Example Sensors B.V., Utrecht, NL (Mar 2022 – present)

- Owned firmware and electronics for the SoilSense LoRaWAN soil-moisture sensor; ~40,000 units
  deployed across 3 countries.
- Cut average current draw from 48 µA to 11 µA (duty-cycling, sensor power gating, LoRa ADR
  tuning), extending projected battery life from 2 to 7 years.
  - CV-safe: "Cut average current from 48 µA to 11 µA, extending battery life from 2 to 7 years."
- Built a Python/pytest hardware-in-the-loop rig (Raspberry Pi + relay board + Otii power
  analyser) running 300 regression tests on every merge via GitHub Actions self-hosted runner.
- Led the 2023 CE/RED re-certification after a radio module change; coordinated with the test lab.
- Designed rev C of the main board in KiCad (4-layer, nRF52840 + SX1262); managed DFM review
  with the contract manufacturer in Poland.
- Mentored 2 junior engineers; wrote the firmware architecture documentation.
- Tools: C, Zephyr RTOS, nRF52840, SX1262, KiCad, Python, pytest, Otii Arc, GitHub Actions, Jira.

### Embedded Software Engineer — Fictional Devices Lda., Porto, PT (Sep 2019 – Feb 2022)

- Developed BLE firmware (FreeRTOS on STM32WB55) for the PulseBand wearable heart-rate monitor,
  through CE certification and a production run of ~8,000 units.
- Implemented an OTA update bootloader with dual-bank fallback; zero bricked devices in the field.
- Wrote the production test firmware and the Python station software used on the factory line.
- Tools: C, C++17, FreeRTOS, STM32WB55, BLE, Altium Designer (reviews only), Python.

### Graduate Engineer — Placeholder Automation, Lisbon, PT (Sep 2018 – Aug 2019)

- Wrote PLC (Siemens S7, TIA Portal) and HMI logic for packaging lines; commissioned three lines on
  customer sites.

## Projects

### Open-source Zephyr driver for the SHT45 humidity sensor (2023)

- Upstreamed to the Zephyr project; ~200 lines of C plus devicetree bindings.

### M.Sc. thesis — energy-harvesting wireless sensor node (2018)

- Solar-powered sensor node on an MSP430; achieved indefinite operation at 1 reading/min indoors.

## Skills inventory

- **Firmware:** C, C++17, Zephyr, FreeRTOS, bare-metal; nRF52, STM32 (L4, WB), ESP32, MSP430;
  bootloaders, OTA; SPI, I²C, UART, BLE, LoRaWAN.
- **Hardware:** KiCad (4-layer designs), Altium (review level), power budgeting, battery
  management, EMC pre-compliance scans.
- **Test & tooling:** Python, pytest, HIL rigs, Otii Arc, oscilloscope, logic analyser, GitHub
  Actions, Docker (basic).
- **Process:** design reviews, DFM, CE/RED certification, Jira, Confluence.

## Education

- M.Sc., Electrical and Computer Engineering, University of Example, Porto (2016 – 2018). Thesis:
  energy-harvesting wireless sensor node.
- B.Sc., Electrical Engineering, University of Example, Porto (2013 – 2016).

## Certifications, publications, patents, awards

- 1 conference paper: "Indoor energy harvesting for sensor nodes", Example Conference 2018.

## Languages

- English — Fluent (C1)
- Portuguese — Native
- Dutch — B1, studying

## Known self-assessed gaps

- Linux kernel / embedded Linux (Yocto) — only hobby-level Raspberry Pi work.
- Safety-critical standards (ISO 26262, IEC 62304) — none; CE/RED only.
- RF design beyond integrating certified modules — none.
- People management — mentoring only, no direct reports.

## Cover letter opening fragments

- I like products that have to survive years in a field without anyone touching them.
- The most satisfying number of my career is "7 years" on a battery label.
