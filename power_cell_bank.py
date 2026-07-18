import sys
from typing import Optional


class _Cell:
    """A single power cell.

    The charge window of a cell at some ``timestamp`` is
    ``load_ts + rated_duration - timestamp``.  Because that value only shifts by
    a constant (``-timestamp``) for every cell simultaneously, the *relative*
    ordering of cells by charge window never changes over time and can be driven
    purely by ``priority = load_ts + rated_duration``.
    """

    __slots__ = ("cell_id", "load_ts", "rated_duration", "priority")

    def __init__(self, cell_id: str, load_ts: float, rated_duration: float) -> None:
        self.cell_id = cell_id
        self.load_ts = load_ts
        self.rated_duration = rated_duration
        self.priority = load_ts + rated_duration

    def is_spent(self, timestamp: float) -> bool:
        return timestamp - self.load_ts >= 2.0 * self.rated_duration

    def is_charged(self, timestamp: float) -> bool:
        return timestamp - self.load_ts < self.rated_duration


class PowerCellBank:
    def __init__(self, num_racks: int) -> None:
        self.num_racks = num_racks
        # racks[i] models rack (i + 1); rack 1 (index 0) is the front rack.
        self.racks: list[list[_Cell]] = [[] for _ in range(num_racks)]
        # Rack i (1-indexed) has capacity 2^i.
        self.capacity: list[int] = [1 << (i + 1) for i in range(num_racks)]

    # ------------------------------------------------------------------ #
    # Spent-cell handling
    # ------------------------------------------------------------------ #
    def _purge_rack(self, idx: int, timestamp: float) -> None:
        rack = self.racks[idx]
        alive = [c for c in rack if not c.is_spent(timestamp)]
        if len(alive) != len(rack):
            self.racks[idx] = alive

    def _purge_all(self, timestamp: float) -> None:
        for i in range(self.num_racks):
            self._purge_rack(i, timestamp)

    # ------------------------------------------------------------------ #
    # LoadCell
    # ------------------------------------------------------------------ #
    def load_cell(self, timestamp: float, cell_id: str, rated_duration: float) -> bool:
        for i in range(self.num_racks):
            self._purge_rack(i, timestamp)
            if len(self.racks[i]) < self.capacity[i]:
                self.racks[i].append(_Cell(cell_id, timestamp, rated_duration))
                return True
        return False

    # ------------------------------------------------------------------ #
    # Discharge
    # ------------------------------------------------------------------ #
    def discharge(self, timestamp: float, max_dispatch: int) -> list[str]:
        self._purge_all(timestamp)
        self._equalise(timestamp)
        return self._bus_shift(timestamp, max_dispatch)

    def _equalise(self, timestamp: float) -> None:
        for k in range(self.num_racks - 1):
            rack_k = self.racks[k]
            rack_kp1 = self.racks[k + 1]

            total_k = len(rack_k)
            if total_k == 0:
                continue

            charged_k = sum(1 for c in rack_k if c.is_charged(timestamp))
            # below-sag: charged fraction strictly below 50% -> 2*charged < total
            if not (2 * charged_k < total_k):
                continue

            # rack k+1's charged cells ordered most-charged first
            # (largest priority, ties broken by smallest cell_id).
            kp1_charged = [c for c in rack_kp1 if c.is_charged(timestamp)]
            if not kp1_charged:
                continue
            kp1_charged.sort(key=lambda c: (-c.priority, c.cell_id))

            # Each balance swap moves out one of rack k's depleted cells and
            # brings in a charged cell, so charged_k grows by one per swap.
            # Determine how many swaps run before rack k is no longer below-sag
            # or rack k+1 runs out of charged cells.
            swaps = 0
            ch = charged_k
            while 2 * ch < total_k and swaps < len(kp1_charged):
                ch += 1
                swaps += 1
            if swaps == 0:
                continue

            # rack k's most-depleted cells: smallest priority, ties smallest id.
            k_sorted = sorted(rack_k, key=lambda c: (c.priority, c.cell_id))
            depleted_out = k_sorted[:swaps]
            charged_in = kp1_charged[:swaps]

            out_ids = {id(c) for c in depleted_out}
            in_ids = {id(c) for c in charged_in}

            self.racks[k] = [c for c in rack_k if id(c) not in out_ids] + charged_in
            self.racks[k + 1] = [c for c in rack_kp1 if id(c) not in in_ids] + depleted_out

    def _bus_shift(self, timestamp: float, max_dispatch: int) -> list[str]:
        result: list[str] = []
        for _ in range(max_dispatch):
            # Active rack: front-most rack holding at least one cell.
            active = -1
            for i in range(self.num_racks):
                if self.racks[i]:
                    active = i
                    break
            if active == -1:
                break

            cell = self._pop_most_charged(active)
            state = "charged" if cell.is_charged(timestamp) else "depleted"
            result.append(f"{cell.cell_id}:{state}")

            # Inward shift: cascade the most-charged cell forward from each rack
            # behind, halting when the next rack back is empty or absent.
            r = active
            while r + 1 < self.num_racks and self.racks[r + 1]:
                self.racks[r].append(self._pop_most_charged(r + 1))
                r += 1
        return result

    def _pop_most_charged(self, idx: int) -> _Cell:
        rack = self.racks[idx]
        best = 0
        best_cell = rack[0]
        for i in range(1, len(rack)):
            c = rack[i]
            if c.priority > best_cell.priority or (
                c.priority == best_cell.priority and c.cell_id < best_cell.cell_id
            ):
                best = i
                best_cell = c
        return rack.pop(best)


def main() -> None:
    bank: Optional[PowerCellBank] = None
    out_lines: list[str] = []

    for raw in sys.stdin.read().splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        op = parts[0]

        if op == "Init":
            bank = PowerCellBank(int(parts[1]))
        elif op == "LoadCell":
            assert bank is not None
            result = bank.load_cell(float(parts[1]), parts[2], float(parts[3]))
            out_lines.append(f"LoadCell={result}")
        elif op == "Discharge":
            assert bank is not None
            result = bank.discharge(float(parts[1]), int(parts[2]))
            out_lines.append(f"Discharge={result}")

    sys.stdout.write("\n".join(out_lines))
    if out_lines:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
