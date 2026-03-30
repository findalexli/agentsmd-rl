# Fix FakeProcessGroup allgather for uneven output tensor sizes

## Bug Description

The `FakeProcessGroup` implementation in `torch/csrc/distributed/c10d/FakeProcessGroup.hpp` crashes when performing an `allgather` operation with output tensors that have different sizes from the input tensor.

In a real distributed setting, each rank may contribute a tensor of a different size. The `allgather` operation collects all tensors from all ranks. When using the `FakeProcessGroup` backend (used for testing without actual distributed communication), the current implementation unconditionally copies the input tensor into every output tensor slot via `tensor.copy_(inputTensors[0])`. This crashes when an output tensor has a different first-dimension size than the input tensor, because `copy_` requires matching shapes.

## Reproduction

```python
import torch
import torch.distributed as dist

dist.init_process_group(backend="fake", rank=0, world_size=2)

input_tensor = torch.ones(5, 3)
output_tensors = [torch.empty(5, 3), torch.empty(4, 3)]  # uneven sizes
dist.all_gather(output_tensors, input_tensor)  # CRASH: shape mismatch in copy_
```

The operation should succeed without error. Output tensors whose first dimension matches the input should be filled with the input data. Output tensors with mismatched first dimensions should be left unchanged (skipped).

## Files to Modify

- `torch/csrc/distributed/c10d/FakeProcessGroup.hpp`
