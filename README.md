## Hi there 👋

I’m a hardware developer for electromobility. I also develop software for embedded systems based on the STM32.

### 🔭 Electric car – hardware & software

I’m currently working on the hardware and software for an electric car. From schematic and PCB design to the firmware running on the STM32, everything is developed in-house.

- 🦶 **Pedal controller** – a new control unit that evaluates the accelerator and brake pedals and passes the values on to the rest of the vehicle via CAN.
- 🔌 **Peripherals** – further control units and boards that connect sensors, actuators and the vehicle electronics.
- 🔋 **Battery management system (BMS)** – still to be integrated, to monitor cell voltages and temperatures and keep the battery pack in a safe operating range.

### 📊 Data logging

A Raspberry Pi acts as the data logger of the vehicle:

- reads out all messages on the CAN bus,
- analyses and decodes the data,
- saves the measurements for later evaluation.

### 🖥️ Live dashboard

In addition, I’m working on a live view that shows the CAN data directly in the browser. It runs on a laptop and receives the data via a CAN adapter.

The current focus is on the structure and architecture of the dashboard:

- 🏗️ **Framework** – the basic setup that connects the CAN adapter to the live view in the browser.
- 🔄 **Decoders** – translate the raw CAN messages into physical values; they are added individually later on.
- 📟 **Widgets** – the individual displays for these values; they are also created afterwards, as the signals are not yet fixed.

### 🌱 Learning

I’m currently digging deeper into the STM32 itself: how the microcontroller is built internally, how its peripherals, buses and memory are structured, and how this knowledge leads to cleaner and more efficient firmware.

## 🧰 Coding Style

All C sources (`.c` / `.h`) in my projects follow a common layout and formatting standard:

- 📄 [C_CODING_STYLE.md](C_CODING_STYLE.md) – the binding style guide (German)
- 🐍 [tools/c_stylecheck.py](tools/c_stylecheck.py) – checks C files against the style guide

```sh
py tools/c_stylecheck.py                  # all ../STM32_* folders next to this repo
py tools/c_stylecheck.py ../STM32_Canbus  # a single project
py tools/c_stylecheck.py -r               # write reports to reports/<YYYYMMDD>_<project>.txt
```

Generated or third-party files (HAL, CMSIS, CubeMX, build output) are skipped automatically.

## 📈 GitHub Stats

![GitHub stats](https://github-readme-stats.vercel.app/api?username=Diveturtle93&theme=vision-friendly-dark&show_icons=true)

![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=Diveturtle93&theme=vision-friendly-dark&langs_count=8&layout=donut&size_weight=0.5&count_weight=0.5)
