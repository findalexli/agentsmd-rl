#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

BASIC_OLD="test/registered/8-gpu-models/test_deepseek_v32_basic.py"
BASIC_NEW="test/registered/8-gpu-models/test_dsa_models_basic.py"
MTP_OLD="test/registered/8-gpu-models/test_deepseek_v32_mtp.py"
MTP_NEW="test/registered/8-gpu-models/test_dsa_models_mtp.py"

# Idempotent: skip if already applied
if [ -f "$BASIC_NEW" ] && grep -q 'GLM5_MODEL_PATH = "zai-org/GLM-5-FP8"' "$BASIC_NEW" 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Step 1: Rename the basic test file
git mv "$BASIC_OLD" "$BASIC_NEW"

# Step 2: Update est_time from 360 to 720 and add GLM5_MODEL_PATH in basic tests
sed -i 's/register_cuda_ci(est_time=360/register_cuda_ci(est_time=720/' "$BASIC_NEW"
sed -i '/^DEEPSEEK_V32_MODEL_PATH = "deepseek-ai\/DeepSeek-V3.2"/a GLM5_MODEL_PATH = "zai-org/GLM-5-FP8"' "$BASIC_NEW"

# Step 3: Add GLM5 test classes to the basic test file
cat >> "$BASIC_NEW" << 'GLM5_BASIC'


