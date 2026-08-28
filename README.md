## CAN BUS IDS SIMULATOR

Simulira omrežje CAN Bus, napade na omrežje ter delovanje časovnega in entropijskega IDS.Program je namenjen izvajanju v operacijskem sistemu Linux in uporablja SocketCAN z virtualnim CAN vmesnikom `vcan0`.

### Sistemske odvisnosti

Program zahteva Python 3 in Tkinter.

```bash
sudo apt install python3-tk
```

### Python odvisnosti

Priporočena je uporaba virtualnega okolja:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Nastavitev virtualnega CAN vmesnika

Za delovanje je potreben virtualni CAN vmesnik `vcan0` v OS Linux.

Prenos modula:

  ```bash
  sudo modprobe vcan
  ```

Ustvaritev virtualnega CAN vmesnika:

  ```bash
  sudo ip link add dev vcan0 type vcan
  ```

Vklop vmesnika:

  ```bash
  sudo ip link set up vcan0
  ```

Preverjanje delovanja:

  ```bash
  ip link show vcan0
  ```

Zagon:

  ```bash
  python main.py
  ```
