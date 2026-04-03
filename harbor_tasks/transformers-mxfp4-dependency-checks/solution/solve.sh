#!/usr/bin/env bash
set -euo pipefail
cd /workspace/transformers

# Idempotent: check if patch is already applied
if grep -q 'kernels_installed' src/transformers/quantizers/quantizer_mxfp4.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

python3 -c "
import re

path = 'src/transformers/quantizers/quantizer_mxfp4.py'
with open(path) as f:
    src = f.read()

# 1. Split combined kernels_available into separate triton_available and kernels_installed
#    Three branches: xpu, cuda, cpu — each has the same pattern
src = re.sub(
    r'kernels_available = is_triton_available\(\"([\d.]+)\"\) and is_kernels_available\(\)',
    r'triton_available = is_triton_available(\"\1\")\n            kernels_installed = is_kernels_available()',
    src,
)

# 2. The else branch: kernels_available = False -> two variables
src = src.replace(
    '            kernels_available = False',
    '            triton_available = False\n            kernels_installed = False',
)

# 3. pre_quantized warning branch: split 'if not kernels_available' into triton + kernels
old_warning = '''            if not kernels_available:
                logger.warning_once(
                    \"MXFP4 quantization requires Triton and kernels installed: CUDA requires Triton >= 3.4.0, XPU requires Triton >= 3.5.0, we will default to dequantizing the model to bf16\"
                )
                self.quantization_config.dequantize = True
                return'''

new_warning = '''            if not triton_available:
                logger.warning_once(
                    \"MXFP4 quantization requires Triton: CUDA requires Triton >= 3.4.0, \"
                    \"XPU/CPU requires Triton >= 3.5.0. Please install triton: \`pip install triton\`. \"
                    \"We will default to dequantizing the model to bf16.\"
                )
                self.quantization_config.dequantize = True
                return

            if not kernels_installed:
                logger.warning_once(
                    \"MXFP4 quantization requires the \`kernels\` package: \"
                    \"\`pip install kernels>=0.12.0\`. \"
                    \"We will default to dequantizing the model to bf16.\"
                )
                self.quantization_config.dequantize = True
                return'''

src = src.replace(old_warning, new_warning)

# 4. non-pre_quantized error branch: split 'elif not kernels_available' into triton + kernels
old_error = '''        elif not kernels_available:
            # we can't quantize the model in this case so we raise an error
            raise ValueError(
                \"MXFP4 quantization requires Triton and kernels installed: CUDA requires Triton >= 3.4.0, XPU/CPU requires Triton >= 3.5.0\"
            )'''

new_error = '''        elif not triton_available:
            raise ValueError(
                \"MXFP4 quantization requires Triton: CUDA requires Triton >= 3.4.0, \"
                \"XPU/CPU requires Triton >= 3.5.0. Please install triton: \`pip install triton\`\"
            )
        elif not kernels_installed:
            raise ValueError(\"MXFP4 quantization requires the \`kernels\` package: \`pip install kernels>=0.12.0\`\")'''

src = src.replace(old_error, new_error)

with open(path, 'w') as f:
    f.write(src)

print('Patch applied successfully.')
"
