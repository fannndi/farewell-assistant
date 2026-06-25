"""LLM status — 9Router manages all models. Just show status."""

from .helpers import get_gpu_info, write_step, write_ok, write_skip, write_info


def handle_llm_setup(action: str = "status", profile: str = ""):
    if action == "status":
        write_step("STATUS", "GPU")
        gpu = get_gpu_info("name,memory.total,temperature.gpu")
        if gpu and gpu.get("available"):
            write_info(f"  {gpu.get('name', '')} ({gpu.get('memory_total', 0)}MB, {gpu.get('temperature', '?')}C)")
        else: write_skip("No GPU detected")
        write_step("MODELS", "Managed by 9Router (port 20128)")
        write_ok("All models/subscriptions via 9Router")
    elif action == "list":
        write_info("Models: managed by 9Router (http://localhost:20128/v1/models)")
    else:
        write_info(f"LLM action '{action}' not supported — 9Router handles all models")