class TestGLM5DP(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = GLM5_MODEL_PATH
        cls.base_url = DEFAULT_URL_FOR_TEST
        other_args = [
            "--trust-remote-code",
            "--tp",
            "8",
            "--dp",
            "8",
            "--enable-dp-attention",
            "--model-loader-extra-config",
            '{"enable_multithread_load": true, "num_threads": 64}',
        ]
        cls.process = popen_launch_server(
            cls.model,
            cls.base_url,
            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
            other_args=other_args,
        )

    @classmethod
    def tearDownClass(cls):
        kill_process_tree(cls.process.pid)

    def test_a_gsm8k(self):
        args = SimpleNamespace(
            base_url=self.base_url,
            model=self.model,
            eval_name="gsm8k",
            api="completion",
            max_tokens=512,
            num_examples=1400,
            num_threads=1400,
            num_shots=20,
        )
        metrics = run_eval(args)
        print(f"{metrics=}")

        if is_in_ci():
            write_github_step_summary(
                f"### test_gsm8k (glm-5)\n" f'{metrics["score"]=:.3f}\n'
            )
            self.assertGreater(metrics["score"], 0.935)

    def test_bs_1_speed(self):
        args = BenchArgs(port=int(self.base_url.split(":")[-1]), max_new_tokens=2048)
        acc_length, speed = send_one_prompt(args)

        print(f"{speed=:.2f}")

        if is_in_ci():
            write_github_step_summary(
                f"### test_bs_1_speed (glm-5)\n" f"{speed=:.2f} token/s\n"
            )
            self.assertGreater(speed, 40)


class TestGLM5TP(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = GLM5_MODEL_PATH
        cls.base_url = DEFAULT_URL_FOR_TEST
        other_args = [
            "--trust-remote-code",
            "--tp",
            "8",
            "--model-loader-extra-config",
            '{"enable_multithread_load": true, "num_threads": 64}',
        ]
        cls.process = popen_launch_server(
            cls.model,
            cls.base_url,
            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
            other_args=other_args,
        )

    @classmethod
    def tearDownClass(cls):
        kill_process_tree(cls.process.pid)

    def test_a_gsm8k(self):
        args = SimpleNamespace(
            base_url=self.base_url,
            model=self.model,
            eval_name="gsm8k",
            api="completion",
            max_tokens=512,
            num_examples=1400,
            num_threads=1400,
            num_shots=20,
        )
        metrics = run_eval(args)
        print(f"{metrics=}")

        if is_in_ci():
            write_github_step_summary(
                f"### test_gsm8k (glm-5)\n" f'{metrics["score"]=:.3f}\n'
            )
            self.assertGreater(metrics["score"], 0.935)

    def test_bs_1_speed(self):
        args = BenchArgs(port=int(self.base_url.split(":")[-1]), max_new_tokens=2048)
        acc_length, speed = send_one_prompt(args)

        print(f"{speed=:.2f}")

        if is_in_ci():
            write_github_step_summary(
                f"### test_bs_1_speed (glm-5)\n" f"{speed=:.2f} token/s\n"
            )
            self.assertGreater(speed, 60)
GLM5_BASIC

# Step 4: Rename the MTP test file
git mv "$MTP_OLD" "$MTP_NEW"

# Step 5: Add GLM5_MODEL_PATH constant in MTP tests
sed -i '/^FULL_DEEPSEEK_V32_MODEL_PATH = "deepseek-ai\/DeepSeek-V3.2"/a GLM5_MODEL_PATH = "zai-org/GLM-5-FP8"' "$MTP_NEW"

# Step 6: Rename TestDeepseekV32DPMTPV2 to TestDeepseekV32TPMTP and update config
sed -i 's/class TestDeepseekV32DPMTPV2/class TestDeepseekV32TPMTP/' "$MTP_NEW"
sed -i '/class TestDeepseekV32TPMTP/,/@classmethod/{ /--dp/,/--enable-dp-attention/d }' "$MTP_NEW"

# Step 7: Update speed thresholds in TestDeepseekV32TPMTP
sed -i 's/self.assertGreater(speed, 90)/self.assertGreater(speed, 180)/' "$MTP_NEW"

# Step 8: Transform TestDeepseekV32TPMTP to TestGLM5DPMTP (change model, add DP back, update env)
# This is complex - we'll use a Python script for the MTP transformations
python3 << 'PYTHON_SCRIPT'
import re

with open("test/registered/8-gpu-models/test_dsa_models_mtp.py", "r") as f:
    content = f.read()

# 1. Wrap TestDeepseekV32DPMTP setUpClass with envs.SGLANG_ENABLE_SPEC_V2.override(True)
old_dpmtp_setup = '''        cls.process = popen_launch_server(
            cls.model,
            cls.base_url,
            timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
            other_args=other_args,
        )'''
new_dpmtp_setup = '''        with envs.SGLANG_ENABLE_SPEC_V2.override(True):
            cls.process = popen_launch_server(
                cls.model,
                cls.base_url,
                timeout=DEFAULT_TIMEOUT_FOR_SERVER_LAUNCH,
                other_args=other_args,
            )'''
# Only replace first occurrence (for TestDeepseekV32DPMTP)
content = content.replace(old_dpmtp_setup, new_dpmtp_setup, 1)

# 2. Replace TestDeepseekV32TPMTP with TestGLM5DPMTP (change model, add DP, update mem-frac)
old_tpmtp = '''class TestDeepseekV32TPMTP(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = FULL_DEEPSEEK_V32_MODEL_PATH
        cls.base_url = DEFAULT_URL_FOR_TEST
        other_args = [
            "--trust-remote-code",
            "--tp",
            "8",
            "--speculative-algorithm",
            "EAGLE",
            "--speculative-num-steps",
            "3",
            "--speculative-eagle-topk",
            "1",
            "--speculative-num-draft-tokens",
            "4",
            "--mem-frac",
            "0.7",'''
new_tpmtp = '''class TestGLM5DPMTP(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = GLM5_MODEL_PATH
        cls.base_url = DEFAULT_URL_FOR_TEST
        other_args = [
            "--trust-remote-code",
            "--tp",
            "8",
            "--dp",
            "8",
            "--enable-dp-attention",
            "--speculative-algorithm",
            "EAGLE",
            "--speculative-num-steps",
            "3",
            "--speculative-eagle-topk",
            "1",
            "--speculative-num-draft-tokens",
            "4",
            "--mem-frac",
            "0.8",'''
content = content.replace(old_tpmtp, new_tpmtp)

# 3. Wrap TestGLM5DPMTP setUpClass with envs.SGLANG_ENABLE_SPEC_V2.override(True)
content = content.replace(old_dpmtp_setup, new_dpmtp_setup)

# 4. Update test_gsm8k message from deepseek-v32 to glm-5 in TestGLM5DPMTP
content = content.replace(
    'f"### test_gsm8k (deepseek-v32 mtp)\\n"',
    'f"### test_gsm8k (glm-5 mtp)\\n"'
)

# 5. Update test_bs_1_speed message and threshold
content = content.replace(
    'f"### test_bs_1_speed (deepseek-v32 mtp)\\n"',
    'f"### test_bs_1_speed (glm-5 mtp)\\n"'
)
content = content.replace('self.assertGreater(speed, 160)', 'self.assertGreater(speed, 70)')

# 6. Rename TestDeepseekV32TPMTPV2 to TestGLM5TPMTP and update model/mem-frac
old_tpv2 = '''class TestDeepseekV32TPMTPV2(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = FULL_DEEPSEEK_V32_MODEL_PATH'''
new_tpv2 = '''class TestGLM5TPMTP(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = GLM5_MODEL_PATH'''
content = content.replace(old_tpv2, new_tpv2)

# 7. Update mem-frac in TestGLM5TPMTP
content = content.replace(
    '''"--mem-frac",
            "0.7",''',
    '''"--mem-frac",
            "0.8",''',
    1  # Only first occurrence (the one in TP test after rename)
)

# 8. Update messages and thresholds in TestGLM5TPMTP
content = content.replace('self.assertGreater(speed, 180)', 'self.assertGreater(speed, 150)')

with open("test/registered/8-gpu-models/test_dsa_models_mtp.py", "w") as f:
    f.write(content)

print("MTP file transformations applied.")
PYTHON_SCRIPT

echo "Patch applied successfully."
