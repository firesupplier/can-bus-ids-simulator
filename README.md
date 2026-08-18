## CAN BUS IDS SIMULATOR

Simulira omrežje CAN Bus, napade na omrežje ter delovanje časovnega in entropijskega IDS.

### Potrebni moduli

```bash
pip install python-tk
pip install python-can
```

### Zagon

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

Zagon programa:

  ```bash
  python main.py
  ```
