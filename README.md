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

All C and Python sources in my projects follow a common layout and formatting standard. The style guides and the matching check scripts live in their own repository:

➡️ **[Coding_Styleguide](https://github.com/Diveturtle93/Coding_Styleguide)**

- 📄 [C Coding Style](https://github.com/Diveturtle93/Coding_Styleguide/blob/main/C_CODING_STYLE.md) – binding style guide for `.c` / `.h` (German)
- 📄 [Python Coding Style](https://github.com/Diveturtle93/Coding_Styleguide/blob/main/PYTHON_CODING_STYLE.md) – binding style guide for `.py` (German)
- 🐍 [Stylecheck tools](https://github.com/Diveturtle93/Coding_Styleguide/tree/main/tools) – check source files against the style guides and write reports

## 📈 GitHub Stats

![GitHub stats](https://github-readme-stats.vercel.app/api?username=Diveturtle93&theme=vision-friendly-dark&show_icons=true)

![Top Langs](https://github-readme-stats.vercel.app/api/top-langs/?username=Diveturtle93&theme=vision-friendly-dark&langs_count=8&layout=donut&size_weight=0.5&count_weight=0.5)
