# Fix FakeProcessGroup allgather crash with uneven tensor sizes

## Bug Description

PyTorch's `FakeProcessGroup` backend (used for testing distributed operations without actual communication) crashes when performing an `allgather` operation where output tensors have different first-dimension sizes than the input tensor.

In a real distributed setting, each rank may contribute a tensor of a different size. The `allgather` operation collects tensors from all ranks. When using `FakeProcessGroup`, the operation fails with a shape mismatch error if any output tensor's first dimension differs from the input tensor's first dimension.

## Reproduction

```python
import torch
import torch.distributed as dist

dist.init_process_group(backend="fake", rank=0, world_size=2)

input_tensor = torch.ones(5, 3)
output_tensors = [torch.empty(5, 3), torch.empty(4, 3)]  # uneven sizes
dist.all_gather(output_tensors, input_tensor)  # CRASH: shape mismatch
```

## Expected Behavior

The `allgather` operation should complete successfully without crashing. Output tensors whose first dimension matches the input tensor should be filled normally, while output tensors with a different first-dimension size should be left unmodified.
